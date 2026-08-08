"""
ML Model Training Script — Electricity Theft Detection
========================================================

Generates a large synthetic dataset of realistic smart meter readings,
trains a Random Forest classifier with hyperparameter tuning, and saves
the model to ml-service/models/model.pkl.

Features extracted match exactly what the backend sends via the /predict API:
  - consumption_stats (mean, std, min, max)
  - voltage_stats (mean, std, min, max)
  - current_stats (mean, std, min, max)
  - power_factor_stats (mean, std, min, max)
  - frequency_stats (mean, std, min, max)
  - tamper_ratio
  - baseline_consumption
  - consumer_type (encoded)
  - reading_count

Plus engineered features for higher accuracy:
  - zero_peak_ratio (consumption = 0 during peak hours 8-20)
  - low_current_normal_voltage_ratio (bypass detection)
  - coefficient_of_variation (consumption)
  - night_day_ratio (inverted pattern detection)
  - extreme_voltage_ratio (voltage < 170 or > 270)
  - very_low_pf_ratio (power factor < 0.3)
  - flat_line_score (unique values ratio)

Usage:
  python ml-service/train_model.py
"""

import os
import sys
import random
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import joblib

# Reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ─── Output path ─────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

# ─── Realistic daily patterns ────────────────────────────
RESIDENTIAL_PATTERN = [
    0.3, 0.2, 0.15, 0.15, 0.2, 0.3, 0.6, 0.9,
    1.0, 0.8, 0.6, 0.5, 0.5, 0.4, 0.4, 0.5,
    0.7, 0.9, 1.2, 1.3, 1.2, 1.0, 0.7, 0.4,
]
COMMERCIAL_PATTERN = [
    0.1, 0.1, 0.1, 0.1, 0.1, 0.15, 0.3, 0.7,
    1.0, 1.2, 1.3, 1.3, 1.1, 1.2, 1.3, 1.2,
    1.1, 1.0, 0.6, 0.3, 0.15, 0.1, 0.1, 0.1,
]


def rand_range(base, var):
    return base + (random.random() * 2 - 1) * var


# ─── Generate a meter's worth of readings ────────────────
def generate_readings(baseline, is_residential, days, anomaly_type=None):
    """Generate realistic hourly readings for one meter."""
    pattern = RESIDENTIAL_PATTERN if is_residential else COMMERCIAL_PATTERN
    readings = []
    now = datetime.now()

    for day in range(days, 0, -1):
        for hour in range(24):
            ts = now - timedelta(days=day) + timedelta(hours=hour)
            mult = pattern[hour]

            if anomaly_type is None:
                # Normal reading
                r = {
                    "timestamp": ts,
                    "hour": hour,
                    "consumption_kwh": max(0, rand_range(baseline * mult, baseline * 0.15)),
                    "voltage": rand_range(230, 8),
                    "current": max(0.1, rand_range(baseline * mult * 4.3, 1.5)),
                    "power_factor": min(1.0, max(0.7, rand_range(0.92, 0.06))),
                    "frequency": rand_range(50, 0.2),
                    "tamper_flag": False,
                }

            elif anomaly_type == "zero_peak":
                # Theft: consumption drops to zero during peak hours
                if 8 <= hour <= 20:
                    r = {
                        "timestamp": ts, "hour": hour,
                        "consumption_kwh": 0,
                        "voltage": rand_range(230, 5),
                        "current": 0.01,
                        "power_factor": rand_range(0.15, 0.05),
                        "frequency": rand_range(50, 0.3),
                        "tamper_flag": False,
                    }
                else:
                    r = {
                        "timestamp": ts, "hour": hour,
                        "consumption_kwh": max(0, rand_range(baseline * mult, baseline * 0.1)),
                        "voltage": rand_range(230, 5),
                        "current": max(0.1, rand_range(baseline * mult * 4.3, 1.0)),
                        "power_factor": min(1.0, max(0.7, rand_range(0.90, 0.05))),
                        "frequency": rand_range(50, 0.2),
                        "tamper_flag": False,
                    }

            elif anomaly_type == "voltage_tamper":
                # Theft: abnormal voltage + frequent tamper flags
                r = {
                    "timestamp": ts, "hour": hour,
                    "consumption_kwh": max(0, rand_range(baseline * 0.2, 0.5)),
                    "voltage": rand_range(170, 15),
                    "current": rand_range(0.05, 0.02),
                    "power_factor": rand_range(0.3, 0.1),
                    "frequency": rand_range(49.0, 0.8),
                    "tamper_flag": random.random() > 0.4,
                }

            elif anomaly_type == "current_bypass":
                # Theft: near-zero current but normal voltage and some consumption
                r = {
                    "timestamp": ts, "hour": hour,
                    "consumption_kwh": max(0, rand_range(baseline * mult * 0.3, 0.5)),
                    "voltage": rand_range(232, 5),
                    "current": rand_range(0.03, 0.01),
                    "power_factor": rand_range(0.25, 0.1),
                    "frequency": rand_range(50, 0.2),
                    "tamper_flag": random.random() > 0.7,
                }

            elif anomaly_type == "flatline":
                # Theft: perfectly constant readings (spoofed meter)
                r = {
                    "timestamp": ts, "hour": hour,
                    "consumption_kwh": 1.0,
                    "voltage": 230.0,
                    "current": 4.35,
                    "power_factor": 0.95,
                    "frequency": 50.0,
                    "tamper_flag": False,
                }

            elif anomaly_type == "night_inversion":
                # Theft: high usage at night, zero during day (reversed pattern)
                if 9 <= hour <= 17:
                    r = {
                        "timestamp": ts, "hour": hour,
                        "consumption_kwh": 0,
                        "voltage": rand_range(230, 5),
                        "current": 0.02,
                        "power_factor": rand_range(0.2, 0.1),
                        "frequency": rand_range(50, 0.2),
                        "tamper_flag": False,
                    }
                else:
                    r = {
                        "timestamp": ts, "hour": hour,
                        "consumption_kwh": max(0, rand_range(baseline * 2.5, baseline * 0.3)),
                        "voltage": rand_range(225, 10),
                        "current": max(0.1, rand_range(baseline * 3 * 4.3, 2.0)),
                        "power_factor": min(1.0, max(0.6, rand_range(0.85, 0.08))),
                        "frequency": rand_range(50, 0.3),
                        "tamper_flag": random.random() > 0.85,
                    }

            elif anomaly_type == "gradual_drop":
                # Theft: consumption gradually decreases day by day
                decay = max(0.05, 1.0 - (days - day) * 0.08)
                r = {
                    "timestamp": ts, "hour": hour,
                    "consumption_kwh": max(0, rand_range(baseline * mult * decay, baseline * 0.1)),
                    "voltage": rand_range(228, 6),
                    "current": max(0.05, rand_range(baseline * mult * decay * 4.3, 1.0)),
                    "power_factor": min(1.0, max(0.5, rand_range(0.85 * decay + 0.1, 0.05))),
                    "frequency": rand_range(50, 0.25),
                    "tamper_flag": random.random() > 0.9 and decay < 0.5,
                }

            elif anomaly_type == "partial_theft":
                # Theft: consumption reduced to ~30% of expected (partial meter bypass)
                r = {
                    "timestamp": ts, "hour": hour,
                    "consumption_kwh": max(0, rand_range(baseline * mult * 0.3, baseline * 0.08)),
                    "voltage": rand_range(230, 7),
                    "current": max(0.05, rand_range(baseline * mult * 0.3 * 4.3, 1.0)),
                    "power_factor": min(1.0, max(0.5, rand_range(0.80, 0.08))),
                    "frequency": rand_range(50, 0.2),
                    "tamper_flag": random.random() > 0.85,
                }

            else:
                raise ValueError(f"Unknown anomaly type: {anomaly_type}")

            readings.append(r)

    return readings


# ─── Extract features from readings ─────────────────────
def extract_features(readings, baseline, is_residential):
    """Extract all features matching the backend's payload to /predict."""
    consumptions = [r["consumption_kwh"] for r in readings]
    voltages = [r["voltage"] for r in readings]
    currents = [r["current"] for r in readings]
    pfs = [r["power_factor"] for r in readings]
    freqs = [r["frequency"] for r in readings]
    tamper_count = sum(1 for r in readings if r["tamper_flag"])
    n = len(readings)

    def stats(arr):
        a = np.array(arr)
        return {
            "mean": float(np.mean(a)),
            "std": float(np.std(a)),
            "min": float(np.min(a)),
            "max": float(np.max(a)),
        }

    cs = stats(consumptions)
    vs = stats(voltages)
    crs = stats(currents)
    pfs_s = stats(pfs)
    fs = stats(freqs)

    tamper_ratio = tamper_count / n if n > 0 else 0.0

    # ── Core features (14, matching the model.py feature_vector) ─
    core = [
        cs["mean"], cs["std"], cs["min"], cs["max"],
        vs["mean"], vs["std"],
        crs["mean"], crs["std"],
        pfs_s["mean"],
        fs["mean"],
        tamper_ratio,
        baseline,
        1.0 if not is_residential else 0.0,
        float(n),
    ]

    # ── Engineered features for higher accuracy ──────────
    # Zero-consumption during peak hours (8-20)
    peak_readings = [r for r in readings if 8 <= r["hour"] <= 20]
    zero_peak = sum(1 for r in peak_readings if r["consumption_kwh"] == 0) if peak_readings else 0
    zero_peak_ratio = zero_peak / len(peak_readings) if peak_readings else 0.0

    # Low current + normal voltage (bypass detection)
    bypass = sum(
        1 for r in readings
        if r["current"] < 0.1 and r["voltage"] > 200 and r["consumption_kwh"] > 0
    )
    bypass_ratio = bypass / n if n > 0 else 0.0

    # Coefficient of variation (consumption)
    cv = cs["std"] / cs["mean"] if cs["mean"] > 0 else 0.0

    # Night vs day ratio
    night_readings = [r["consumption_kwh"] for r in readings if r["hour"] < 6]
    day_readings = [r["consumption_kwh"] for r in readings if 9 <= r["hour"] <= 17]
    night_avg = np.mean(night_readings) if night_readings else 0.0
    day_avg = np.mean(day_readings) if day_readings else 0.001
    night_day_ratio = float(night_avg / day_avg) if day_avg > 0 else 0.0

    # Extreme voltage ratio
    extreme_v = sum(1 for r in readings if r["voltage"] < 170 or r["voltage"] > 270)
    extreme_v_ratio = extreme_v / n if n > 0 else 0.0

    # Very low PF ratio
    very_low_pf = sum(1 for r in readings if r["power_factor"] < 0.3)
    very_low_pf_ratio = very_low_pf / n if n > 0 else 0.0

    # Flat-line score
    unique_vals = len(set(round(c, 2) for c in consumptions))
    flat_score = 1.0 - (unique_vals / n) if n > 10 else 0.0

    # Consumption vs baseline ratio
    baseline_ratio = cs["mean"] / baseline if baseline > 0 else 1.0

    # Frequency deviation ratio
    freq_out = sum(1 for r in readings if r["frequency"] < 49.0 or r["frequency"] > 51.0)
    freq_out_ratio = freq_out / n if n > 0 else 0.0

    # Max consecutive tamper
    max_consec = 0
    cur = 0
    for r in readings:
        if r["tamper_flag"]:
            cur += 1
            max_consec = max(max_consec, cur)
        else:
            cur = 0
    consec_tamper_norm = min(1.0, max_consec / 10.0)

    engineered = [
        zero_peak_ratio,
        bypass_ratio,
        cv,
        night_day_ratio,
        extreme_v_ratio,
        very_low_pf_ratio,
        flat_score,
        baseline_ratio,
        freq_out_ratio,
        consec_tamper_norm,
    ]

    return core + engineered


# ─── Build dataset ───────────────────────────────────────
def build_dataset(n_normal=3000, n_anomaly_each=600):
    """Generate synthetic labeled data."""
    print(f"[DATA] Generating dataset: {n_normal} normal + {n_anomaly_each} x 7 anomaly types...")

    baselines_res = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
    baselines_com = [6.0, 8.0, 10.0, 12.0, 15.0, 20.0]
    anomaly_types = [
        "zero_peak", "voltage_tamper", "current_bypass",
        "flatline", "night_inversion", "gradual_drop", "partial_theft",
    ]

    X, y = [], []

    # Normal samples
    for i in range(n_normal):
        is_res = random.random() < 0.6
        bl = random.choice(baselines_res if is_res else baselines_com)
        days = random.choice([10, 14, 20, 25, 30])
        readings = generate_readings(bl, is_res, days, anomaly_type=None)
        feats = extract_features(readings, bl, is_res)
        X.append(feats)
        y.append(0)
        if (i + 1) % 500 == 0:
            print(f"   Normal: {i+1}/{n_normal}")

    # Anomalous samples
    for atype in anomaly_types:
        for i in range(n_anomaly_each):
            is_res = random.random() < 0.5
            bl = random.choice(baselines_res if is_res else baselines_com)
            days = random.choice([7, 10, 14, 20, 30])
            readings = generate_readings(bl, is_res, days, anomaly_type=atype)
            feats = extract_features(readings, bl, is_res)
            X.append(feats)
            y.append(1)
        print(f"   Anomaly [{atype}]: {n_anomaly_each} samples generated")

    X = np.array(X)
    y = np.array(y)
    print(f"[OK] Dataset: {X.shape[0]} samples x {X.shape[1]} features")
    print(f"   Normal: {np.sum(y == 0)}, Anomalous: {np.sum(y == 1)}")
    return X, y


# ─── Feature names ───────────────────────────────────────
FEATURE_NAMES = [
    "consumption_mean", "consumption_std", "consumption_min", "consumption_max",
    "voltage_mean", "voltage_std",
    "current_mean", "current_std",
    "power_factor_mean",
    "frequency_mean",
    "tamper_ratio",
    "baseline_consumption",
    "is_commercial",
    "reading_count",
    # Engineered
    "zero_peak_ratio",
    "bypass_ratio",
    "coeff_of_variation",
    "night_day_ratio",
    "extreme_voltage_ratio",
    "very_low_pf_ratio",
    "flat_line_score",
    "baseline_ratio",
    "freq_out_ratio",
    "consec_tamper_norm",
]


# ─── Train ───────────────────────────────────────────────
def train():
    X, y = build_dataset(n_normal=3000, n_anomaly_each=600)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y,
    )

    print("\n[TRAIN] Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=25,
        min_samples_split=3,
        min_samples_leaf=1,
        max_features="sqrt",
        bootstrap=True,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # ── Evaluate ─────────────────────────────────────────
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("\n" + "=" * 50)
    print(f"[RESULTS]")
    print("=" * 50)
    print(f"   Accuracy:   {acc * 100:.2f}%")
    print(f"   Precision:  {prec * 100:.2f}%")
    print(f"   Recall:     {rec * 100:.2f}%")
    print(f"   F1 Score:   {f1 * 100:.2f}%")
    print()
    print("   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Theft"]))
    print("   Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   [[{cm[0][0]:>5d}  {cm[0][1]:>5d}]")
    print(f"    [{cm[1][0]:>5d}  {cm[1][1]:>5d}]]")
    print(f"   (TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]})")

    # Cross-validation
    print("\n[CV] 5-Fold Cross-Validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy", n_jobs=-1)
    print(f"   CV Accuracy: {cv_scores.mean() * 100:.2f}% +/- {cv_scores.std() * 100:.2f}%")

    # Feature importance
    print("\n[TOP] Top 10 Feature Importances:")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    for rank, idx in enumerate(indices[:10], 1):
        name = FEATURE_NAMES[idx] if idx < len(FEATURE_NAMES) else f"feature_{idx}"
        print(f"   {rank:>2}. {name:<25s} {importances[idx]:.4f}")

    # ── Save model ───────────────────────────────────────
    joblib.dump(model, MODEL_PATH)
    print(f"\n[SAVE] Model saved to: {MODEL_PATH}")
    print(f"   Model size: {os.path.getsize(MODEL_PATH) / 1024 / 1024:.1f} MB")

    return model, acc


if __name__ == "__main__":
    model, acc = train()
    print(f"\n[DONE] Training complete! Accuracy: {acc * 100:.2f}%")
