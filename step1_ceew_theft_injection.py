"""
=============================================================================
 CEEW Dataset: Synthetic Theft Injection + Feature Engineering + SMOTE Pipeline
=============================================================================
This script processes the CEEW Mathura/Bareilly 3-minute interval smart meter
data by:
  1. Sampling a manageable subset (per meter, hourly aggregation)
  2. Engineering 47 features from the raw telemetry
  3. Injecting 7 realistic synthetic theft profiles
  4. Applying SMOTE to handle class imbalance
  5. Saving the processed dataset for model training

Theft Profiles (based on published NTL research):
  T1 - Peak-hour bypass:       Zero consumption during 8AM-8PM
  T2 - Flat-line spoofing:     Constant consumption readings
  T3 - Gradual consumption drop: Slow reduction over time
  T4 - Night-only usage:       Consumption only between 10PM-6AM
  T5 - Voltage tampering:      Abnormally low voltage readings
  T6 - Current bypass:         Near-zero current with normal voltage
  T7 - Random partial theft:   Random 30-70% reduction in consumption
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import glob
import warnings
from collections import defaultdict
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler
import joblib

warnings.filterwarnings('ignore')
np.random.seed(42)


# ─── STEP 1: Load & Aggregate CEEW Data ─────────────────────────────────────

def load_ceew_data(data_dir="data", sample_meters=20):
    """Load CEEW CSV files and aggregate to hourly readings per meter."""
    
    ceew_files = [f for f in glob.glob(os.path.join(data_dir, "*.csv"))
                  if "CEEW" in f or "SM Cleaned" in f]
    
    if not ceew_files:
        print("No CEEW files found!")
        return None
    
    print(f"Found {len(ceew_files)} CEEW data files. Loading...")
    
    dfs = []
    for f in ceew_files:
        print(f"  Reading: {os.path.basename(f)}")
        # Read in chunks for memory efficiency
        chunk_iter = pd.read_csv(f, chunksize=500_000)
        for chunk in chunk_iter:
            # Standardize column names
            col_map = {}
            for c in chunk.columns:
                cl = c.lower()
                if 'timestamp' in cl:
                    col_map[c] = 'timestamp'
                elif 'kwh' in cl:
                    col_map[c] = 'kwh'
                elif 'voltage' in cl or 'volt' in cl:
                    col_map[c] = 'voltage'
                elif 'current' in cl or 'amp' in cl:
                    col_map[c] = 'current'
                elif 'freq' in cl:
                    col_map[c] = 'frequency'
                elif 'meter' in cl:
                    col_map[c] = 'meter'
                elif 'date' in cl:
                    col_map[c] = 'date'
            chunk = chunk.rename(columns=col_map)
            
            needed = ['timestamp', 'kwh', 'voltage', 'current', 'frequency', 'meter']
            if all(col in chunk.columns for col in needed):
                dfs.append(chunk[needed])
    
    if not dfs:
        print("No valid CEEW data could be loaded.")
        return None
    
    print("Concatenating all chunks...")
    df = pd.concat(dfs, ignore_index=True)
    print(f"Total raw records: {len(df):,}")
    
    # Parse timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    
    # Sample meters for tractability
    unique_meters = df['meter'].unique()
    print(f"Total unique meters: {len(unique_meters)}")
    
    if len(unique_meters) > sample_meters:
        selected = np.random.choice(unique_meters, sample_meters, replace=False)
        df = df[df['meter'].isin(selected)]
        print(f"Sampled {sample_meters} meters for processing")
    
    # Aggregate to hourly
    print("Aggregating to hourly intervals...")
    df['hour_bucket'] = df['timestamp'].dt.floor('h')
    
    hourly = df.groupby(['meter', 'hour_bucket']).agg(
        kwh=('kwh', 'sum'),
        voltage=('voltage', 'mean'),
        current=('current', 'mean'),
        frequency=('frequency', 'mean'),
        reading_count=('kwh', 'count')
    ).reset_index()
    
    hourly = hourly.rename(columns={'hour_bucket': 'timestamp'})
    hourly = hourly.sort_values(['meter', 'timestamp']).reset_index(drop=True)
    
    print(f"Hourly aggregated records: {len(hourly):,}")
    return hourly


# ─── STEP 2: Inject Synthetic Theft Profiles ────────────────────────────────

def inject_theft_profiles(df):
    """
    Take genuine hourly meter data and create theft variants.
    Returns a combined DataFrame with 'label' column (0=normal, 1=theft)
    and 'theft_type' column.
    """
    print("\nInjecting synthetic theft profiles...")
    
    # Mark all original data as normal
    normal_df = df.copy()
    normal_df['label'] = 0
    normal_df['theft_type'] = 'normal'
    
    theft_dfs = []
    meters = df['meter'].unique()
    
    for meter_id in meters:
        meter_data = df[df['meter'] == meter_id].copy()
        
        if len(meter_data) < 48:  # Need at least 2 days of hourly data
            continue
        
        # T1: Peak-hour bypass — zero consumption during 8AM-8PM
        t1 = meter_data.copy()
        peak_mask = t1['timestamp'].dt.hour.between(8, 19)
        t1.loc[peak_mask, 'kwh'] = 0.0
        t1.loc[peak_mask, 'current'] = t1.loc[peak_mask, 'current'] * 0.05
        t1['label'] = 1
        t1['theft_type'] = 'T1_peak_bypass'
        t1['meter'] = f"{meter_id}_T1"
        theft_dfs.append(t1)
        
        # T2: Flat-line spoofing — constant consumption
        t2 = meter_data.copy()
        flat_val = meter_data['kwh'].median() * 0.3
        t2['kwh'] = flat_val
        t2['label'] = 1
        t2['theft_type'] = 'T2_flatline'
        t2['meter'] = f"{meter_id}_T2"
        theft_dfs.append(t2)
        
        # T3: Gradual consumption drop — slow decline over time
        t3 = meter_data.copy()
        n = len(t3)
        decay = np.linspace(1.0, 0.15, n)
        t3['kwh'] = t3['kwh'] * decay
        t3['current'] = t3['current'] * decay
        t3['label'] = 1
        t3['theft_type'] = 'T3_gradual_drop'
        t3['meter'] = f"{meter_id}_T3"
        theft_dfs.append(t3)
        
        # T4: Night-only usage — consumption only 10PM-6AM
        t4 = meter_data.copy()
        day_mask = t4['timestamp'].dt.hour.between(6, 21)
        t4.loc[day_mask, 'kwh'] = 0.0
        t4.loc[day_mask, 'current'] = t4.loc[day_mask, 'current'] * 0.02
        t4['label'] = 1
        t4['theft_type'] = 'T4_night_only'
        t4['meter'] = f"{meter_id}_T4"
        theft_dfs.append(t4)
        
        # T5: Voltage tampering — abnormally low voltage
        t5 = meter_data.copy()
        t5['voltage'] = t5['voltage'] * np.random.uniform(0.65, 0.80, len(t5))
        t5['kwh'] = t5['kwh'] * np.random.uniform(0.3, 0.6, len(t5))
        t5['label'] = 1
        t5['theft_type'] = 'T5_voltage_tamper'
        t5['meter'] = f"{meter_id}_T5"
        theft_dfs.append(t5)
        
        # T6: Current bypass — near-zero current with normal voltage
        t6 = meter_data.copy()
        bypass_mask = np.random.rand(len(t6)) > 0.3  # 70% of readings bypassed
        t6.loc[bypass_mask, 'current'] = t6.loc[bypass_mask, 'current'] * 0.03
        t6.loc[bypass_mask, 'kwh'] = t6.loc[bypass_mask, 'kwh'] * 0.05
        t6['label'] = 1
        t6['theft_type'] = 'T6_current_bypass'
        t6['meter'] = f"{meter_id}_T6"
        theft_dfs.append(t6)
        
        # T7: Random partial theft — random 30-70% reduction
        t7 = meter_data.copy()
        reduction = np.random.uniform(0.3, 0.7, len(t7))
        t7['kwh'] = t7['kwh'] * reduction
        t7['current'] = t7['current'] * reduction
        t7['label'] = 1
        t7['theft_type'] = 'T7_partial_theft'
        t7['meter'] = f"{meter_id}_T7"
        theft_dfs.append(t7)
    
    # Combine normal + theft
    all_theft = pd.concat(theft_dfs, ignore_index=True)
    combined = pd.concat([normal_df, all_theft], ignore_index=True)
    combined = combined.sort_values(['meter', 'timestamp']).reset_index(drop=True)
    
    print(f"Normal samples:  {len(normal_df):,}")
    print(f"Theft samples:   {len(all_theft):,}")
    print(f"Total combined:  {len(combined):,}")
    print(f"\nTheft type distribution:")
    print(combined['theft_type'].value_counts().to_string())
    
    return combined


# ─── STEP 3: Feature Engineering (47-Feature Pipeline) ──────────────────────

def engineer_features(df):
    """
    Engineer 47 features per consumer from hourly readings.
    Features grouped into:
      - Statistical (mean, std, min, max, skew, kurtosis) × 4 variables = 24
      - Temporal (hour patterns, day/night ratio, weekday/weekend) = 8
      - Ratio-based (zero_peak_ratio, bypass_ratio, flat_line_score, etc.) = 10
      - Rolling window (3-day, 7-day trends) = 5
    """
    print("\nEngineering 47 features per consumer...")
    
    feature_records = []
    meters = df['meter'].unique()
    
    for i, meter_id in enumerate(meters):
        if (i + 1) % 20 == 0:
            print(f"  Processing meter {i+1}/{len(meters)}...")
        
        m = df[df['meter'] == meter_id].copy()
        
        if len(m) < 24:  # Need at least 1 day
            continue
        
        label = m['label'].iloc[0]
        theft_type = m['theft_type'].iloc[0]
        m['hour'] = m['timestamp'].dt.hour
        m['dayofweek'] = m['timestamp'].dt.dayofweek
        
        features = {}
        
        # --- Statistical features (24) ---
        for col in ['kwh', 'voltage', 'current', 'frequency']:
            features[f'{col}_mean'] = m[col].mean()
            features[f'{col}_std'] = m[col].std()
            features[f'{col}_min'] = m[col].min()
            features[f'{col}_max'] = m[col].max()
            features[f'{col}_skew'] = m[col].skew()
            features[f'{col}_kurtosis'] = m[col].kurtosis()
        
        # --- Temporal features (8) ---
        peak_hours = m[m['hour'].between(8, 19)]
        off_peak = m[~m['hour'].between(8, 19)]
        
        features['peak_consumption_mean'] = peak_hours['kwh'].mean() if len(peak_hours) > 0 else 0
        features['offpeak_consumption_mean'] = off_peak['kwh'].mean() if len(off_peak) > 0 else 0
        features['night_day_ratio'] = (
            off_peak['kwh'].mean() / peak_hours['kwh'].mean()
            if len(peak_hours) > 0 and peak_hours['kwh'].mean() > 0 else 0
        )
        
        weekday = m[m['dayofweek'] < 5]
        weekend = m[m['dayofweek'] >= 5]
        features['weekday_mean'] = weekday['kwh'].mean() if len(weekday) > 0 else 0
        features['weekend_mean'] = weekend['kwh'].mean() if len(weekend) > 0 else 0
        features['weekday_weekend_ratio'] = (
            features['weekend_mean'] / features['weekday_mean']
            if features['weekday_mean'] > 0 else 0
        )
        
        # Hour-of-day consumption entropy
        hourly_dist = m.groupby('hour')['kwh'].mean()
        hourly_dist_norm = hourly_dist / hourly_dist.sum() if hourly_dist.sum() > 0 else hourly_dist
        hourly_dist_norm = hourly_dist_norm[hourly_dist_norm > 0]
        features['consumption_entropy'] = -(hourly_dist_norm * np.log2(hourly_dist_norm)).sum()
        
        # Peak hour concentration
        features['peak_concentration'] = (
            peak_hours['kwh'].sum() / m['kwh'].sum()
            if m['kwh'].sum() > 0 else 0
        )
        
        # --- Ratio-based features (10) ---
        # Zero peak ratio
        peak_zero = (peak_hours['kwh'] == 0).sum() if len(peak_hours) > 0 else 0
        features['zero_peak_ratio'] = peak_zero / len(peak_hours) if len(peak_hours) > 0 else 0
        
        # Bypass ratio (low current + normal voltage)
        if len(m) > 0:
            bypass = ((m['current'] < m['current'].quantile(0.1)) &
                      (m['voltage'] > m['voltage'].quantile(0.25))).sum()
            features['bypass_ratio'] = bypass / len(m)
        else:
            features['bypass_ratio'] = 0
        
        # Flat-line score
        unique_vals = m['kwh'].nunique()
        features['flat_line_score'] = 1.0 - (unique_vals / len(m)) if len(m) > 0 else 0
        
        # Coefficient of variation
        features['kwh_cv'] = m['kwh'].std() / m['kwh'].mean() if m['kwh'].mean() > 0 else 0
        features['voltage_cv'] = m['voltage'].std() / m['voltage'].mean() if m['voltage'].mean() > 0 else 0
        features['current_cv'] = m['current'].std() / m['current'].mean() if m['current'].mean() > 0 else 0
        
        # Voltage anomaly ratio (outside 190-260V)
        voltage_anomaly = ((m['voltage'] < 190) | (m['voltage'] > 260)).sum()
        features['voltage_anomaly_ratio'] = voltage_anomaly / len(m) if len(m) > 0 else 0
        
        # Frequency deviation ratio (outside 49.5-50.5Hz)
        freq_anomaly = ((m['frequency'] < 49.5) | (m['frequency'] > 50.5)).sum()
        features['freq_anomaly_ratio'] = freq_anomaly / len(m) if len(m) > 0 else 0
        
        # Zero consumption ratio (all hours)
        features['zero_consumption_ratio'] = (m['kwh'] == 0).sum() / len(m) if len(m) > 0 else 0
        
        # Max consecutive zeros
        is_zero = (m['kwh'] == 0).astype(int).values
        max_consec_zero = 0
        curr_count = 0
        for val in is_zero:
            if val == 1:
                curr_count += 1
                max_consec_zero = max(max_consec_zero, curr_count)
            else:
                curr_count = 0
        features['max_consecutive_zeros'] = max_consec_zero
        
        # --- Rolling window features (5) ---
        daily = m.groupby(m['timestamp'].dt.date)['kwh'].sum()
        
        if len(daily) >= 3:
            features['rolling_3d_mean'] = daily.rolling(3).mean().mean()
            features['rolling_3d_std'] = daily.rolling(3).std().mean()
        else:
            features['rolling_3d_mean'] = daily.mean()
            features['rolling_3d_std'] = 0
        
        if len(daily) >= 7:
            features['rolling_7d_mean'] = daily.rolling(7).mean().mean()
            features['rolling_7d_std'] = daily.rolling(7).std().mean()
            features['rolling_7d_trend'] = np.polyfit(range(min(len(daily), 30)), daily.values[:30], 1)[0] if len(daily) >= 7 else 0
        else:
            features['rolling_7d_mean'] = daily.mean()
            features['rolling_7d_std'] = 0
            features['rolling_7d_trend'] = 0
        
        features['label'] = label
        features['theft_type'] = theft_type
        features['meter'] = meter_id
        
        feature_records.append(features)
    
    feature_df = pd.DataFrame(feature_records)
    
    # Fill NaN with 0
    numeric_cols = feature_df.select_dtypes(include=[np.number]).columns
    feature_df[numeric_cols] = feature_df[numeric_cols].fillna(0)
    
    # Replace inf with large values
    feature_df = feature_df.replace([np.inf, -np.inf], 0)
    
    print(f"Engineered {len(feature_df.columns) - 3} features for {len(feature_df)} consumer profiles")
    return feature_df


# ─── STEP 4: Apply SMOTE ────────────────────────────────────────────────────

def apply_smote(feature_df):
    """Apply SMOTE to balance normal vs theft classes."""
    print("\nApplying SMOTE for class balancing...")
    
    exclude_cols = ['label', 'theft_type', 'meter']
    feature_cols = [c for c in feature_df.columns if c not in exclude_cols]
    
    X = feature_df[feature_cols].values
    y = feature_df['label'].values
    
    print(f"Before SMOTE — Normal: {(y == 0).sum()}, Theft: {(y == 1).sum()}")
    
    smote = SMOTE(random_state=42, k_neighbors=min(5, (y == 0).sum() - 1))
    X_resampled, y_resampled = smote.fit_resample(X, y)
    
    print(f"After SMOTE  — Normal: {(y_resampled == 0).sum()}, Theft: {(y_resampled == 1).sum()}")
    
    resampled_df = pd.DataFrame(X_resampled, columns=feature_cols)
    resampled_df['label'] = y_resampled
    
    return resampled_df, feature_cols


# ─── MAIN ───────────────────────────────────────────────────────────────────

def main():
    output_dir = "processed_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Load CEEW data
    hourly = load_ceew_data(data_dir="data", sample_meters=20)
    if hourly is None:
        return
    
    # Save hourly aggregated data
    hourly_path = os.path.join(output_dir, "ceew_hourly_aggregated.csv")
    hourly.to_csv(hourly_path, index=False)
    print(f"\nHourly aggregated data saved to {hourly_path}")
    
    # Step 2: Inject theft profiles
    combined = inject_theft_profiles(hourly)
    
    # Step 3: Engineer features
    feature_df = engineer_features(combined)
    
    # Save pre-SMOTE features
    pre_smote_path = os.path.join(output_dir, "ceew_features_pre_smote.csv")
    feature_df.to_csv(pre_smote_path, index=False)
    print(f"\nPre-SMOTE features saved to {pre_smote_path}")
    
    # Step 4: Apply SMOTE
    resampled_df, feature_cols = apply_smote(feature_df)
    
    # Save SMOTE-balanced dataset
    smote_path = os.path.join(output_dir, "ceew_features_smote_balanced.csv")
    resampled_df.to_csv(smote_path, index=False)
    print(f"SMOTE-balanced features saved to {smote_path}")
    
    # Save feature column names for model training
    joblib.dump(feature_cols, os.path.join(output_dir, "feature_columns.pkl"))
    
    print("\n" + "=" * 60)
    print("CEEW PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Feature count:   {len(feature_cols)}")
    print(f"Feature names:   {feature_cols}")
    print(f"\nOutput files in '{output_dir}/':")
    print(f"  1. ceew_hourly_aggregated.csv     — Cleaned hourly data")
    print(f"  2. ceew_features_pre_smote.csv    — 47 features per consumer")
    print(f"  3. ceew_features_smote_balanced.csv — SMOTE-balanced dataset")
    print(f"  4. feature_columns.pkl            — Feature column names")


if __name__ == "__main__":
    main()
