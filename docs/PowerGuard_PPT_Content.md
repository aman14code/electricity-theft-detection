# POWERGUARD: Deep Dive Presentation Content

This document contains the exact slide-by-slide text content of the PowerGuard Deep Dive Presentation.

---

## PAGE 1: TITLE SLIDE
**POWERGUARD**
Electricity Theft Detection System
Complete Deep Dive Study Guide

**Key Stats:**
- 8 Detection Factors
- 5 ML Models
- 47+ Engineered Features
- 4 Microservices

*ML + Heuristic Hybrid | SGCC Dataset | Ensemble Strategy | SHAP Explainability*

---

## PAGE 2: THE PROBLEM - Electricity Theft

**Non-Technical Loss (NTL)**
- India loses ~₹1.5 lakh crore/year to theft
- Globally: $96 billion problem
- 20-25% of total electricity generated is stolen

**Why Can't Humans Find It?**
- Manual inspection covers only 2-5% of meters/year
- Skilled thieves make it visually undetectable
- Inspections cost ₹500-2000 per visit
- Data spoofing leaves zero physical evidence

**Our Solution**
- Use smart meter telemetry data (already being collected)
- 6 dimensions: consumption, voltage, current, power factor, frequency, tamper
- ML + rule-based heuristics to find anomalies
- Explainable results operators can act on

---

## PAGE 3: THE 6 INPUT DIMENSIONS

1. **Consumption (kWh):** 0.5-20 (How much electricity consumed)
2. **Voltage (Volts):** 190-250V (Electrical pressure in line)
3. **Current (Amps):** 0.5-30A (Flow of electrons through meter)
4. **Power Factor (0-1):** 0.85-1.0 (Real/Apparent power ratio)
5. **Frequency (Hz):** 49.5-50.5 (Grid oscillation rate)
6. **Tamper Flag (Bool):** false (Hardware sensor trigger)

*Note: Different theft techniques disturb different dimensions — that's why we analyze all 6 together.*

---

## PAGE 4: THE 8 DETECTION FACTORS (Overview)

1. **Consumption Drop [25% weight]:** Meter bypass during daytime
2. **Tamper Detection [20% weight]:** Physical hardware tampering
3. **Current Anomaly [15% weight]:** Current shunted around meter
4. **Voltage Anomaly [10% weight]:** Voltage manipulation
5. **Power Factor [10% weight]:** Load manipulation via capacitors
6. **Pattern Irregularity [10% weight]:** Day/night inversion, chaos
7. **Frequency Deviation [5% weight]:** Illegal grid tapping
8. **Flat-line Detection [5% weight]:** Spoofed/replayed data

*Note: Each factor scores 0.0 (clean) to 1.0 (theft). Combined via weighted average + boosting logic.*

---

## PAGE 5: FACTOR 1 - Consumption Drop [25%]

**What it detects:** Meter bypass during daytime hours.

**The Physics / Logic:**
- Zero kWh during 8AM-8PM is impossible.
- People use ACs, fridges, lights during the day.
- Zero during peak hours = bypassed meter.
- Also checks: avg < 30% of baseline.

**Algorithm:**
- Filter to peak hours (8AM-8PM)
- Count zero-kWh readings
- Score = min(1.0, (zeros/total) x 5)
- If avg < 30% baseline -> floor at 0.7
- x5 multiplier: 20% zeros = score 1.0

*Why 25% weight? Strongest single indicator. Appears in 70%+ of confirmed theft cases.*

---

## PAGE 6: FACTOR 2 - Current Anomaly [15%]

**What it detects:** Physical meter bypass (current shunted around meter).

**The Physics / Logic:**
- Ohm's Law: P = V x I
- If voltage=220V, current=0.05A, but consumption>0
- -> Physically IMPOSSIBLE without bypass
- Current must flow through bypass wire

**Algorithm:**
- Find: current<0.1A AND voltage>200V AND consumption>0
- Score = min(1.0, (count/total) x 4)
- Zero current + consumption>0.5 -> x8 boost
- Violates basic electrical physics

*Why 15% weight? Physics-based signal. Very hard to fake or explain away. Less common than consumption drops.*

---

## PAGE 7: FACTOR 3 - Tamper Detection [20%]

**What it detects:** Physical tampering with meter hardware.

**The Physics / Logic:**
- Smart meters have accelerometers, reed switches, case-open detectors.
- Physical opening/shaking/magnet -> tamper flag.
- Consecutive flags = sustained tampering.
- Random faults are isolated (1-2 flags).

**Algorithm:**
- Score = min(1.0, tamper_ratio x 10)
- -> 10% tamper rate = score 1.0
- Consecutive check:
- 5+ consecutive flags -> score 0.9 (deliberate, not random noise)

*Why 20% weight? Physical hardware signal. Very reliable but can have false positives (storms, accidents).*

---

## PAGE 8: FACTOR 4 - Voltage Anomaly [10%]

**What it detects:** Voltage manipulation to reduce metered consumption.

**The Physics / Logic:**
- Thieves use "voltage divider" devices.
- Energy = V x I x t
- Lower voltage = lower recorded consumption.
- Safe band: 190V-250V (India standard).
- Extreme (<170V or >270V) = deliberate.

**Algorithm:**
- Count readings outside 190-250V
- Score = min(1.0, (outliers/total) x 3)
- Extreme voltage (<170V or >270V):
- 5x multiplier (deliberate manipulation) vs grid fluctuation

*Why 10% weight? Voltage issues CAN be legitimate (grid problems during monsoon). Weighted lower for this reason.*

---

## PAGE 9: FACTOR 5 - Power Factor [10%]

**What it detects:** Load manipulation using capacitor banks.

**The Physics / Logic:**
- PF = Real Power / Apparent Power
- PF=1.0: perfect efficiency
- PF=0.3: 70% energy wasted as reactive
- Thieves use capacitors to create low PF
- Meter records less 'real power'

**Algorithm:**
- Count readings where PF < 0.5
- Score = min(1.0, (low_pf/total) x 3)
- Cross-reference:
- PF<0.3 AND consumption<20% baseline
- -> x5 multiplier (VERY strong signal)

*Why 10% weight? Low PF alone can be legitimate (old motors). Combined with low consumption = strong theft signal.*

---

## PAGE 10: FACTOR 6 - Pattern Irregularity [10%]

**What it detects:** Reversed, chaotic, or artificially manipulated patterns.

**The Physics / Logic:**
- Normal: peaks at 8AM and 7PM.
- Theft: HIGH at 2AM, ZERO during day.
- Stealing when inspectors aren't watching.
- Also detects erratic/random patterns.

**Algorithm:**
- CV = std / mean
- Score = min(1.0, (CV-0.5) / 1.5)
- Day/Night Inversion:
- night_avg > 2x day_avg -> 0.6
- day=0 but night>0 -> 0.85
- mean=0 (active meter) -> 0.8

*Why 10% weight? Catches behavioral anomalies that physics-based measures miss.*

---

## PAGE 11: FACTOR 7 - Frequency Deviation [5%]

**What it detects:** Grid-level anomalies from illegal high-power tapping.

**The Physics / Logic:**
- India grid: exactly 50 Hz (+/- 0.5 Hz)
- Most tightly controlled grid parameter.
- Deviations: large illegal loads tapping in.
- Or generator running unsynchronized.

**Algorithm:**
- Normal band: 49.0 - 51.0 Hz
- Count readings outside band
- Score = min(1.0, (outliers/total) x 4)
- Weak individual signal, useful in combination.

*Why 5% weight? Frequency affects entire grid, not just one meter. Weakest individual signal but adds value in ensemble.*

---

## PAGE 12: FACTOR 8 - Flat-line Detection [5%]

**What it detects:** Spoofed/replayed meter data (hacked firmware).

**The Physics / Logic:**
- Real consumption is NEVER perfectly constant.
- Even a fridge has compressor cycles.
- Same kWh for 24 hours = pre-recorded fake data.
- Very specific attack (firmware hacking).

**Algorithm:**
- unique_ratio = unique_values / total
- Score = min(1.0, (1-unique_ratio)x2 - 0.5)
- Last-24 check:
- <= 2 unique values in 24 readings
- -> score floor at 0.9

*Why 5% weight? Very specific attack type. When present, extremely obvious. But rare (requires technical sophistication).*

---

## PAGE 13: WEIGHTED SCORING & BOOSTING LOGIC

**The Formula:**
theft_prob = (drop x 0.25) + (tamper x 0.20) + (current x 0.15) + (voltage x 0.10) + (PF x 0.10) + (pattern x 0.10) + (freq x 0.05) + (flatline x 0.05)

**Boost Rule 1: Multi-Measure Agreement**
- If 3+ factors score above 0.5: `theft_prob = min(1.0, theft_prob x 1.3)`
- *Why?* Multiple independent detectors agreeing means real probability is HIGHER than weighted average.

**Boost Rule 2: High-Confidence Floor**
- If ANY factor >= 0.9: `theft_prob = max(0.40, theft_prob)`
- *Why?* One factor screaming 'theft' at 0.9 should NEVER be washed out by 7 clean factors.

**Decision Threshold:** 
`anomaly_flag = true` if probability >= 30%
- *Why 30%?* Missing a thief costs ₹50,000+/year. A false alarm costs ₹500 (one inspection). 100:1 cost ratio.

---

## PAGE 14: WORKED EXAMPLE (Scoring a Suspicious Meter)

**Factor Scores:**
- Consumption Drop: 0.80 x 0.25 = 0.200
- Tamper Detection: 0.90 x 0.20 = 0.180
- Current Anomaly:  0.70 x 0.15 = 0.105
- Voltage Anomaly:  0.30 x 0.10 = 0.030
- Power Factor:     0.20 x 0.10 = 0.020
- Pattern Irregular:0.40 x 0.10 = 0.040
- Frequency Deviat: 0.10 x 0.05 = 0.005
- Flat-line:        0.00 x 0.05 = 0.000

**Weighted Sum:** 0.580 (58%)

**Apply Boost Rule 1:** 3 factors > 0.5 (drop, tamper, current) -> x1.3
0.580 x 1.3 = 0.754 (75.4%)

**Result:** 75.4% -> CRITICAL RISK -> Immediate field investigation

---

## PAGE 15: FEATURE ENGINEERING (47+ Features)

1. **Statistical (14):** mean, std, CV, skewness, kurtosis, percentiles (p10/25/75/90), IQR, range, min, max, median
2. **Temporal (10):** weekday/weekend ratio, seasonal Q1-Q4, month-over-month changes, trend ratio, autocorrelation (lag-1, lag-7)
3. **Anomaly (9):** zero-day count/ratio, sudden drops, flatline days, unique ratio, volatility index, below-baseline ratio
4. **Comparative (3):** zone z-score deviation, zone percentile rank, ratio-to-zone average
5. **Metadata (6):** consumer type (one-hot x3), baseline kWh, sanctioned load, consumption-to-sanctioned ratio
6. **Advanced (5):** entropy, last/first 30-day ratio, max consecutive below-threshold, weekday/weekend means

*Note: Raw '10 kWh today' is not enough. ML models need rich, multi-dimensional feature views.*

---

## PAGE 16: CLASS IMBALANCE (91.5% Honest vs 8.5% Theft)

**The Problem: Accuracy Paradox**
A model that ALWAYS predicts 'Honest' gets 91.5% accuracy but catches ZERO thieves. Useless!

**Solution 1: SMOTE**
- Creates synthetic thief samples. Balances to 50/50 training set.
- Math: `x_new = x_i + lambda * (x_zi - x_i)`

**Solution 2: Class Weights**
- Model penalizes missing thief 6.25x more. Forces model to 'care about' thieves.
- `weight = n_total / (2 * n_theft)`

**Solution 3: Threshold Tuning**
- Find threshold that maximizes F1-score (usually ~0.35-0.45, not default 0.50). Lower = catch more thieves.

---

## PAGE 17: THE 5 ML MODELS

1. **Random Forest:** 300 trees voting. max_depth=20, class_weight=balanced. 
   - *Strength:* Feature importance.
2. **XGBoost:** 300 sequential boosted trees. L1/L2 regularization, scale_pos_weight. 
   - *Strength:* Best for tabular data.
3. **DNN:** 128->64->32 neural network. Dropout 40%, BatchNorm, Early Stop. 
   - *Strength:* Non-linear patterns.
4. **LSTM:** 2 stacked layers (128->64). Memory gates, dropout 0.3. 
   - *Strength:* Time-series sequences.
5. **Isolation Forest:** 200 trees, unsupervised. No labels needed, contamination=0.1. 
   - *Strength:* Catches novel theft.

---

## PAGE 18: ENSEMBLE STRATEGY (Combining 5 Models)

**Soft Voting (Simple Average)**
`P_ensemble = (P_RF + P_XGB + P_DNN + P_LSTM + P_ISO) / 5`
*Example:* RF: 0.72, XGB: 0.68, DNN: 0.81, LSTM: 0.55, ISO: 0.60 -> Ensemble = 0.672 (67.2%)

**Stacking (Meta-Learner)**
Logistic Regression learns optimal weights for each model's prediction:
`P = sigmoid(w1*P_RF + w2*P_XGB + w3*P_DNN + w4*P_LSTM + w5*P_ISO + b)`
*If XGBoost is consistently more reliable, meta-learner automatically gives it higher weight.*

**Why Not Just Use the Best Model?**
Every model has blind spots. RF can't capture complex interactions. XGBoost may overfit. DNN is a black box. LSTM is overkill for non-temporal patterns. Isolation Forest has false positives. The ensemble lets models COVER for each other's weaknesses.

---

## PAGE 19: EXPLAINABILITY (SHAP + Heuristic Breakdown)

**The Black-Box Problem:** 
Inspector asks "WHY 90% theft?" -- "Because neural network said so" is NOT acceptable.

**Solution 1: SHAP Values**
Game-theory math (Shapley values) breaks down which feature caused the high score:
- anom_zero_day_ratio: +0.23 (UP)
- stat_cv: +0.18 (UP)
- comp_zone_deviation: +0.15 (UP)
- meta_baseline_kwh: -0.05 (down)

**Solution 2: 8-Measure Breakdown**
The heuristic ALWAYS runs to provide visual breakdown on dashboard:
- Consumption Drop: 80%
- Tamper Detection: 90%
- Current Anomaly: 70%
- Voltage Anomaly: 30%
- Power Factor: 20%
*(Physical explanation operators can understand and act on.)*

---

## PAGE 20: TRAINING PIPELINE (7 Phases)

1. **Load SGCC Dataset:** 42,372 consumers x 1,035 days. 91.5% honest / 8.5% theft.
2. **Preprocessing:** Forward/backward fill missing values. Winsorize at 5th/95th percentile. Engineer 47-65 features.
3. **Class Imbalance:** SMOTE (k=5 neighbors) + Cost-sensitive class weights.
4. **Train 5 Models:** RF(300) + XGBoost(300) + DNN + LSTM + Isolation Forest.
5. **Ensemble:** Soft Voting + Stacking + Optimal threshold tuning.
6. **Evaluation:** Accuracy, Precision, Recall, F1, AUC-ROC, PR-AUC, 5-Fold CV.
7. **SHAP:** TreeExplainer on Random Forest. Top 15 features by importance.

---

## PAGE 21: 6 SYNTHETIC THEFT SCENARIOS

1. **Meter Tampering:** Consumption x 0.1-0.4 (Adjusted calibration).
2. **Bypass:** Zero consumption blocks (Copper wire around CT).
3. **Billing Irregularity:** 30-70% readings replaced (Bribed reader / hacked billing).
4. **Unauthorized Tap:** Sudden drop to near-zero (Direct grid connection).
5. **Flat-line Spoof:** Constant value forever (Hacked meter firmware).
6. **Gradual Decay:** Exponential decay to 5% (Deliberate mechanical degradation).

*Each starts at random point (20-80% through timeline), maintains realistic seasonality before theft.*

---

## PAGE 22: EVALUATION METRICS

- **Precision:** TP / (TP+FP) - Of all 'theft' predictions, how many correct?
- **Recall:** TP / (TP+FN) - Of all actual thieves, how many caught?
- **F1-Score:** 2*(P*R)/(P+R) - Harmonic mean of Precision & Recall.
- **AUC-ROC:** Area under curve - Discrimination ability across all thresholds.

**Confusion Matrix:**
- **TN (True Negative)** = Honest correctly identified
- **TP (True Positive)** = Thief correctly caught!
- **FP (False Positive)** = False alarm (wasted inspection, cost: ₹500)
- **FN (False Negative)** = MISSED thief! (cost: ₹50,000+/year)

**5-Fold Stratified CV:** Split data into 5 parts, train on 4, test on 1. Rotate 5 times. Report mean +/- std.

---

## PAGE 23: SYSTEM ARCHITECTURE

1. **React Frontend:** Vite, Dashboard, Port 5173. 7 pages + JWT auth, Recharts visualization.
2. **Node.js API:** Express, Port 5000. Auth, CRUD, Stats. Orchestrates ML calls.
3. **FastAPI ML Service:** Python, Port 8000. 8-Measure Heuristic, Ensemble Model.
4. **MongoDB:** Port 27017. Meters, Readings, Alerts, Compound Indexes.

**Data Flow:** Frontend --(REST/JSON)--> Backend --(HTTP POST)--> ML Service | Backend --(Mongoose)--> MongoDB

**Triple-Layer Fallback (System NEVER Fails)**
- Layer 1: ML Ensemble (ensemble_model.pkl) -> Highest accuracy
- Layer 2: Python Heuristic (8-measure rules) -> No model file needed
- Layer 3: JavaScript Fallback (same algorithm in JS) -> Zero external dependencies

---

## PAGE 24: RISK CLASSIFICATION (4 Tiers)

1. **LOW (0% - 29%):** No action needed
2. **MEDIUM (30% - 49%):** Inspect within 30 days
3. **HIGH (50% - 74%):** Inspect within 7 days
4. **CRITICAL (75% - 100%):** Immediate investigation

**Data Flow: Button Click to Result**
1. User clicks 'Analyze Anomalies' on a meter
2. Frontend sends POST /api/analyze/:meterId (JWT attached)
3. Backend verifies ownership, fetches 30 days of readings (~720 hourly)
4. Backend computes stats (mean/std/min/max for all 6 dimensions)
5. Backend POSTs to ML Service with 15s timeout
6. ML Service runs ensemble (or heuristic fallback), returns 8 scores
7. If anomaly -> Alert created in MongoDB -> Red banner + 8 progress bars

---

## PAGE 25: SUMMARY

**What We Built:**
- PowerGuard: full-stack ML-powered electricity theft detection system
- Analyzes 6-dimensional smart meter telemetry in real-time
- 8-measure weighted heuristic engine with per-factor explainability
- 5-model ML ensemble (RF + XGBoost + DNN + LSTM + Isolation Forest)
- Trained on SGCC dataset (42,372 consumers) with SMOTE for class imbalance
- 47+ engineered features across 6 categories
- SHAP explainability for transparent, actionable predictions
- 4-service microservice architecture (React + Node.js + FastAPI + MongoDB)
- Triple-layer fallback ensuring zero downtime
- 4-tier risk classification with one-click bulk analysis

*Interview Tip: For every component ask: What? -> Why? -> How? -> Alternatives? -> Trade-offs? -> What would I change?*
