"""
Model loader + deterministic heuristic fallback.

Attempts to load a pre-trained .pkl model (Random Forest / XGBoost).
If the model file doesn't exist, falls back to an 8-measure
deterministic heuristic engine for maximum detection accuracy.

Detection Measures:
  1. Consumption Drop     — zero kWh during peak daylight hours
  2. Voltage Anomaly      — readings outside safe 190–250V band
  3. Current Anomaly      — near-zero current with normal voltage (bypass)
  4. Power Factor Anomaly — unusually low PF suggesting load manipulation
  5. Frequency Deviation  — grid frequency outside 49–51 Hz
  6. Tamper Detection     — hardware tamper flags from the meter
  7. Pattern Irregularity — statistical deviation from expected patterns
  8. Flat-line Detection  — suspiciously constant readings (spoofed meter)
"""

import os
import math
import joblib
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional

from .schemas import (
    MeterReading, Features, AnomalyBreakdown, PredictResponse
)

# ─── Try loading a trained model ─────────────────────────
POSSIBLE_PATHS = [
    os.getenv("MODEL_PATH"),
    os.path.join(os.path.dirname(__file__), "..", "models", "model.pkl"),
    os.path.join(os.path.dirname(__file__), "models", "model.pkl"),
    "models/model.pkl",
    "/app/models/model.pkl",
]

_model = None
for p in POSSIBLE_PATHS:
    if p and os.path.exists(p):
        try:
            _model = joblib.load(p)
            print(f"[OK] Loaded ML model from {p}")
            break
        except Exception as e:
            print(f"[WARN] Failed loading model from {p}: {e}")

if _model is None:
    print("[INFO] No ML model found — using 8-measure heuristic engine")


def predict_with_model(features: Features, readings: List[MeterReading]) -> Optional[PredictResponse]:
    """
    Run prediction using the trained ML model if available.
    Returns None if no model is loaded.
    """
    if _model is None:
        return None

    try:
        n = len(readings)
        if n == 0:
            return None

        # ── Core features (14) ───────────────────────────
        core = [
            features.consumption_stats.mean,
            features.consumption_stats.std,
            features.consumption_stats.min,
            features.consumption_stats.max,
            features.voltage_stats.mean,
            features.voltage_stats.std,
            features.current_stats.mean,
            features.current_stats.std,
            features.power_factor_stats.mean,
            features.frequency_stats.mean,
            features.tamper_ratio,
            features.baseline_consumption,
            1.0 if features.consumer_type == "commercial" else 0.0,
            float(features.reading_count),
        ]

        # ── Engineered features (10) — must match train_model.py ──
        # 1. zero_peak_ratio
        peak = [r for r in readings if 8 <= _get_hour(r.timestamp) <= 20]
        zero_peak = sum(1 for r in peak if r.consumption_kwh == 0) if peak else 0
        zero_peak_ratio = zero_peak / len(peak) if peak else 0.0

        # 2. bypass_ratio (low current + normal voltage)
        bypass = sum(1 for r in readings if r.current < 0.1 and r.voltage > 200 and r.consumption_kwh > 0)
        bypass_ratio = bypass / n

        # 3. coefficient of variation
        cv = features.consumption_stats.std / features.consumption_stats.mean if features.consumption_stats.mean > 0 else 0.0

        # 4. night/day ratio
        night = [r.consumption_kwh for r in readings if _get_hour(r.timestamp) < 6]
        day = [r.consumption_kwh for r in readings if 9 <= _get_hour(r.timestamp) <= 17]
        night_avg = sum(night) / len(night) if night else 0.0
        day_avg = sum(day) / len(day) if day else 0.001
        night_day_ratio = night_avg / day_avg if day_avg > 0 else 0.0

        # 5. extreme voltage ratio
        extreme_v = sum(1 for r in readings if r.voltage < 170 or r.voltage > 270)
        extreme_v_ratio = extreme_v / n

        # 6. very low PF ratio
        very_low_pf = sum(1 for r in readings if r.power_factor < 0.3)
        very_low_pf_ratio = very_low_pf / n

        # 7. flat-line score
        unique_vals = len(set(round(r.consumption_kwh, 2) for r in readings))
        flat_score = 1.0 - (unique_vals / n) if n > 10 else 0.0

        # 8. baseline ratio
        baseline_ratio = features.consumption_stats.mean / features.baseline_consumption if features.baseline_consumption > 0 else 1.0

        # 9. frequency out-of-range ratio
        freq_out = sum(1 for r in readings if r.frequency < 49.0 or r.frequency > 51.0)
        freq_out_ratio = freq_out / n

        # 10. consecutive tamper normalization
        max_consec = _max_consecutive_true([r.tamper_flag for r in readings])
        consec_tamper_norm = min(1.0, max_consec / 10.0)

        engineered = [
            zero_peak_ratio, bypass_ratio, cv, night_day_ratio,
            extreme_v_ratio, very_low_pf_ratio, flat_score,
            baseline_ratio, freq_out_ratio, consec_tamper_norm,
        ]

        feature_vector = np.array([core + engineered])

        probability = float(_model.predict_proba(feature_vector)[0][1])
        anomaly = probability >= 0.30

        # Also compute heuristic breakdown for explainability
        heuristic_result = predict_heuristic(features, readings)

        return PredictResponse(
            theft_probability=round(probability, 4),
            anomaly_flag=anomaly,
            anomaly_breakdown=heuristic_result.anomaly_breakdown,
            source="model",
            confidence=round(abs(probability - 0.5) * 2, 4),
            risk_level=_classify_risk(probability),
        )
    except Exception as e:
        print(f"Model prediction failed: {e} — falling back to heuristic")
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
