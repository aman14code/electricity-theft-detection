# Master Prompt for Claude: Corrected Research Paper

## Context
You are rewriting an IEEE-format research paper for electricity theft detection using Indian smart grid data. The paper has been reviewed and has multiple issues that must be fixed before submission. Below is every piece of raw data you need.

---

## 1. CORRECT AUTHOR BLOCK (MUST USE THIS)

**Authors:** Keshav Aggarwal, Aman Sharma, Abhinav Saini  
**Supervisor:** Ashu Singh  
**Affiliation:** Department of Computer Science & Engineering, Meerut Institute of Engineering & Technology (MIET), Meerut, Uttar Pradesh, India  

> ⚠️ DO NOT use "PowerGuard AMI Research Initiative", "powerguard-ai.org", or "New Delhi". These are INVENTED and INCORRECT.

---

## 2. ACTUAL FEATURE LIST (47 Features from Code)

The features are computed per consumer profile in `step1_ceew_theft_injection.py`, function `engineer_features()`.

### Statistical Features (24) — 6 stats × 4 variables
For each of `kwh`, `voltage`, `current`, `frequency`:
- `{var}_mean`, `{var}_std`, `{var}_min`, `{var}_max`, `{var}_skew`, `{var}_kurtosis`

Full list: `kwh_mean`, `kwh_std`, `kwh_min`, `kwh_max`, `kwh_skew`, `kwh_kurtosis`, `voltage_mean`, `voltage_std`, `voltage_min`, `voltage_max`, `voltage_skew`, `voltage_kurtosis`, `current_mean`, `current_std`, `current_min`, `current_max`, `current_skew`, `current_kurtosis`, `frequency_mean`, `frequency_std`, `frequency_min`, `frequency_max`, `frequency_skew`, `frequency_kurtosis`

### Temporal Features (8)
- `peak_consumption_mean` — mean kWh during 8AM-7PM
- `offpeak_consumption_mean` — mean kWh during 8PM-7AM
- `night_day_ratio` — offpeak_mean / peak_mean
- `weekday_mean` — mean kWh on weekdays (Mon-Fri)
- `weekend_mean` — mean kWh on weekends (Sat-Sun)
- `weekday_weekend_ratio` — weekend_mean / weekday_mean
- `consumption_entropy` — Shannon entropy of hourly consumption distribution
- `peak_concentration` — fraction of total kWh consumed during peak hours

### Ratio-Based Features (10)
- `zero_peak_ratio` — fraction of peak hours with zero consumption
- `bypass_ratio` — fraction of readings with low current (<10th percentile) AND normal voltage (>25th percentile)
- `flat_line_score` — 1 - (unique_kwh_values / total_readings)
- `kwh_cv` — coefficient of variation for kWh
- `voltage_cv` — coefficient of variation for voltage
- `current_cv` — coefficient of variation for current
- `voltage_anomaly_ratio` — fraction of readings with voltage outside 190-260V
- `freq_anomaly_ratio` — fraction of readings with frequency outside 49.5-50.5Hz
- `zero_consumption_ratio` — fraction of all readings with zero kWh
- `max_consecutive_zeros` — longest run of consecutive zero-kWh readings

### Rolling Window Features (5)
- `rolling_3d_mean` — mean of 3-day rolling daily kWh sum
- `rolling_3d_std` — std of 3-day rolling daily kWh sum
- `rolling_7d_mean` — mean of 7-day rolling daily kWh sum
- `rolling_7d_std` — std of 7-day rolling daily kWh sum
- `rolling_7d_trend` — linear regression slope of first 30 daily sums

### ⚠️ TABLE II CORRECTIONS NEEDED
The current Table II in the paper lists features that DO NOT exist in the code:
- ❌ Shannon entropy (not computed — `consumption_entropy` is computed but it's Shannon entropy of hourly distribution, which is valid)
- ❌ CUSUM change-point count — NOT in code
- ❌ Apparent vs active power discrepancy — NOT in code (no apparent power computed)
- ❌ Power factor cos(φ) — NOT in code
- ❌ Feeder baseline deviation — NOT in code
- ❌ Voltage sag count — NOT in code (only `voltage_anomaly_ratio`)
- ❌ Current-to-consumption divergence — NOT in code  
- ❌ Lag-1/7/24 autocorrelation — NOT in code
- ❌ Zero-crossing rate — NOT in code
- ❌ Signal energy — NOT in code
- ❌ First-order difference variance — NOT in code
- ❌ Peak-to-Average Ratio (PAR) — NOT in code (but `peak_concentration` is similar)
- ❌ Diurnal index — NOT in code

Replace Table II with the ACTUAL 47 features listed above organized as:
- Statistical (24): 6 stats × 4 variables  
- Temporal (8): peak/offpeak means, ratios, entropy, concentration
- Ratio-based (10): zero ratios, bypass, flat-line, CVs, anomaly ratios, consecutive zeros
- Rolling Window (5): 3d/7d means, stds, trend

Also fix the "harmonic" claim in contributions — there are NO harmonic features.

---

## 3. T1–T7 ATTACK INJECTION CODE (Exact from step1)

```python
# T1: Peak-hour bypass — zero consumption during 8AM-8PM
peak_mask = t1['timestamp'].dt.hour.between(8, 19)
t1.loc[peak_mask, 'kwh'] = 0.0
t1.loc[peak_mask, 'current'] = t1.loc[peak_mask, 'current'] * 0.05

# T2: Flat-line spoofing — constant consumption
flat_val = meter_data['kwh'].median() * 0.3
t2['kwh'] = flat_val

# T3: Gradual consumption drop — slow decline over time
decay = np.linspace(1.0, 0.15, n)
t3['kwh'] = t3['kwh'] * decay
t3['current'] = t3['current'] * decay

# T4: Night-only usage — consumption only 10PM-6AM
day_mask = t4['timestamp'].dt.hour.between(6, 21)
t4.loc[day_mask, 'kwh'] = 0.0
t4.loc[day_mask, 'current'] = t4.loc[day_mask, 'current'] * 0.02

# T5: Voltage tampering — abnormally low voltage
t5['voltage'] = t5['voltage'] * np.random.uniform(0.65, 0.80, len(t5))
t5['kwh'] = t5['kwh'] * np.random.uniform(0.3, 0.6, len(t5))

# T6: Current bypass — near-zero current with normal voltage
bypass_mask = np.random.rand(len(t6)) > 0.3  # 70% of readings bypassed
t6.loc[bypass_mask, 'current'] = t6.loc[bypass_mask, 'current'] * 0.03
t6.loc[bypass_mask, 'kwh'] = t6.loc[bypass_mask, 'kwh'] * 0.05

# T7: Random partial theft — random 30-70% reduction
reduction = np.random.uniform(0.3, 0.7, len(t7))
t7['kwh'] = t7['kwh'] * reduction
t7['current'] = t7['current'] * reduction
```

### ⚠️ T1–T7 FRAMING CORRECTIONS
- These are **author-defined** attack profiles **inspired by** prior NTL attack taxonomies [4], [15]
- Do NOT claim they are "IEEE-aligned" or "IEEE mathematical theft injection profiles" or "peer-reviewed IEEE mathematical theft injection profiles"
- Do NOT cite [10] and [11] as validation that synthetic labels are established practice
- Correct framing: "We define seven synthetic attack profiles (T1–T7) inspired by established NTL attack taxonomies in the literature [4], [15]"
- Note: `T2` uses `median * 0.3` not `min(x)` — the LaTeX formula says `min(x)` but code says `median * 0.3`

---

## 4. MODEL ARCHITECTURES (Exact from step2)

### Random Forest
```python
RandomForestClassifier(
    n_estimators=500, max_depth=25, min_samples_split=5,
    class_weight='balanced', random_state=42, n_jobs=-1
)
```

### XGBoost
```python
xgb.XGBClassifier(
    n_estimators=300, max_depth=8, learning_rate=0.05,
    scale_pos_weight=neg/pos, random_state=42,
    use_label_encoder=False, eval_metric='logloss',
    subsample=0.8, colsample_bytree=0.8
)
```

### DNN (4-layer, NOT "three hidden layers")
```python
Sequential([
    Dense(256, activation='relu', input_shape=(n_features,)),
    BatchNormalization(),
    Dropout(0.3),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])
# Optimizer: Adam(lr=0.001), Loss: binary_crossentropy
# EarlyStopping(patience=10), class_weight applied
# Epochs: 100, Batch: 32, validation_split: 0.15
```
Architecture: 256→128→64→32→1, 4 hidden layers, dropout 0.3/0.3/0.2/0.2, BatchNorm on first 3 layers.

### LSTM
```python
Sequential([
    LSTM(128, return_sequences=True, input_shape=(n_features, 1)),
    Dropout(0.3),
    LSTM(64, return_sequences=False),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])
# Optimizer: Adam(lr=0.001), Epochs: 50, Batch: 32
# Input reshape: (samples, features, 1) — each feature treated as a timestep
```
⚠️ Note: The LSTM treats each of the 47 features as a "timestep" — this is a non-standard use. It should be noted as a limitation.

### Isolation Forest
```python
IsolationForest(n_estimators=300, contamination=0.1, random_state=42, n_jobs=-1)
```

### 1D-CNN Benchmark (step5, Dataset C only)
```python
Sequential([
    Conv1D(64, kernel_size=7, activation='relu', input_shape=(1034, 1)),
    BatchNormalization(), MaxPooling1D(2), Dropout(0.3),
    Conv1D(128, kernel_size=5, activation='relu'),
    BatchNormalization(), MaxPooling1D(2), Dropout(0.3),
    Conv1D(64, kernel_size=3, activation='relu'),
    BatchNormalization(), MaxPooling1D(2), Dropout(0.3),
    Flatten(),
    Dense(128, activation='relu'), Dropout(0.4),
    Dense(64, activation='relu'), Dropout(0.2),
    Dense(1, activation='sigmoid')
])
# Optimizer: Adam(lr=0.0005), Epochs: 100, Batch: 16
# Input: raw 1034-day consumption reshaped to (1034, 1)
```

### Soft-Voting Ensemble
```python
# Combines RF, XGBoost, DNN, LSTM (excludes Isolation Forest)
# Weights: proportional to each model's individual F1 score
weights = [results[k].get('f1', 0.5) for k in supervised_probs.keys()]
weighted_sum = sum(prob * w for prob, w in zip(probabilities, weights))
avg_prob = weighted_sum / sum(weights)
prediction = (avg_prob >= 0.5).astype(int)
```

---

## 5. COMPLETE RESULTS DATA

### model_comparison.csv (Tables III, IV, V)
```
Dataset,Model,accuracy,precision,recall,f1,auc_roc
CEEW,Random Forest,1.0,1.0,1.0,1.0,1.0
CEEW,XGBoost,1.0,1.0,1.0,1.0,1.0
CEEW,DNN,0.9688,1.0,0.9643,0.9818,0.9911
CEEW,LSTM,0.9062,0.963,0.9286,0.9455,0.9196
CEEW,Isolation Forest,0.1562,1.0,0.0357,0.069,0.6429
CEEW,Soft-Voting Ensemble,0.9688,1.0,0.9643,0.9818,1.0
SmartMeter,Random Forest,0.986,0.95,0.76,0.8444,0.9987
SmartMeter,XGBoost,0.99,0.8448,0.98,0.9074,0.9979
SmartMeter,DNN,0.949,0.4949,0.98,0.6577,0.9913
SmartMeter,LSTM,0.891,0.2435,0.56,0.3394,0.8777
SmartMeter,Isolation Forest,0.915,0.3196,0.62,0.4218,0.9256
SmartMeter,Soft-Voting Ensemble,0.991,0.8475,1.0,0.9174,0.9982
GitHub,Random Forest,0.7436,0.7778,0.7,0.7368,0.8026
GitHub,XGBoost,0.8205,0.8421,0.8,0.8205,0.7763
GitHub,DNN,0.6154,0.619,0.65,0.6341,0.7368
GitHub,LSTM,0.4872,0.5,0.55,0.5238,0.5316
GitHub,Isolation Forest,0.4872,0.5,0.1,0.1667,0.5605
GitHub,Soft-Voting Ensemble,0.7436,0.75,0.75,0.75,0.7763
```

### cv_results.json (Cross-Validation)
```json
{
  "CEEW_Random_Forest": {
    "folds_f1": [0.9492, 0.9492, 1.0, 1.0, 0.963],
    "mean_f1": 0.9723,
    "sample_sd_f1": 0.0259,
    "pop_sd_f1": 0.0232,
    "mean_acc": 0.95,
    "sample_sd_acc": 0.0474
  },
  "CEEW_XGBoost": {
    "folds_f1": [0.9655, 0.9643, 1.0, 1.0, 0.9825],
    "mean_f1": 0.9825,
    "sample_sd_f1": 0.0176,
    "pop_sd_f1": 0.0157,
    "mean_acc": 0.9688,
    "sample_sd_acc": 0.0312
  },
  "SmartMeter_Random_Forest": {
    "folds_f1": [0.9278, 0.8636, 0.875, 0.8172, 0.8696],
    "mean_f1": 0.8706,
    "sample_sd_f1": 0.0394,
    "pop_sd_f1": 0.0352,
    "mean_acc": 0.988,
    "sample_sd_acc": 0.0035
  },
  "SmartMeter_XGBoost": {
    "folds_f1": [0.9259, 0.8952, 0.8868, 0.9126, 0.8932],
    "mean_f1": 0.9028,
    "sample_sd_f1": 0.0161,
    "pop_sd_f1": 0.0144,
    "mean_acc": 0.9898,
    "sample_sd_acc": 0.0016
  },
  "GitHub_XGBoost": {
    "folds_f1": [0.7317, 0.7027, 0.7027, 0.8, 0.625],
    "mean_f1": 0.7124,
    "sample_sd_f1": 0.063,
    "pop_sd_f1": 0.0563,
    "mean_acc": 0.7225,
    "sample_sd_acc": 0.0396
  }
}
```

### Table VI: Confusion Matrix Breakdown
- **CEEW Holdout (32 profiles: 4 normal, 28 theft):** TN=4, FP=0, FN=1, TP=27
  - Honest Recall: 100%, Theft Recall: 96.43%, Precision: 100%
- **SmartMeter Holdout (1000 records: 950 normal, 50 theft):** TN=941, FP=9, FN=0, TP=50
  - Honest Recall: 99.05%, Theft Recall: 100%, Precision: 84.75% (50/59)

---

## 6. DATASET DETAILS

### Dataset A: CEEW
- Source: Kaggle (jehanbhathena) — CEEW Smart Meter Data from Mathura & Bareilly, UP, India
- Raw: 3-minute interval telemetry (kWh, Voltage, Current, Frequency, Meter ID)
- Processing: Aggregated to hourly → 235,547 hourly records from 20 sampled meters
- After theft injection: 20 honest + 140 theft = 160 consumer profiles
- Split: GroupShuffleSplit by base meter ID (80:20 → 16 train meters, 4 test meters)
- Test set: 32 profiles (4 honest, 28 theft) from 4 unseen physical meters
- SMOTE: Applied to training set ONLY after split
- Labels: SYNTHETIC (T1-T7 attack injection). NOT real utility-inspected theft labels.

### Dataset B: Smart Meter + Weather
- Source: Kaggle (ziya07) — 5,000 half-hourly records with weather
- Columns: Timestamp, Electricity_Consumed, Temperature, Humidity, Wind_Speed, Avg_Past_Consumption, Anomaly_Label
- All values appear to be pre-normalized (0-1 range)
- Labels: "Normal" (4750) and "Abnormal" (250) — 5% anomaly rate
- Split: 80:20 stratified → 4000 train, 1000 test (950 normal, 50 abnormal)
- No SMOTE applied — class_weight and scale_pos_weight used instead
- ⚠️ ISSUE: Labels may be tied to `Avg_Past_Consumption` (consumption deviation). The split is random hourly, not grouped by consumer.

### Dataset C: External Benchmark (SGCC-derived)
- Source: GitHub repo vaishnavi-1/Electricity-theft-detection-using-ML, subfolder fraud-detection-CNN
- Originally from SGCC (State Grid Corporation of China) 
- 191 consumers (97 fraud FLAG=1, 94 honest FLAG=0) — 9 dropped from original 200 due to >50% missing
- 1034 daily consumption features (dates: 2014-01-01 to 2016-10-31)
- Split: 80:20 stratified → 152 train, 39 test (19 normal, 20 fraud)
- No SMOTE applied — scale_pos_weight used
- ⚠️ TIMELINE: Paper says "1,036" days but actual columns = 1034. Fix to 1034.

---

## 7. STALE / FAKE FIGURES THAT NEED FIXING

### Figures from `generate_extra_graphs.py` — ALL USING FAKE DATA
These scripts generate figures with HARDCODED numbers that don't match real results:

1. **fig1_class_imbalance.png** — Uses SGCC numbers (38757 genuine, 3615 theft). Should show CEEW distribution (20 honest, 140 theft profiles). Title says "SGCC Dataset" but paper uses CEEW.

2. **fig2_smote_impact.png** — Uses SGCC numbers (38757→38757). Should show CEEW: Pre-SMOTE on training fold (~16 honest, ~112 theft) → Post-SMOTE (~112/112). The exact numbers depend on which meters land in train.

3. **fig4_feature_importance.png** — Uses FAKE feature names (`anom_zero_day_count`, `meta_baseline_kwh`, `stat_cv`). Real SHAP plots exist at `model_results/plots/shap_CEEW_XGBoost.png` — USE THOSE.

4. **fig5_cross_validation.png** — Uses FAKE accuracy values (~87-90%). Real values from cv_results.json are 95-97% for CEEW, 98.8-99% for SmartMeter, 72% for GitHub.

5. **fig7_radar_chart.png** — Uses FAKE values (accuracy ~0.85-0.90, F1 ~0.36-0.42). Real values are completely different per dataset.

6. **fig6_pr_curves.png** — Uses APPROXIMATED PR curves, not real data. The `approx_pr` function generates fake curves.

7. **confusion_matrix.png** — Uses FAKE matrix [7302,450; 408,315]. Real confusion matrices exist at `model_results/plots/cm_*.png`.

### Real figures that exist (use these):
- `model_results/plots/shap_CEEW_XGBoost.png` — Real CEEW SHAP
- `model_results/plots/shap_SmartMeter_XGBoost.png` — Real SmartMeter SHAP
- `model_results/plots/shap_GitHub_XGBoost.png` — Real GitHub SHAP
- `paper_graphs/real_roc_curve_CEEW.png` — Real CEEW ROC
- `paper_graphs/real_roc_curve_SmartMeter.png` — Real SmartMeter ROC
- `paper_graphs/real_roc_curve_GitHub.png` — Real GitHub ROC
- `model_results/plots/cm_CEEW_Soft_Voting_Ensemble.png` — Real CEEW confusion matrix
- `model_results/plots/cm_SmartMeter_Soft_Voting_Ensemble.png` — Real SmartMeter confusion matrix
- `paper_graphs/benchmark_cnn_vs_xgboost.png` — Real CNN vs XGBoost ROC
- `paper_graphs/publication_model_comparison.png` — Real SmartMeter bar chart (from model_comparison.csv)

---

## 8. COMPLETE CORRECTIONS CHECKLIST

### MUST FIX (Paper will be rejected without these)

- [ ] **Author block**: Restore Keshav Aggarwal, Aman Sharma, Abhinav Saini, supervisor Ashu Singh, MIET Meerut. Delete PowerGuard/New Delhi/powerguard-ai.org.

- [ ] **Table II features**: Replace with actual 47 features from code (see section 2 above). Remove all phantom features (CUSUM, power factor, apparent power, etc.).

- [ ] **Remove "harmonic" from contributions**: No harmonic features exist. Say "statistical, temporal, ratio-based, and rolling-window features".

- [ ] **T1-T7 framing**: Reframe as "author-defined profiles inspired by [4], [15]". Drop claims of "IEEE-aligned" or "peer-reviewed IEEE mathematical". Fix T2 formula (code uses `median*0.3`, paper says `min(x)`).

- [ ] **Section IV-D false claim**: Remove "maintains strong discrimination (>0.82) on the external benchmark". Ensemble AUC on Dataset C is 0.7763 and F1 is 0.75. Write honestly: "Performance degrades on Dataset C, suggesting that models trained on synthetic theft profiles face a domain gap when evaluated on real utility inspection labels."

- [ ] **Section IV-G top predictors**: Update to match actual SHAP features. From the CEEW SHAP plots, the top predictors are features like `flat_line_score`, `peak_consumption_mean`, `night_day_ratio`, `zero_peak_ratio`, `bypass_ratio` (features designed to capture T1, T2, T4). Remove "voltage sag count" and "apparent-active power divergence" since they don't exist. Remove "legally defensible".

- [ ] **Unsupported claims**: 
  - Remove or source "$96 billion" (needs a citation or remove)
  - Remove or source "AT&C 15-22%" (needs a citation or remove)  
  - Remove "Indian DISCOMs don't release audit logs" (unverifiable)
  - Remove "$25-$50 per inspection" (unsourced)
  - Delete the unused cost formula in Section IV-E (it's never applied to actual data)

- [ ] **DNN architecture**: Paper says "three hidden layers, dropout 0.4". Code has 4 hidden layers (256→128→64→32), dropout 0.3/0.3/0.2/0.2 with BatchNorm on first 3.

- [ ] **CNN comparison (Section IV-F)**: CNN AUC is higher than XGBoost on Dataset C (from the ROC plot). Report both accurately. Don't claim 39 test consumers "confirm an optimal paradigm". Note the test set is small (39 consumers).

- [ ] **Remove "Leaflet GIS"** from contributions unless the dashboard actually uses Leaflet (check README).

- [ ] **Dataset C timeline**: Fix "1,036 days" to "1,034 daily features" (actual column count).

- [ ] **Abstract length**: Currently ~370 words. IEEE typically wants ≤250. Shorten significantly.

### SHOULD FIX (Improves paper quality)

- [ ] **SD convention**: Pick one convention (sample SD, ddof=1) and use consistently. Currently mixes sample and population SD.

- [ ] **Add limitations for Dataset B**: Note that the split is random hourly (not grouped by consumer), and that labels may be algorithmically generated based on consumption deviation.

- [ ] **Note LSTM limitation**: LSTM treats 47 features as "timesteps" — this is non-standard for tabular data.

- [ ] **Report Isolation Forest, DNN issues**: DNN precision on Dataset B is 0.4949 (near random). LSTM near-chance on Dataset C (AUC 0.5316). Isolation Forest has 0.1562 accuracy on CEEW. Add brief narrative acknowledging these.

- [ ] **CEEW ROC quantization**: The CEEW ROC is quantized because there are only 4 honest (negative) test samples. Note this.

- [ ] **Confidence intervals**: Note that confidence intervals are not reported and test sets are small (32 profiles for CEEW, 39 for GitHub).

- [ ] **Soften language**: "Superior operational stability" → "higher stability". "Superior detection accuracy" → "higher detection accuracy".

- [ ] **Remove unused references**: [12], [20]-[25], [27], [34], [35] may not be cited in the text. Verify and clean up.

- [ ] **Fix [13] citation**: [13] cites Li et al. for TreeSHAP but TreeSHAP is Lundberg [33]. Verify all SHAP references point to [33].

- [ ] **Dashboard claims**: Describe as "heuristic-first detection engine with optional trained model" and note the dashboard/heuristic engine was not quantitatively evaluated in this paper.

### FIGURES TO REGENERATE
The following figures need to be regenerated with real data (not hardcoded fake numbers):
1. Fig. 1 (class imbalance) — use CEEW actual distribution
2. Fig. 3 (SMOTE) — use CEEW training fold actual distributions  
3. Fig. 4 (feature importance) — use real SHAP from `model_results/plots/shap_CEEW_XGBoost.png`
4. Fig. 5 (CV stability) — use real cv_results.json values
5. Fig. 6 (radar chart) — use real model_comparison.csv values
6. Fig. 10 (PR curves) — need real PR curve data or remove

---

## 9. SPLIT METHODOLOGY (Verified Correct)

### Dataset A (CEEW):
```python
# GroupShuffleSplit by base meter ID (strips _T1, _T2, etc.)
groups = df['meter'].apply(lambda x: str(x).split('_')[0]).values
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=groups))
# Scaler fit on train only
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train_raw)
X_test = scaler.transform(X_test_raw)
# SMOTE on train only
smote = SMOTE(random_state=42, k_neighbors=k)
X_train, y_train = smote.fit_resample(X_train, y_train)
```

### Dataset B (SmartMeter):
```python
# Simple stratified split (no grouping by consumer — potential issue)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
# No SMOTE — uses class_weight and scale_pos_weight instead
```

### Dataset C (GitHub):
```python
# Stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
# No SMOTE — uses scale_pos_weight
```

---

## 10. DATASET B FEATURE ENGINEERING (from step2)
```python
# Engineered features on top of raw columns:
df['Hour'] = df['Timestamp'].dt.hour
df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
df['IsPeak'] = df['Hour'].between(8, 20).astype(int)
df['Consumption_Deviation'] = df['Electricity_Consumed'] - df['Avg_Past_Consumption']
df['Consumption_Ratio'] = df['Electricity_Consumed'] / (df['Avg_Past_Consumption'] + 1e-6)
df['Temp_Consumption'] = df['Temperature'] * df['Electricity_Consumed']
df['Humidity_Consumption'] = df['Humidity'] * df['Electricity_Consumed']

feature_cols = ['Electricity_Consumed', 'Temperature', 'Humidity', 'Wind_Speed',
                'Avg_Past_Consumption', 'Hour', 'DayOfWeek', 'IsWeekend', 'IsPeak',
                'Consumption_Deviation', 'Consumption_Ratio', 'Temp_Consumption',
                'Humidity_Consumption']  # 13 features total
```

---

## 11. SEEDS AND REPRODUCIBILITY
- `np.random.seed(42)` and `tf.random.set_seed(42)` used throughout
- `random_state=42` on all sklearn/xgboost models and splits
- EarlyStopping with `restore_best_weights=True`

## 12. CROSS-VALIDATION METHODOLOGY
- **CEEW**: 5-fold GroupKFold by base meter ID, SMOTE per fold on training split only
- **SmartMeter**: 5-fold StratifiedKFold, no SMOTE (uses scale_pos_weight=4750/250)
- **GitHub**: 5-fold StratifiedKFold with scale_pos_weight=neg/pos

---

## INSTRUCTIONS FOR CLAUDE

Using ALL the data above, rewrite the complete research paper (`research_paper_complete.md`) fixing every item in the corrections checklist. The paper should:

1. Use the CORRECT author block
2. Have an abstract ≤250 words
3. Have Table II matching the ACTUAL 47 features
4. Frame T1-T7 correctly as author-defined
5. Report all results HONESTLY including where models fail
6. Note all limitations including synthetic labels, small test sets, LSTM misuse
7. Use sample SD (ddof=1) consistently
8. Remove all unsupported macro-economic claims or properly cite them
9. Remove phantom features and methods not in the code
10. Keep IEEE formatting conventions
