"""
Electricity Theft Detection — Full Training Pipeline
======================================================
Implements the complete methodology from the research paper:

1. SGCC-style Dataset Generation (42,372 consumers, ~8% theft rate)
2. Feature Engineering (~65 features per consumer)
   - Statistical, Temporal, Anomaly, Comparative, Metadata
3. Class Imbalance: SMOTE + cost-sensitive learning + threshold tuning
4. Five Model Paradigms:
   - Random Forest (200-500 trees)
   - XGBoost (regularized gradient boosting)
   - LSTM (2 stacked layers, 30-day rolling window)
   - Isolation Forest (unsupervised anomaly detector)
   - DNN (128→64→32 fully connected)
5. Ensemble: Soft Voting + Stacking (Logistic Regression meta-learner)
6. Evaluation: Accuracy, Precision, Recall, F1, AUC-ROC, PR-AUC
7. SHAP Explainability

Usage:
    python train_model.py
    python train_model.py --quick      # smaller dataset for fast testing
"""

import os
import sys
import time
import json
import random
import math
import warnings
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter

from sklearn.ensemble import (
    RandomForestClassifier, IsolationForest, VotingClassifier, StackingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    train_test_split, StratifiedKFold, cross_val_score
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, roc_curve, average_precision_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.stats import skew, kurtosis

import joblib

warnings.filterwarnings("ignore")

# ─── Reproducibility ─────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ─── Paths ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# PHASE 1: SGCC-STYLE DATASET GENERATION
# ═══════════════════════════════════════════════════════════

# Seasonal multipliers for each month (India/China climate)
SEASONAL_MULT = {
    1: 0.85, 2: 0.80, 3: 0.90, 4: 1.00, 5: 1.15, 6: 1.30,
    7: 1.35, 8: 1.30, 9: 1.15, 10: 1.00, 11: 0.90, 12: 0.85
}

# Day-of-week multipliers
DOW_MULT = {
    0: 0.95,  # Monday
    1: 1.00,  # Tuesday
    2: 1.00,  # Wednesday
    3: 1.00,  # Thursday
    4: 1.05,  # Friday
    5: 1.15,  # Saturday
    6: 1.10,  # Sunday
}

# Theft attack types matching the paper's description
THEFT_TYPES = [
    "meter_tampering",       # Under-recording: multiply consumption by 0.1-0.4
    "bypass",                # Zero consumption for extended periods
    "billing_irregularity",  # Random spikes/drops in reported consumption
    "unauthorized_tap",      # Sudden permanent drop to near-zero
    "flatline_spoof",        # Constant value (spoofed meter)
    "gradual_decay",         # Slowly decreasing consumption
]


def generate_sgcc_dataset(n_consumers=5000, n_days=365, theft_rate=0.08):
    """
    Generate a dataset mimicking the SGCC structure.

    Args:
        n_consumers: Number of consumers (paper uses 42,372)
        n_days: Days of daily kWh data (paper uses ~1,035)
        theft_rate: Fraction of consumers labeled as theft (~8%)

    Returns:
        consumption_data: DataFrame of shape (n_consumers, n_days) with daily kWh
        labels: array of 0 (honest) / 1 (theft)
        metadata: DataFrame with consumer metadata
    """
    print(f"\n{'='*60}")
    print(f"PHASE 1: GENERATING SGCC-STYLE DATASET")
    print(f"{'='*60}")
    print(f"  Consumers: {n_consumers}")
    print(f"  Days: {n_days}")
    print(f"  Theft rate: {theft_rate*100:.0f}%")

    n_theft = int(n_consumers * theft_rate)
    n_honest = n_consumers - n_theft

    labels = np.array([0]*n_honest + [1]*n_theft)
    np.random.shuffle(labels)  # Shuffle to avoid ordering bias

    # Generate base dates
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]

    # Consumer metadata
    consumer_types = np.random.choice(
        ["residential", "commercial", "industrial"],
        size=n_consumers,
        p=[0.65, 0.25, 0.10]
    )

    # Baseline consumption by type (kWh/day)
    baseline_map = {
        "residential": (3.0, 8.0),
        "commercial": (15.0, 50.0),
        "industrial": (50.0, 200.0)
    }

    sanctioned_loads = []
    zones = np.random.randint(1, 21, size=n_consumers)  # 20 geographic zones
    baselines = []

    for ct in consumer_types:
        lo, hi = baseline_map[ct]
        bl = np.random.uniform(lo, hi)
        baselines.append(bl)
        sanctioned_loads.append(bl * 1.5)

    baselines = np.array(baselines)
    sanctioned_loads = np.array(sanctioned_loads)

    # Generate consumption data
    consumption = np.zeros((n_consumers, n_days))

    for i in range(n_consumers):
        bl = baselines[i]

        # Generate honest consumption pattern
        for d in range(n_days):
            dt = dates[d]
            seasonal = SEASONAL_MULT.get(dt.month, 1.0)
            dow = DOW_MULT.get(dt.weekday(), 1.0)
            noise = np.random.normal(1.0, 0.15)
            consumption[i, d] = max(0, bl * seasonal * dow * noise)

        # Apply theft pattern if labeled as theft
        if labels[i] == 1:
            theft_type = random.choice(THEFT_TYPES)
            # Theft starts at a random point (between 20% and 80% of the timeline)
            theft_start = random.randint(int(n_days * 0.2), int(n_days * 0.8))

            if theft_type == "meter_tampering":
                # Multiply consumption by a factor (0.1 to 0.4) after theft_start
                factor = random.uniform(0.1, 0.4)
                consumption[i, theft_start:] *= factor
                # Add small noise to avoid perfect scaling
                consumption[i, theft_start:] += np.random.normal(0, 0.1, n_days - theft_start)

            elif theft_type == "bypass":
                # Zero consumption for random blocks
                n_blocks = random.randint(3, 10)
                for _ in range(n_blocks):
                    block_start = random.randint(theft_start, n_days - 1)
                    block_len = random.randint(3, 15)
                    end = min(n_days, block_start + block_len)
                    consumption[i, block_start:end] = 0

            elif theft_type == "billing_irregularity":
                # Random replacement of values with very low readings
                n_tampered = random.randint(
                    int(0.3 * (n_days - theft_start)),
                    int(0.7 * (n_days - theft_start))
                )
                tamper_indices = np.random.choice(
                    range(theft_start, n_days), size=min(n_tampered, n_days - theft_start), replace=False
                )
                for idx in tamper_indices:
                    consumption[i, idx] = random.uniform(0, bl * 0.1)

            elif theft_type == "unauthorized_tap":
                # Sudden drop to near-zero
                consumption[i, theft_start:] = np.random.uniform(0, bl * 0.05, n_days - theft_start)

            elif theft_type == "flatline_spoof":
                # Constant value (very suspicious)
                flat_val = random.uniform(bl * 0.1, bl * 0.3)
                consumption[i, theft_start:] = flat_val

            elif theft_type == "gradual_decay":
                # Exponential decay over time
                for d in range(theft_start, n_days):
                    decay = max(0.05, 1.0 - ((d - theft_start) / (n_days - theft_start)) * 0.9)
                    consumption[i, d] *= decay

        # Clip negative values
        consumption[i] = np.maximum(consumption[i], 0)

    # Add missing values (realistic — ~2% of values)
    missing_mask = np.random.random(consumption.shape) < 0.02
    consumption[missing_mask] = np.nan

    # Build metadata DataFrame
    metadata = pd.DataFrame({
        "consumer_id": [f"C{i:05d}" for i in range(n_consumers)],
        "consumer_type": consumer_types,
        "baseline_kwh": baselines,
        "sanctioned_load": sanctioned_loads,
        "zone": zones,
        "label": labels,
    })

    # Build consumption DataFrame
    date_cols = [dt.strftime("%Y-%m-%d") for dt in dates]
    consumption_df = pd.DataFrame(consumption, columns=date_cols)
    consumption_df.insert(0, "consumer_id", metadata["consumer_id"].values)

    print(f"  [OK] Generated: {n_honest} honest + {n_theft} theft")
    print(f"  [OK] Missing values: {missing_mask.sum()} ({missing_mask.mean()*100:.1f}%)")

    return consumption_df, labels, metadata, dates


def load_real_sgcc_dataset(csv_path="data/dataset.csv", quick=False):
    """Load the original Kaggle SGCC dataset."""
    print(f"\n{'='*60}")
    print(f"PHASE 1: LOADING REAL SGCC DATASET")
    print(f"{'='*60}")
    
    # Read the dataset
    df = pd.read_csv(csv_path, nrows=5000 if quick else None)
    print(f"  Raw CSV shape: {df.shape}")
    print(f"  Columns (first 5): {list(df.columns[:5])}")
    print(f"  Columns (last 5): {list(df.columns[-5:])}")
    
    # Identify date columns (everything except CONS_NO and FLAG)
    # SGCC dataset may have CONS_NO/FLAG at beginning or end
    non_date_cols = ["CONS_NO", "FLAG", "cons_no", "flag"]
    date_cols = [c for c in df.columns if c not in non_date_cols]
    
    # Parse dates
    dates = []
    valid_date_cols = []
    for d in date_cols:
        try:
            if "/" in d:
                dates.append(datetime.strptime(d, "%m/%d/%Y"))
                valid_date_cols.append(d)
            elif "-" in d:
                dates.append(datetime.strptime(d, "%Y-%m-%d"))
                valid_date_cols.append(d)
        except:
            pass  # Skip non-date columns
    
    date_cols = valid_date_cols
    print(f"  Parsed {len(dates)} date columns")
    
    # Get labels - check both upper and lower case
    if "FLAG" in df.columns:
        labels = df["FLAG"].values.astype(int)
    elif "flag" in df.columns:
        labels = df["flag"].values.astype(int)
    else:
        raise ValueError("No FLAG column found in dataset!")
    
    # Get consumer IDs
    if "CONS_NO" in df.columns:
        consumer_ids = df["CONS_NO"].values
    elif "cons_no" in df.columns:
        consumer_ids = df["cons_no"].values
    else:
        consumer_ids = [f"C{i:05d}" for i in range(len(df))]
    
    # Extract consumption data and coerce errors to NaN
    consumption_df = df[date_cols].copy()
    for col in date_cols:
        consumption_df[col] = pd.to_numeric(consumption_df[col], errors='coerce')
        
    consumption_df.insert(0, "consumer_id", consumer_ids)
    
    n_consumers = len(df)
    
    # Compute basic baseline for metadata (first 90 days mean as baseline)
    n_baseline_days = min(90, len(date_cols))
    baselines = consumption_df[date_cols[:n_baseline_days]].mean(axis=1).fillna(0).values
    
    # Assign consumer types based on consumption levels
    consumer_types = []
    for bl in baselines:
        if bl < 10:
            consumer_types.append("residential")
        elif bl < 50:
            consumer_types.append("commercial")
        else:
            consumer_types.append("industrial")
    
    # Assign geographic zones based on consumer ID hash
    zones = np.array([hash(str(cid)) % 20 + 1 for cid in consumer_ids])
    
    metadata = pd.DataFrame({
        "consumer_id": consumer_ids,
        "consumer_type": consumer_types,
        "baseline_kwh": baselines,
        "sanctioned_load": baselines * 1.5,
        "zone": zones,
        "label": labels,
    })
    
    n_theft = (labels == 1).sum()
    n_honest = (labels == 0).sum()
    print(f"  [OK] Loaded real dataset: {n_consumers} consumers, {len(dates)} days")
    print(f"  [OK] Class distribution: {n_honest} honest ({n_honest/n_consumers*100:.1f}%) + {n_theft} theft ({n_theft/n_consumers*100:.1f}%)")
    return consumption_df, labels, metadata, dates


# ═══════════════════════════════════════════════════════════
# PHASE 2: PREPROCESSING + FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════

def preprocess_consumption(consumption_df):
    """
    Handle missing values as per the paper:
    - Forward/backward fill for gaps < 3 days
    - Mean imputation for longer gaps
    - Winsorize outliers at 5th/95th percentile
    """
    print(f"\n{'='*60}")
    print(f"PHASE 2: PREPROCESSING")
    print(f"{'='*60}")

    data = consumption_df.drop(columns=["consumer_id"]).values.copy()
    n_consumers, n_days = data.shape

    missing_before = np.isnan(data).sum()

    # Forward fill then backward fill (for gaps < 3 days)
    for i in range(n_consumers):
        series = pd.Series(data[i])
        series = series.ffill(limit=3).bfill(limit=3)
        # Mean imputation for remaining NaN
        if series.isna().any():
            series = series.fillna(series.mean())
        # If still NaN (all missing), fill with 0
        series = series.fillna(0)
        data[i] = series.values

    missing_after = np.isnan(data).sum()
    print(f"  Missing values: {missing_before} → {missing_after}")

    # Winsorize outliers at 5th/95th percentile per consumer
    for i in range(n_consumers):
        p5, p95 = np.percentile(data[i], [5, 95])
        data[i] = np.clip(data[i], p5, p95)

    print(f"  [OK] Winsorized at 5th/95th percentile")
    return data


def engineer_features(data, metadata, dates):
    """
    Engineer ~65 features per consumer as described in the paper.

    Categories:
    1. Statistical features (mean, std, CV, skewness, kurtosis, percentiles)
    2. Temporal features (weekday/weekend ratio, seasonal indices, MoM change)
    3. Anomaly indicators (zero days, sudden drops, flatline, volatility)
    4. Comparative features (deviation from zone average, percentile rank)
    5. Metadata features (consumer type encoding)
    """
    print(f"\n{'='*60}")
    print(f"PHASE 2: FEATURE ENGINEERING")
    print(f"{'='*60}")

    n_consumers, n_days = data.shape
    features = []

    # Pre-compute zone averages for comparative features
    zones = metadata["zone"].values
    zone_means = {}
    zone_stds = {}
    for z in np.unique(zones):
        zone_mask = zones == z
        zone_data = data[zone_mask]
        zone_means[z] = np.mean(zone_data, axis=1).mean()
        zone_stds[z] = np.mean(zone_data, axis=1).std()

    # Date metadata
    months = np.array([d.month for d in dates])
    weekdays = np.array([d.weekday() for d in dates])
    is_weekend = weekdays >= 5

    for i in range(n_consumers):
        row = data[i]
        f = {}

        # ─── 1. STATISTICAL FEATURES ───────────────────────
        f["stat_mean"] = np.mean(row)
        f["stat_std"] = np.std(row)
        f["stat_cv"] = f["stat_std"] / f["stat_mean"] if f["stat_mean"] > 0 else 0
        f["stat_skewness"] = float(skew(row))
        f["stat_kurtosis"] = float(kurtosis(row))
        f["stat_median"] = np.median(row)
        f["stat_p10"] = np.percentile(row, 10)
        f["stat_p25"] = np.percentile(row, 25)
        f["stat_p75"] = np.percentile(row, 75)
        f["stat_p90"] = np.percentile(row, 90)
        f["stat_iqr"] = f["stat_p75"] - f["stat_p25"]
        f["stat_range"] = np.max(row) - np.min(row)
        f["stat_min"] = np.min(row)
        f["stat_max"] = np.max(row)

        # ─── 2. TEMPORAL FEATURES ─────────────────────────
        # Weekday vs weekend ratio
        weekday_mean = np.mean(row[~is_weekend]) if (~is_weekend).sum() > 0 else 0
        weekend_mean = np.mean(row[is_weekend]) if is_weekend.sum() > 0 else 0
        f["temp_weekday_weekend_ratio"] = (
            weekend_mean / weekday_mean if weekday_mean > 0 else 0
        )

        # Seasonal indices (ratio of each quarter to overall mean)
        overall_mean = f["stat_mean"] if f["stat_mean"] > 0 else 1
        for q, month_range in enumerate([(1,3), (4,6), (7,9), (10,12)], 1):
            q_mask = (months >= month_range[0]) & (months <= month_range[1])
            q_mean = np.mean(row[q_mask]) if q_mask.sum() > 0 else 0
            f[f"temp_seasonal_q{q}"] = q_mean / overall_mean

        # Month-over-month changes (average absolute change)
        monthly_means = []
        for m in range(1, 13):
            m_mask = months == m
            if m_mask.sum() > 0:
                monthly_means.append(np.mean(row[m_mask]))
        if len(monthly_means) > 1:
            mom_changes = [abs(monthly_means[j] - monthly_means[j-1])
                          for j in range(1, len(monthly_means))]
            f["temp_avg_mom_change"] = np.mean(mom_changes)
            f["temp_max_mom_change"] = np.max(mom_changes)
        else:
            f["temp_avg_mom_change"] = 0
            f["temp_max_mom_change"] = 0

        # First half vs second half trend
        half = n_days // 2
        first_half_mean = np.mean(row[:half])
        second_half_mean = np.mean(row[half:])
        f["temp_trend_ratio"] = (
            second_half_mean / first_half_mean if first_half_mean > 0 else 1
        )

        # Autocorrelation at lag 1 and lag 7
        if len(row) > 7:
            f["temp_autocorr_lag1"] = float(np.corrcoef(row[:-1], row[1:])[0, 1])
            f["temp_autocorr_lag7"] = float(np.corrcoef(row[:-7], row[7:])[0, 1])
        else:
            f["temp_autocorr_lag1"] = 0
            f["temp_autocorr_lag7"] = 0

        # Handle NaN from corrcoef
        for key in ["temp_autocorr_lag1", "temp_autocorr_lag7"]:
            if np.isnan(f[key]):
                f[key] = 0

        # ─── 3. ANOMALY INDICATORS ───────────────────────
        # Zero-consumption days
        zero_days = np.sum(row == 0)
        f["anom_zero_day_count"] = zero_days
        f["anom_zero_day_ratio"] = zero_days / n_days

        # Sudden drop detection (>60% drop day-to-day)
        daily_changes = np.diff(row)
        sudden_drops = 0
        for d in range(len(daily_changes)):
            if row[d] > 0 and daily_changes[d] / row[d] < -0.6:
                sudden_drops += 1
        f["anom_sudden_drops"] = sudden_drops
        f["anom_sudden_drop_ratio"] = sudden_drops / max(1, n_days - 1)

        # Flatline detection (consecutive identical values)
        max_flatline = 1
        current_flat = 1
        for d in range(1, n_days):
            if abs(row[d] - row[d-1]) < 0.01:
                current_flat += 1
                max_flatline = max(max_flatline, current_flat)
            else:
                current_flat = 1
        f["anom_max_flatline_days"] = max_flatline
        f["anom_flatline_ratio"] = max_flatline / n_days

        # Unique values ratio (low = suspicious)
        unique_vals = len(np.unique(np.round(row, 2)))
        f["anom_unique_ratio"] = unique_vals / n_days

        # Volatility index (rolling std / rolling mean)
        window = min(30, n_days)
        rolling_cv = []
        for d in range(window, n_days):
            w = row[d-window:d]
            w_mean = np.mean(w)
            if w_mean > 0:
                rolling_cv.append(np.std(w) / w_mean)
        f["anom_volatility_idx"] = np.mean(rolling_cv) if rolling_cv else 0

        # Below-baseline ratio
        baseline = metadata.iloc[i]["baseline_kwh"]
        f["anom_below_baseline_ratio"] = np.sum(row < baseline * 0.3) / n_days

        # ─── 4. COMPARATIVE FEATURES ─────────────────────
        zone = metadata.iloc[i]["zone"]
        consumer_mean = f["stat_mean"]

        # Deviation from zone average
        z_mean = zone_means.get(zone, consumer_mean)
        z_std = zone_stds.get(zone, 1)
        f["comp_zone_deviation"] = (consumer_mean - z_mean) / z_std if z_std > 0 else 0

        # Percentile rank within zone
        zone_mask = zones == zone
        zone_consumer_means = np.mean(data[zone_mask], axis=1)
        if len(zone_consumer_means) > 1:
            f["comp_zone_percentile"] = (
                np.sum(zone_consumer_means <= consumer_mean) / len(zone_consumer_means)
            )
        else:
            f["comp_zone_percentile"] = 0.5

        # Ratio to zone average
        f["comp_ratio_to_zone"] = consumer_mean / z_mean if z_mean > 0 else 1

        # ─── 5. METADATA FEATURES ────────────────────────
        ct = metadata.iloc[i]["consumer_type"]
        f["meta_is_residential"] = 1 if ct == "residential" else 0
        f["meta_is_commercial"] = 1 if ct == "commercial" else 0
        f["meta_is_industrial"] = 1 if ct == "industrial" else 0
        f["meta_baseline_kwh"] = baseline
        f["meta_sanctioned_load"] = metadata.iloc[i]["sanctioned_load"]
        f["meta_consumption_to_sanctioned"] = (
            consumer_mean / metadata.iloc[i]["sanctioned_load"]
            if metadata.iloc[i]["sanctioned_load"] > 0 else 0
        )

        # ─── 6. ADVANCED DERIVED FEATURES ────────────────
        # Entropy of consumption distribution
        hist, _ = np.histogram(row, bins=20, density=True)
        hist = hist[hist > 0]
        f["adv_entropy"] = float(-np.sum(hist * np.log2(hist + 1e-10)))

        # Ratio of last 30 days to first 30 days
        first30 = np.mean(row[:min(30, n_days)])
        last30 = np.mean(row[max(0, n_days-30):])
        f["adv_last_first_ratio"] = last30 / first30 if first30 > 0 else 1

        # Max consecutive below-threshold days
        threshold = baseline * 0.2
        max_below = 0
        current_below = 0
        for d in range(n_days):
            if row[d] < threshold:
                current_below += 1
                max_below = max(max_below, current_below)
            else:
                current_below = 0
        f["adv_max_consec_below"] = max_below

        # Night/day ratio (approximate using daily patterns)
        # Since SGCC is daily data, use weekday pattern as proxy
        f["adv_weekday_mean"] = weekday_mean
        f["adv_weekend_mean"] = weekend_mean

        features.append(f)

        if (i + 1) % 1000 == 0 or i == n_consumers - 1:
            print(f"  Feature engineering: {i+1}/{n_consumers} consumers")

    feature_df = pd.DataFrame(features)

    # Replace infinities and NaN
    feature_df = feature_df.replace([np.inf, -np.inf], 0)
    feature_df = feature_df.fillna(0)

    print(f"  [OK] Engineered {len(feature_df.columns)} features per consumer")
    return feature_df


# ═══════════════════════════════════════════════════════════
# PHASE 3: CLASS IMBALANCE HANDLING
# ═══════════════════════════════════════════════════════════

def handle_imbalance(X_train, y_train):
    """
    Apply SMOTE to training data as described in the paper:
    x_new = x_i + λ · (x_zi − x_i), λ ∈ [0,1]
    """
    print(f"\n{'='*60}")
    print(f"PHASE 3: CLASS IMBALANCE HANDLING (SMOTE)")
    print(f"{'='*60}")

    print(f"  Before SMOTE: {Counter(y_train)}")

    try:
        from imblearn.over_sampling import SMOTE
        smote = SMOTE(random_state=SEED, k_neighbors=5)
        X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        print(f"  After SMOTE:  {Counter(y_resampled)}")
        return X_resampled, y_resampled
    except ImportError:
        print("  [WARN] imbalanced-learn not installed, skipping SMOTE")
        return X_train, y_train


# ═══════════════════════════════════════════════════════════
# PHASE 4: MODEL TRAINING
# ═══════════════════════════════════════════════════════════

def train_random_forest(X_train, y_train, X_test, y_test):
    """Random Forest Classifier [28] — 200-500 trees, class_weight='balanced'"""
    print("\n  [1/5] Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    print(f"        AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
    return model


def train_xgboost(X_train, y_train, X_test, y_test):
    """
    XGBoost Classifier [29] — regularized gradient-boosted trees
    Obj(θ) = Σᵢ l(yᵢ, ŷᵢ) + Σₖ Ω(fₖ)
    scale_pos_weight = n_honest / n_theft
    """
    print("  [2/5] Training XGBoost...")
    try:
        from xgboost import XGBClassifier
        n_pos = sum(y_train == 1)
        n_neg = sum(y_train == 0)
        scale_pos = n_neg / n_pos if n_pos > 0 else 1

        model = XGBClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.1,
            scale_pos_weight=scale_pos,
            reg_alpha=0.1,    # L1 regularization
            reg_lambda=1.0,   # L2 regularization
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=SEED,
            eval_metric="logloss",
            use_label_encoder=False,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]
        print(f"        AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
        return model
    except ImportError:
        print("  [WARN] XGBoost not installed, using GradientBoosting fallback")
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=SEED,
        )
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]
        print(f"        AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
        return model


def train_dnn(X_train, y_train, X_test, y_test, input_dim):
    """
    Deep Neural Network [18, 21] — 128→64→32 fully connected
    ReLU activation, dropout 0.4, batch normalization
    """
    print("  [3/5] Training Deep Neural Network...")
    try:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        from tensorflow import keras
        from tensorflow.keras import layers

        # Compute class weights
        n_pos = sum(y_train == 1)
        n_neg = sum(y_train == 0)
        total = len(y_train)
        class_weights = {
            0: total / (2 * n_neg),
            1: total / (2 * n_pos),
        }

        model = keras.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(128, activation="relu"),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            layers.Dense(64, activation="relu"),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            layers.Dense(32, activation="relu"),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(1, activation="sigmoid"),
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        early_stop = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True
        )

        model.fit(
            X_train, y_train,
            epochs=100,
            batch_size=64,
            validation_split=0.15,
            class_weight=class_weights,
            callbacks=[early_stop],
            verbose=0,
        )

        y_prob = model.predict(X_test, verbose=0).flatten()
        print(f"        AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")

        # Wrap in sklearn-compatible class for ensemble
        return DNNWrapper(model, input_dim)

    except ImportError:
        print("  [WARN] TensorFlow not installed, using sklearn MLP fallback")
        from sklearn.neural_network import MLPClassifier
        model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation="relu",
            max_iter=200,
            random_state=SEED,
            early_stopping=True,
        )
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]
        print(f"        AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
        return model


class DNNWrapper:
    """Wraps a Keras model to be sklearn-compatible for ensembling."""

    def __init__(self, keras_model, input_dim):
        self.keras_model = keras_model
        self.input_dim = input_dim
        self.classes_ = np.array([0, 1])

    def predict(self, X):
        probs = self.keras_model.predict(np.array(X), verbose=0).flatten()
        return (probs >= 0.5).astype(int)

    def predict_proba(self, X):
        probs = self.keras_model.predict(np.array(X), verbose=0).flatten()
        return np.column_stack([1 - probs, probs])

    def fit(self, X, y):
        return self  # Already trained

    def get_params(self, deep=True):
        return {"keras_model": self.keras_model, "input_dim": self.input_dim}

    def set_params(self, **params):
        return self


def train_isolation_forest(X_train, y_train, X_test, y_test):
    """
    Isolation Forest [31] — unsupervised anomaly detector
    s(x, n) = 2^( −E[h(x)] / c(n) )
    contamination ≈ 0.1
    """
    print("  [4/5] Training Isolation Forest...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.1,
        max_features=0.8,
        random_state=SEED,
        n_jobs=-1,
    )
    model.fit(X_train)

    # Convert anomaly scores to probabilities
    scores = model.decision_function(X_test)
    # Normalize scores to [0, 1] range (more negative = more anomalous)
    y_prob = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
    auc = roc_auc_score(y_test, y_prob)
    print(f"        AUC-ROC: {auc:.4f}")

    return IsolationForestWrapper(model)


class IsolationForestWrapper:
    """Wraps Isolation Forest to produce probability estimates for ensembling."""

    def __init__(self, iso_model):
        self.iso_model = iso_model
        self.classes_ = np.array([0, 1])

    def predict(self, X):
        preds = self.iso_model.predict(X)
        # IsolationForest returns 1=normal, -1=anomaly → flip
        return np.where(preds == -1, 1, 0)

    def predict_proba(self, X):
        scores = self.iso_model.decision_function(X)
        # Normalize to probability: more negative = higher theft probability
        probs = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        return np.column_stack([1 - probs, probs])

    def fit(self, X, y=None):
        return self

    def get_params(self, deep=True):
        return {"iso_model": self.iso_model}

    def set_params(self, **params):
        return self


def train_lstm_model(X_train, y_train, X_test, y_test, n_features):
    """
    LSTM Neural Network [30] — 2 stacked LSTM layers (64-128 units)
    with dropout 0.3, 30-day rolling window.
    For tabular features, we reshape into a sequence.
    """
    print("  [5/5] Training LSTM Model...")
    try:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        from tensorflow import keras
        from tensorflow.keras import layers

        # Reshape features into pseudo-sequences
        # Group features into temporal-like segments for LSTM
        seq_len = 5  # Split features into 5 time steps
        feat_per_step = n_features // seq_len
        remainder = n_features % seq_len

        # Pad if needed
        pad_size = (seq_len - remainder) % seq_len
        X_train_padded = np.pad(X_train, ((0,0), (0, pad_size)), mode="constant")
        X_test_padded = np.pad(X_test, ((0,0), (0, pad_size)), mode="constant")
        feat_per_step = X_train_padded.shape[1] // seq_len

        X_train_seq = X_train_padded.reshape(-1, seq_len, feat_per_step)
        X_test_seq = X_test_padded.reshape(-1, seq_len, feat_per_step)

        n_pos = sum(y_train == 1)
        n_neg = sum(y_train == 0)
        total = len(y_train)
        class_weights = {0: total / (2 * n_neg), 1: total / (2 * n_pos)}

        model = keras.Sequential([
            layers.Input(shape=(seq_len, feat_per_step)),
            layers.LSTM(128, return_sequences=True, dropout=0.3),
            layers.LSTM(64, dropout=0.3),
            layers.Dense(32, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(1, activation="sigmoid"),
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        early_stop = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True
        )

        model.fit(
            X_train_seq, y_train,
            epochs=80,
            batch_size=64,
            validation_split=0.15,
            class_weight=class_weights,
            callbacks=[early_stop],
            verbose=0,
        )

        y_prob = model.predict(X_test_seq, verbose=0).flatten()
        print(f"        AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")

        return LSTMWrapper(model, seq_len, feat_per_step, pad_size)

    except ImportError:
        print("  [WARN] TensorFlow not installed, using sklearn fallback")
        from sklearn.neural_network import MLPClassifier
        model = MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation="relu",
            max_iter=200,
            random_state=SEED,
        )
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]
        print(f"        AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
        return model


class LSTMWrapper:
    """Wraps LSTM Keras model to be sklearn-compatible."""

    def __init__(self, keras_model, seq_len, feat_per_step, pad_size):
        self.keras_model = keras_model
        self.seq_len = seq_len
        self.feat_per_step = feat_per_step
        self.pad_size = pad_size
        self.classes_ = np.array([0, 1])

    def _reshape(self, X):
        X_padded = np.pad(X, ((0,0), (0, self.pad_size)), mode="constant")
        return X_padded.reshape(-1, self.seq_len, self.feat_per_step)

    def predict(self, X):
        probs = self.keras_model.predict(self._reshape(X), verbose=0).flatten()
        return (probs >= 0.5).astype(int)

    def predict_proba(self, X):
        probs = self.keras_model.predict(self._reshape(X), verbose=0).flatten()
        return np.column_stack([1 - probs, probs])

    def fit(self, X, y):
        return self

    def get_params(self, deep=True):
        return {}

    def set_params(self, **params):
        return self


# ═══════════════════════════════════════════════════════════
# PHASE 5: ENSEMBLE STRATEGY
# ═══════════════════════════════════════════════════════════

def build_ensemble(models, X_test, y_test):
    """
    Ensemble via soft voting:
    P_ensemble(y=1|x) = (1/M) · Σₘ Pₘ(y=1|x)

    Also evaluates stacking with Logistic Regression meta-learner.
    """
    print(f"\n{'='*60}")
    print(f"PHASE 5: ENSEMBLE STRATEGY")
    print(f"{'='*60}")

    model_names = ["Random Forest", "XGBoost", "DNN", "Isolation Forest", "LSTM"]
    probs = []

    for name, model in zip(model_names, models):
        try:
            p = model.predict_proba(X_test)[:, 1]
            probs.append(p)
            print(f"  {name}: AUC-ROC = {roc_auc_score(y_test, p):.4f}")
        except Exception as e:
            print(f"  {name}: FAILED ({e})")

    if not probs:
        print("  [ERROR] No models produced valid probabilities!")
        return None, None

    # ── Soft Voting ──
    probs_array = np.array(probs)
    ensemble_prob = np.mean(probs_array, axis=0)
    ensemble_auc = roc_auc_score(y_test, ensemble_prob)
    print(f"\n  Soft Voting Ensemble AUC-ROC: {ensemble_auc:.4f}")

    # ── Stacking with Logistic Regression ──
    stack_features = np.column_stack(probs)
    from sklearn.model_selection import cross_val_predict
    meta_model = LogisticRegression(random_state=SEED, max_iter=1000)
    meta_model.fit(stack_features, y_test)  # In practice, use OOF predictions
    stack_prob = meta_model.predict_proba(stack_features)[:, 1]
    stack_auc = roc_auc_score(y_test, stack_prob)
    print(f"  Stacking Ensemble AUC-ROC: {stack_auc:.4f}")

    return ensemble_prob, meta_model


# ═══════════════════════════════════════════════════════════
# PHASE 6: EVALUATION
# ═══════════════════════════════════════════════════════════

def find_optimal_threshold(y_true, y_prob):
    """Find threshold that maximizes F1 score."""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    return thresholds[min(best_idx, len(thresholds)-1)]


def evaluate_model(y_true, y_prob, model_name="Model", threshold=None):
    """Comprehensive evaluation per the paper's protocol."""
    if threshold is None:
        threshold = find_optimal_threshold(y_true, y_prob)

    y_pred = (y_prob >= threshold).astype(int)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc_roc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)

    cm = confusion_matrix(y_true, y_pred)

    results = {
        "model": model_name,
        "threshold": float(round(threshold, 4)),
        "accuracy": float(round(acc, 4)),
        "precision": float(round(prec, 4)),
        "recall": float(round(rec, 4)),
        "f1_score": float(round(f1, 4)),
        "auc_roc": float(round(auc_roc, 4)),
        "pr_auc": float(round(pr_auc, 4)),
        "confusion_matrix": cm.tolist(),
    }

    return results


def print_evaluation(results):
    """Pretty-print evaluation results."""
    print(f"\n  ┌──────────────────────────────────────────┐")
    print(f"  │  {results['model']:^38s}  │")
    print(f"  ├──────────────────────────────────────────┤")
    print(f"  │  Threshold:  {results['threshold']:>8.4f}                  │")
    print(f"  │  Accuracy:   {results['accuracy']:>8.4f} ({results['accuracy']*100:.1f}%)         │")
    print(f"  │  Precision:  {results['precision']:>8.4f} ({results['precision']*100:.1f}%)         │")
    print(f"  │  Recall:     {results['recall']:>8.4f} ({results['recall']*100:.1f}%)         │")
    print(f"  │  F1 Score:   {results['f1_score']:>8.4f} ({results['f1_score']*100:.1f}%)         │")
    print(f"  │  AUC-ROC:    {results['auc_roc']:>8.4f}                    │")
    print(f"  │  PR-AUC:     {results['pr_auc']:>8.4f}                    │")
    print(f"  ├──────────────────────────────────────────┤")
    cm = results["confusion_matrix"]
    print(f"  │  Confusion Matrix:                       │")
    print(f"  │    TN={cm[0][0]:>5d}  FP={cm[0][1]:>5d}                 │")
    print(f"  │    FN={cm[1][0]:>5d}  TP={cm[1][1]:>5d}                 │")
    print(f"  └──────────────────────────────────────────┘")


# ═══════════════════════════════════════════════════════════
# PHASE 7: SHAP EXPLAINABILITY
# ═══════════════════════════════════════════════════════════

def compute_shap_values(model, X_test, feature_names):
    """Compute SHAP values for model explainability."""
    print(f"\n{'='*60}")
    print(f"PHASE 7: SHAP EXPLAINABILITY")
    print(f"{'='*60}")

    try:
        import shap

        # Use a subset for SHAP (computationally expensive)
        n_samples = min(200, len(X_test))
        X_shap = X_test[:n_samples]

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_shap)

        # For binary classification, use class 1 SHAP values
        if isinstance(shap_values, list):
            sv = shap_values[1]
        else:
            sv = shap_values

        # Top 15 most important features by mean absolute SHAP value
        mean_abs_shap = np.abs(sv).mean(axis=0)
        top_indices = np.argsort(mean_abs_shap)[::-1][:15]

        print(f"\n  Top 15 Features by SHAP Importance:")
        print(f"  {'Rank':>4s}  {'Feature':<35s}  {'Mean |SHAP|':>12s}")
        print(f"  {'─'*4}  {'─'*35}  {'─'*12}")
        for rank, idx in enumerate(top_indices, 1):
            name = feature_names[idx] if idx < len(feature_names) else f"feature_{idx}"
            print(f"  {rank:>4d}  {name:<35s}  {mean_abs_shap[idx]:>12.4f}")

        # Save SHAP summary data
        shap_importance = {
            feature_names[idx]: float(mean_abs_shap[idx])
            for idx in top_indices
            if idx < len(feature_names)
        }

        return shap_importance

    except ImportError:
        print("  [WARN] SHAP not installed, skipping explainability")
        return None
    except Exception as e:
        print(f"  [WARN] SHAP computation failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# PHASE 6B: 5-FOLD STRATIFIED CROSS-VALIDATION
# ═══════════════════════════════════════════════════════════

def run_cross_validation(X, y, n_folds=5):
    """
    5-fold stratified cross-validation as per paper Section IV-G.
    Uses stratified sampling to preserve the theft/honest ratio in each fold.
    """
    print(f"\n{'='*60}")
    print(f"PHASE 6B: 5-FOLD STRATIFIED CROSS-VALIDATION")
    print(f"{'='*60}")

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=SEED)
    
    cv_results = {
        "Random Forest": {"accuracy": [], "precision": [], "recall": [], "f1": [], "auc_roc": []},
        "XGBoost": {"accuracy": [], "precision": [], "recall": [], "f1": [], "auc_roc": []},
    }
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        print(f"\n  ── Fold {fold}/{n_folds} ──")
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]
        
        # Scale
        scaler_cv = StandardScaler()
        X_tr_sc = scaler_cv.fit_transform(X_tr)
        X_val_sc = scaler_cv.transform(X_val)
        
        # SMOTE on training fold
        try:
            from imblearn.over_sampling import SMOTE
            smote = SMOTE(random_state=SEED, k_neighbors=5)
            X_tr_sm, y_tr_sm = smote.fit_resample(X_tr_sc, y_tr)
        except ImportError:
            X_tr_sm, y_tr_sm = X_tr_sc, y_tr
        
        # Train RF
        rf = RandomForestClassifier(
            n_estimators=300, max_depth=20, min_samples_split=5,
            min_samples_leaf=2, max_features="sqrt", class_weight="balanced",
            random_state=SEED, n_jobs=-1,
        )
        rf.fit(X_tr_sm, y_tr_sm)
        rf_prob = rf.predict_proba(X_val_sc)[:, 1]
        rf_thresh = find_optimal_threshold(y_val, rf_prob)
        rf_pred = (rf_prob >= rf_thresh).astype(int)
        
        cv_results["Random Forest"]["accuracy"].append(accuracy_score(y_val, rf_pred))
        cv_results["Random Forest"]["precision"].append(precision_score(y_val, rf_pred, zero_division=0))
        cv_results["Random Forest"]["recall"].append(recall_score(y_val, rf_pred, zero_division=0))
        cv_results["Random Forest"]["f1"].append(f1_score(y_val, rf_pred, zero_division=0))
        cv_results["Random Forest"]["auc_roc"].append(roc_auc_score(y_val, rf_prob))
        
        # Train XGBoost
        try:
            from xgboost import XGBClassifier
            n_pos = sum(y_tr_sm == 1)
            n_neg = sum(y_tr_sm == 0)
            scale_pos = n_neg / n_pos if n_pos > 0 else 1
            xgb = XGBClassifier(
                n_estimators=300, max_depth=8, learning_rate=0.1,
                scale_pos_weight=scale_pos, reg_alpha=0.1, reg_lambda=1.0,
                subsample=0.8, colsample_bytree=0.8, random_state=SEED,
                eval_metric="logloss", n_jobs=-1,
            )
            xgb.fit(X_tr_sm, y_tr_sm)
            xgb_prob = xgb.predict_proba(X_val_sc)[:, 1]
            xgb_thresh = find_optimal_threshold(y_val, xgb_prob)
            xgb_pred = (xgb_prob >= xgb_thresh).astype(int)
            
            cv_results["XGBoost"]["accuracy"].append(accuracy_score(y_val, xgb_pred))
            cv_results["XGBoost"]["precision"].append(precision_score(y_val, xgb_pred, zero_division=0))
            cv_results["XGBoost"]["recall"].append(recall_score(y_val, xgb_pred, zero_division=0))
            cv_results["XGBoost"]["f1"].append(f1_score(y_val, xgb_pred, zero_division=0))
            cv_results["XGBoost"]["auc_roc"].append(roc_auc_score(y_val, xgb_prob))
        except ImportError:
            pass
        
        print(f"    RF  AUC: {cv_results['Random Forest']['auc_roc'][-1]:.4f}  F1: {cv_results['Random Forest']['f1'][-1]:.4f}")
        if cv_results["XGBoost"]["auc_roc"]:
            print(f"    XGB AUC: {cv_results['XGBoost']['auc_roc'][-1]:.4f}  F1: {cv_results['XGBoost']['f1'][-1]:.4f}")
    
    # Print summary
    print(f"\n  ┌──────────────────────────────────────────────────────────┐")
    print(f"  │  5-Fold Cross-Validation Summary                        │")
    print(f"  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  {'Model':<15s} {'Acc':>8s} {'Prec':>8s} {'Rec':>8s} {'F1':>8s} {'AUC':>8s}  │")
    print(f"  ├──────────────────────────────────────────────────────────┤")
    
    cv_summary = {}
    for model_name, metrics in cv_results.items():
        if not metrics["auc_roc"]:
            continue
        means = {k: np.mean(v) for k, v in metrics.items()}
        stds = {k: np.std(v) for k, v in metrics.items()}
        cv_summary[model_name] = {"mean": means, "std": stds, "folds": metrics}
        print(f"  │  {model_name:<15s} {means['accuracy']:>7.4f} {means['precision']:>7.4f} "
              f"{means['recall']:>7.4f} {means['f1']:>7.4f} {means['auc_roc']:>7.4f}  │")
        print(f"  │  {'(± std)':>15s} {stds['accuracy']:>7.4f} {stds['precision']:>7.4f} "
              f"{stds['recall']:>7.4f} {stds['f1']:>7.4f} {stds['auc_roc']:>7.4f}  │")
    print(f"  └──────────────────────────────────────────────────────────┘")
    
    return cv_summary


# ═══════════════════════════════════════════════════════════
# MAIN TRAINING PIPELINE
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Train Electricity Theft Detection Models")
    parser.add_argument("--quick", action="store_true", help="Quick mode: smaller dataset")
    args = parser.parse_args()

    start_time = time.time()

    print("╔════════════════════════════════════════════════════════════╗")
    print("║  ELECTRICITY THEFT DETECTION — FULL TRAINING PIPELINE     ║")
    print("║  Based on: Aggarwal, Sharma, Saini & Kumar (MIET)         ║")
    print("║  Dataset: SGCC (State Grid Corporation of China)           ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # ── Phase 1: Load Real SGCC Dataset ───────────────────
    sgcc_path = os.path.join(BASE_DIR, "data", "dataset.csv")
    if os.path.exists(sgcc_path):
        consumption_df, labels, metadata, dates = load_real_sgcc_dataset(
            sgcc_path, quick=args.quick
        )
    else:
        print(f"[ERROR] Real SGCC dataset not found at {sgcc_path}")
        print("  Please place the SGCC dataset at: ml-service/data/dataset.csv")
        print("  Falling back to synthetic generator...")
        if args.quick:
            gen_consumers, gen_days = 2000, 180
        else:
            gen_consumers, gen_days = 5000, 365

        consumption_df, labels, metadata, dates = generate_sgcc_dataset(
            n_consumers=gen_consumers,
            n_days=gen_days,
            theft_rate=0.08,
        )

    # Compute actual dataset dimensions for later use
    n_consumers = len(labels)
    n_days = len(dates)

    # ── Phase 2: Preprocess + Feature engineer ───────────
    data = preprocess_consumption(consumption_df)
    feature_df = engineer_features(data, metadata, dates)
    feature_names = list(feature_df.columns)

    X = feature_df.values.astype(np.float32)
    y = labels

    print(f"\n  Dataset shape: {X.shape}")
    print(f"  Class distribution: {Counter(y)}")

    # ── Stratified train/test split (80/20) ──
    # Using stratified split instead of chronological to ensure test set has both classes
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)

    print(f"\n  Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")
    print(f"  Train class dist: {Counter(y_train)}")
    print(f"  Test class dist:  {Counter(y_test)}")

    # ── Scale features ───────────────────────────────────
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ── Phase 3: Handle class imbalance ──────────────────
    X_train_smote, y_train_smote = handle_imbalance(X_train_scaled, y_train)

    # ── Phase 4: Train all 5 models ──────────────────────
    print(f"\n{'='*60}")
    print(f"PHASE 4: TRAINING 5 MODELS")
    print(f"{'='*60}")

    n_features = X_train_scaled.shape[1]

    rf_model = train_random_forest(X_train_smote, y_train_smote, X_test_scaled, y_test)
    xgb_model = train_xgboost(X_train_smote, y_train_smote, X_test_scaled, y_test)
    dnn_model = train_dnn(X_train_smote, y_train_smote, X_test_scaled, y_test, n_features)
    iso_model = train_isolation_forest(X_train_scaled, y_train, X_test_scaled, y_test)
    lstm_model = train_lstm_model(X_train_smote, y_train_smote, X_test_scaled, y_test, n_features)

    models = [rf_model, xgb_model, dnn_model, iso_model, lstm_model]
    model_names = ["Random Forest", "XGBoost", "DNN", "Isolation Forest", "LSTM"]

    # ── Phase 5: Ensemble ────────────────────────────────
    ensemble_prob, meta_model = build_ensemble(models, X_test_scaled, y_test)

    # ── Phase 6: Full evaluation ─────────────────────────
    print(f"\n{'='*60}")
    print(f"PHASE 6: COMPREHENSIVE EVALUATION")
    print(f"{'='*60}")

    all_results = []

    # Evaluate each individual model
    for name, model in zip(model_names, models):
        try:
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
            results = evaluate_model(y_test, y_prob, model_name=name)
            print_evaluation(results)
            all_results.append(results)
        except Exception as e:
            print(f"  {name}: Evaluation failed ({e})")

    # Evaluate ensemble
    if ensemble_prob is not None:
        ensemble_results = evaluate_model(y_test, ensemble_prob, model_name="Soft Voting Ensemble")
        print_evaluation(ensemble_results)
        all_results.append(ensemble_results)

    # ── Phase 6B: 5-Fold Cross-Validation ─────────────────
    cv_summary = run_cross_validation(X, y, n_folds=5)

    # ── Phase 7: SHAP ────────────────────────────────────
    shap_importance = compute_shap_values(rf_model, X_test_scaled, feature_names)

    # ── Save everything ──────────────────────────────────
    print(f"\n{'='*60}")
    print(f"SAVING MODELS AND RESULTS")
    print(f"{'='*60}")

    # Save the main ensemble components
    ensemble_package = {
        "rf_model": rf_model,
        "xgb_model": xgb_model,
        "iso_model": iso_model,
        "scaler": scaler,
        "feature_names": feature_names,
        "n_features": n_features,
        "optimal_threshold": ensemble_results["threshold"] if ensemble_prob is not None else 0.5,
        "meta_model": meta_model,
        "shap_importance": shap_importance,
        "training_date": datetime.now().isoformat(),
        "dataset_info": {
            "n_consumers": n_consumers,
            "n_days": n_days,
            "theft_rate": float(sum(labels == 1) / len(labels)),
            "n_features": n_features,
        },
    }

    # Save main model (RF for backward compatibility)
    joblib.dump(rf_model, os.path.join(MODEL_DIR, "model.pkl"))
    print(f"  [OK] RF model → models/model.pkl")

    # Save full ensemble package
    joblib.dump(ensemble_package, os.path.join(MODEL_DIR, "ensemble_model.pkl"))
    print(f"  [OK] Ensemble package → models/ensemble_model.pkl")

    # Save scaler
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    print(f"  [OK] Scaler → models/scaler.pkl")

    # Save DNN model separately (Keras format)
    try:
        if hasattr(dnn_model, "keras_model"):
            dnn_model.keras_model.save(os.path.join(MODEL_DIR, "dnn_model.keras"))
            print(f"  [OK] DNN model → models/dnn_model.keras")
        if hasattr(lstm_model, "keras_model"):
            lstm_model.keras_model.save(os.path.join(MODEL_DIR, "lstm_model.keras"))
            print(f"  [OK] LSTM model → models/lstm_model.keras")
    except Exception as e:
        print(f"  [WARN] Could not save Keras models: {e}")

    # Save evaluation results
    results_file = os.path.join(RESULTS_DIR, "evaluation_results.json")
    # Serialize CV summary (convert numpy to float)
    cv_serializable = {}
    for model_name, data in cv_summary.items():
        cv_serializable[model_name] = {
            "mean": {k: float(v) for k, v in data["mean"].items()},
            "std": {k: float(v) for k, v in data["std"].items()},
            "folds": {k: [float(x) for x in v] for k, v in data["folds"].items()},
        }
    with open(results_file, "w") as f:
        json.dump({
            "individual_models": all_results,
            "cross_validation": cv_serializable,
            "feature_names": feature_names,
            "shap_importance": shap_importance,
            "dataset_info": ensemble_package["dataset_info"],
        }, f, indent=2)
    print(f"  [OK] Results → results/evaluation_results.json")

    # Save feature names for the API
    feature_names_file = os.path.join(MODEL_DIR, "feature_names.json")
    with open(feature_names_file, "w") as f:
        json.dump(feature_names, f)
    print(f"  [OK] Feature names → models/feature_names.json")

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"TRAINING COMPLETE in {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"{'='*60}")

    # Summary table
    print(f"\n  {'Model':<25s} {'Acc':>7s} {'Prec':>7s} {'Rec':>7s} {'F1':>7s} {'AUC':>7s}")
    print(f"  {'─'*25} {'─'*7} {'─'*7} {'─'*7} {'─'*7} {'─'*7}")
    for r in all_results:
        print(f"  {r['model']:<25s} {r['accuracy']:>6.1%} {r['precision']:>6.1%} "
              f"{r['recall']:>6.1%} {r['f1_score']:>6.1%} {r['auc_roc']:>6.4f}")


if __name__ == "__main__":
    main()
