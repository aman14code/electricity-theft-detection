"""
Model loader + ensemble + deterministic heuristic fallback.

Attempts to load a pre-trained ensemble package (RF, XGBoost, Isolation Forest, etc.)
If the model file doesn't exist, falls back to an 8-measure
deterministic heuristic engine for maximum detection accuracy.
"""

import os
import joblib
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional

from .schemas import (
    MeterReading, Features, AnomalyBreakdown, PredictResponse,
    ModelScore, ShapExplanation
)

import sys

# ─── MOCK WRAPPERS TO FIX COLLAB UNPICKLING ──────────────
class DNNWrapper:
    def __init__(self, keras_model, input_dim):
        self.keras_model = keras_model
        self.input_dim = input_dim
        self.classes_ = np.array([0, 1])
    def predict_proba(self, X):
        if not hasattr(self, 'keras_model') or self.keras_model is None:
            return np.zeros((len(X), 2))
        probs = self.keras_model.predict(np.array(X), verbose=0).flatten()
        return np.column_stack([1 - probs, probs])

class IsolationForestWrapper:
    def __init__(self, iso_model):
        self.iso_model = iso_model
        self.classes_ = np.array([0, 1])
    def predict_proba(self, X):
        scores = self.iso_model.decision_function(X)
        probs = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        return np.column_stack([1 - probs, probs])

class LSTMWrapper:
    def __init__(self, keras_model, seq_len, feat_per_step, pad_size):
        self.keras_model = keras_model
        self.seq_len = seq_len
        self.feat_per_step = feat_per_step
        self.pad_size = pad_size
        self.classes_ = np.array([0, 1])
    def predict_proba(self, X):
        return np.zeros((len(X), 2)) # Fast fallback if needed

# Map to __main__ so joblib can find them from Colab
setattr(sys.modules['__main__'], 'DNNWrapper', DNNWrapper)
setattr(sys.modules['__main__'], 'IsolationForestWrapper', IsolationForestWrapper)
setattr(sys.modules['__main__'], 'LSTMWrapper', LSTMWrapper)


# ─── Try loading a trained model ─────────────────────────
POSSIBLE_PATHS = [
    os.getenv("MODEL_PATH"),
    os.path.join(os.path.dirname(__file__), "..", "models", "ensemble_model.pkl"),
    os.path.join(os.path.dirname(__file__), "models", "ensemble_model.pkl"),
    "models/ensemble_model.pkl",
    "/app/models/ensemble_model.pkl",
]

_ensemble = None
for p in POSSIBLE_PATHS:
    if p and os.path.exists(p):
        try:
            _ensemble = joblib.load(p)
            print(f"[OK] Loaded ML ensemble from {p}")
            break
        except Exception as e:
            print(f"[WARN] Failed loading ensemble from {p}: {e}")

if _ensemble is None:
    print("[INFO] No ML ensemble found — using 8-measure heuristic engine")


def _extract_features_for_ensemble(features: Features, readings: List[MeterReading], feature_names: List[str]) -> np.ndarray:
    """Map incoming request features and readings to the format expected by the ensemble."""
    n = len(readings)
    f_dict = {}

    # Basic stats
    kwh = [r.consumption_kwh for r in readings] if n > 0 else [0.0]
    f_dict["stat_mean"] = np.mean(kwh)
    f_dict["stat_std"] = np.std(kwh)
    f_dict["stat_cv"] = f_dict["stat_std"] / f_dict["stat_mean"] if f_dict["stat_mean"] > 0 else 0
    f_dict["stat_min"] = np.min(kwh)
    f_dict["stat_max"] = np.max(kwh)
    f_dict["stat_median"] = np.median(kwh)
    f_dict["stat_iqr"] = np.percentile(kwh, 75) - np.percentile(kwh, 25)
    f_dict["stat_range"] = np.max(kwh) - np.min(kwh)

    # Anomaly
    zero_days = sum(1 for x in kwh if x == 0)
    f_dict["anom_zero_day_count"] = zero_days
    f_dict["anom_zero_day_ratio"] = zero_days / max(1, n)
    f_dict["anom_below_baseline_ratio"] = sum(1 for x in kwh if x < features.baseline_consumption * 0.3) / max(1, n)

    # Metadata
    f_dict["meta_is_residential"] = 1.0 if features.consumer_type == "residential" else 0.0
    f_dict["meta_is_commercial"] = 1.0 if features.consumer_type == "commercial" else 0.0
    f_dict["meta_is_industrial"] = 1.0 if features.consumer_type == "industrial" else 0.0
    f_dict["meta_baseline_kwh"] = features.baseline_consumption
    
    # Fill feature vector
    feat_vector = []
    for name in feature_names:
        feat_vector.append(f_dict.get(name, 0.0))
        
    return np.array([feat_vector])


def predict_with_model(features: Features, readings: List[MeterReading]) -> Optional[PredictResponse]:
    """Run prediction using the trained ML ensemble if available."""
    if _ensemble is None:
        return None

    try:
        if len(readings) == 0:
            return None

        feature_names = _ensemble.get("feature_names", [])
        scaler = _ensemble.get("scaler")
        rf_model = _ensemble.get("rf_model")
        xgb_model = _ensemble.get("xgb_model")
        iso_model = _ensemble.get("iso_model")
        meta_model = _ensemble.get("meta_model")
        optimal_threshold = _ensemble.get("optimal_threshold", 0.5)

        X_raw = _extract_features_for_ensemble(features, readings, feature_names)
        X_scaled = scaler.transform(X_raw) if scaler else X_raw

        model_scores = []
        probs = []

        # Predict RF
        if rf_model:
            p_rf = float(rf_model.predict_proba(X_scaled)[0, 1])
            probs.append(p_rf)
            model_scores.append(ModelScore(model_name="Random Forest", probability=round(p_rf, 4), prediction="theft" if p_rf >= optimal_threshold else "normal"))

        # Predict XGBoost
        if xgb_model:
            # Need a wrapper or just use predict_proba
            p_xgb = float(xgb_model.predict_proba(X_scaled)[0, 1])
            probs.append(p_xgb)
            model_scores.append(ModelScore(model_name="XGBoost", probability=round(p_xgb, 4), prediction="theft" if p_xgb >= optimal_threshold else "normal"))

        # Predict Isolation Forest
        if iso_model:
            try:
                p_iso = float(iso_model.predict_proba(X_scaled)[0, 1])
                probs.append(p_iso)
                model_scores.append(ModelScore(model_name="Isolation Forest", probability=round(p_iso, 4), prediction="theft" if p_iso >= optimal_threshold else "normal"))
            except:
                pass

        if not probs:
            return None

        # Soft voting
        ensemble_prob = float(np.mean(probs))

        # Stacking (if meta_model exists)
        if meta_model and len(probs) >= 2:
            try:
                stack_features = np.array(probs).reshape(1, -1)
                ensemble_prob = float(meta_model.predict_proba(stack_features)[0, 1])
            except:
                pass

        anomaly = ensemble_prob >= optimal_threshold

        # Generate SHAP Explanations
        shap_explanations = []
        global_shap = _ensemble.get("shap_importance", {})
        if global_shap:
            # Pick top 5 features for the explanation
            top_features = list(global_shap.keys())[:5]
            for f in top_features:
                if f in feature_names:
                    idx = feature_names.index(f)
                    f_val = float(X_raw[0, idx])
                    shap_explanations.append(
                        ShapExplanation(
                            feature_name=f,
                            shap_value=global_shap[f],
                            feature_value=f_val
                        )
                    )

        # Get heuristic breakdown for explainability
        heuristic_result = predict_heuristic(features, readings)

        return PredictResponse(
            theft_probability=round(ensemble_prob, 4),
            anomaly_flag=anomaly,
            anomaly_breakdown=heuristic_result.anomaly_breakdown,
            source="ensemble",
            confidence=round(abs(ensemble_prob - optimal_threshold) * 2, 4),
            risk_level=_classify_risk(ensemble_prob),
            model_scores=model_scores,
            ensemble_method="stacking" if meta_model else "soft_voting",
            shap_explanations=shap_explanations,
            top_risk_factors=[s.feature_name for s in shap_explanations[:3]]
        )
    except Exception as e:
        print(f"Ensemble prediction failed: {e} — falling back to heuristic")
        return None



def predict_heuristic(features: Features, readings: List[MeterReading]) -> PredictResponse:
    """
    8-measure deterministic heuristic engine.
    Each measure produces a score between 0 and 1.
    Final probability is a weighted combination.
    """
    n = len(readings)
    if n == 0:
        return PredictResponse(
            theft_probability=0.0,
            anomaly_flag=False,
            anomaly_breakdown=AnomalyBreakdown(),
            source="heuristic",
            confidence=1.0,
            risk_level="low",
        )

    scores = {}

    # ── 1. Consumption Drop (weight: 0.25) ───────────────
    peak_readings = [
        r for r in readings
        if 8 <= _get_hour(r.timestamp) <= 20
    ]
    if peak_readings:
        zero_in_peak = sum(1 for r in peak_readings if r.consumption_kwh == 0)
        scores["consumption_drop"] = min(1.0, (zero_in_peak / len(peak_readings)) * 5)
    else:
        scores["consumption_drop"] = 0.0

    # Check for sudden drops relative to baseline
    if features.baseline_consumption > 0:
        avg_ratio = features.consumption_stats.mean / features.baseline_consumption
        if avg_ratio < 0.3:
            scores["consumption_drop"] = max(scores["consumption_drop"], 0.7)

    # ── 2. Voltage Anomaly (weight: 0.10) ────────────────
    voltage_outliers = sum(1 for r in readings if r.voltage < 190 or r.voltage > 250)
    scores["voltage_anomaly"] = min(1.0, (voltage_outliers / n) * 3)

    # Extreme voltage = stronger signal
    extreme_voltage = sum(1 for r in readings if r.voltage < 170 or r.voltage > 270)
    if extreme_voltage > 0:
        scores["voltage_anomaly"] = max(scores["voltage_anomaly"], min(1.0, (extreme_voltage / n) * 5))

    # ── 3. Current Anomaly (weight: 0.15) ────────────────
    # Bypass detection: low current + normal voltage + nonzero consumption
    suspicious_current = sum(
        1 for r in readings
        if r.current < 0.1 and r.voltage > 200 and r.consumption_kwh > 0
    )
    scores["current_anomaly"] = min(1.0, (suspicious_current / n) * 4)

    # Also flag: zero current but nonzero consumption (impossible without theft)
    impossible = sum(
        1 for r in readings
        if r.current == 0 and r.consumption_kwh > 0.5
    )
    if impossible > 0:
        scores["current_anomaly"] = max(scores["current_anomaly"], min(1.0, (impossible / n) * 8))

    # ── 4. Power Factor Anomaly (weight: 0.10) ──────────
    low_pf = sum(1 for r in readings if r.power_factor < 0.5)
    scores["power_factor_anomaly"] = min(1.0, (low_pf / n) * 3)

    # Very low PF with low consumption = stronger signal
    very_low_pf_and_consumption = sum(
        1 for r in readings
        if r.power_factor < 0.3 and r.consumption_kwh < features.baseline_consumption * 0.2
    )
    if very_low_pf_and_consumption > 0:
        scores["power_factor_anomaly"] = max(
            scores["power_factor_anomaly"],
            min(1.0, (very_low_pf_and_consumption / n) * 5)
        )

    # ── 5. Frequency Deviation (weight: 0.05) ───────────
    freq_outliers = sum(1 for r in readings if r.frequency < 49.0 or r.frequency > 51.0)
    scores["frequency_deviation"] = min(1.0, (freq_outliers / n) * 4)

    # ── 6. Tamper Detection (weight: 0.20) ───────────────
    scores["tamper_detected"] = min(1.0, features.tamper_ratio * 10)

    # Consecutive tamper flags = even more suspicious
    max_consecutive_tamper = _max_consecutive_true([r.tamper_flag for r in readings])
    if max_consecutive_tamper >= 5:
        scores["tamper_detected"] = max(scores["tamper_detected"], 0.9)

    # ── 7. Pattern Irregularity (weight: 0.10) ──────────
    if features.consumption_stats.mean > 0:
        cv = features.consumption_stats.std / features.consumption_stats.mean
        scores["pattern_irregularity"] = min(1.0, max(0.0, (cv - 0.5) / 1.5))
    else:
        scores["pattern_irregularity"] = 0.8  # Zero mean is suspicious

    # Check for day/night inversion (high at night, zero during day)
    night_avg = _avg_consumption_for_hours(readings, range(0, 6))
    day_avg = _avg_consumption_for_hours(readings, range(9, 18))
    if day_avg > 0 and night_avg > day_avg * 2:
        scores["pattern_irregularity"] = max(scores["pattern_irregularity"], 0.6)
    elif day_avg == 0 and night_avg > 0:
        scores["pattern_irregularity"] = max(scores["pattern_irregularity"], 0.85)

    # ── 8. Flat-line Detection (weight: 0.05) ───────────
    unique_values = len(set(r.consumption_kwh for r in readings))
    if n > 10:
        unique_ratio = unique_values / n
        scores["flat_line_detection"] = min(1.0, max(0.0, (1 - unique_ratio) * 2 - 0.5))
    else:
        scores["flat_line_detection"] = 0.0

    # Check for perfectly repeating sequences
    if n >= 24:
        last_24 = [r.consumption_kwh for r in readings[-24:]]
        if len(set(last_24)) <= 2:
            scores["flat_line_detection"] = max(scores["flat_line_detection"], 0.9)

    # ── Weighted combination ─────────────────────────────
    weights = {
        "consumption_drop": 0.25,
        "voltage_anomaly": 0.10,
        "current_anomaly": 0.15,
        "power_factor_anomaly": 0.10,
        "frequency_deviation": 0.05,
        "tamper_detected": 0.20,
        "pattern_irregularity": 0.10,
        "flat_line_detection": 0.05,
    }

    weighted_sum = sum(scores[k] * weights[k] for k in weights)
    total_weight = sum(weights.values())
    theft_probability = round(weighted_sum / total_weight, 4)

    # Boost: if 3+ measures score above 0.5, increase probability
    high_measures = sum(1 for v in scores.values() if v > 0.5)
    if high_measures >= 3:
        theft_probability = min(1.0, theft_probability * 1.3)

    # Boost: if any single measure is above 0.9, floor at 40%
    if any(v >= 0.9 for v in scores.values()):
        theft_probability = max(0.40, theft_probability)

    theft_probability = round(theft_probability, 4)
    anomaly_flag = theft_probability >= 0.30

    # Confidence = how many measures agree
    agreeing = sum(1 for v in scores.values() if (v > 0.5) == anomaly_flag)
    confidence = round(agreeing / len(scores), 4)

    return PredictResponse(
        theft_probability=theft_probability,
        anomaly_flag=anomaly_flag,
        anomaly_breakdown=AnomalyBreakdown(**scores),
        source="heuristic",
        confidence=confidence,
        risk_level=_classify_risk(theft_probability),
    )


# ─── Helper functions ────────────────────────────────────

def _get_hour(timestamp_str: str) -> int:
    """Extract hour from ISO timestamp string."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.hour
    except Exception:
        return 12  # Default to midday

def _max_consecutive_true(flags: List[bool]) -> int:
    """Find the longest run of True values."""
    max_run = 0
    current = 0
    for f in flags:
        if f:
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run

def _avg_consumption_for_hours(readings: List[MeterReading], hours: range) -> float:
    """Average consumption during specific hours."""
    filtered = [r.consumption_kwh for r in readings if _get_hour(r.timestamp) in hours]
    return sum(filtered) / len(filtered) if filtered else 0.0

def _classify_risk(probability: float) -> str:
    """Classify theft probability into risk levels."""
    if probability >= 0.75:
        return "critical"
    elif probability >= 0.50:
        return "high"
    elif probability >= 0.30:
        return "medium"
    else:
        return "low"
