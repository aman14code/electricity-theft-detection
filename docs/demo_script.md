# ⚡ PowerGuard — Demo Script for Teachers

**Live URL:** [https://electricity-theft-detection-sandy.vercel.app](https://electricity-theft-detection-sandy.vercel.app)  
**Duration:** 15–20 minutes  
**Tip:** Open the site beforehand so Render's free tier wakes up (takes ~30s first load)

---

## 🎬 Opening (1 minute)

> *"This is **PowerGuard** — an end-to-end electricity theft detection system built as a research project. India loses approximately ₹1.5 lakh crore annually to electricity theft, which is about 20-25% of total electricity generated. Traditional detection relies on manual inspections which can only cover 2-5% of consumers per year. Our system uses **machine learning** to automatically detect theft from smart meter data."*

**Key phrase to say:** *"This is based on our research paper: **Electricity Theft Detection Using Machine Learning — An Ensemble Approach for Non-Technical Loss Identification in Power Distribution Networks**"*

---

## Step 1: Login / Register (1 minute)

1. Click **Register** → create a demo account (e.g., `Demo Power Corp`, any email/password)
2. You'll be redirected to the Dashboard

> *"The system is multi-tenant — each power distribution company registers separately and only sees their own meters and alerts. We use JWT-based authentication."*

---

## Step 2: Dashboard (2 minutes)

**Show these sections:**

### Metric Cards (top)
> *"These show real-time stats — total meters registered, active theft alerts, resolved cases, and the average threat score across the network."*

### Consumption Chart
> *"This is a 7-day consumption aggregation across all smart meters. In a real deployment, sudden network-wide drops here could indicate large-scale theft."*

### Anomaly Detection Panel
> *"We use **8 independent detection measures** — each analyzing a different dimension of theft:*
> 1. *Consumption Drop — zero kWh during peak hours*
> 2. *Tamper Detection — hardware tamper flags*
> 3. *Current Bypass — low current with normal voltage*
> 4. *Voltage Anomaly — readings outside 190–250V range*
> 5. *Power Factor, Frequency, Pattern Irregularity, and Flat-line Detection"*

### System Status Panel
> *"Our system uses a **microservice architecture** — React frontend on Vercel, Node.js backend on Render, FastAPI ML service on Render, and MongoDB Atlas for storage."*

---

## Step 3: Add a Smart Meter (2 minutes)

1. Go to **Meters** page
2. Click **"Add Meter"**
3. Fill in: Location = `Block A — Building 1`, Type = `Residential`, Baseline = `3.5`
4. Create it

> *"Each smart meter has a location, consumer type (residential/commercial/industrial), and a baseline consumption. The baseline is critical for our ML model — one of our 47 engineered features is `meta_baseline_kwh` which helps detect if actual consumption is abnormally low compared to expected usage."*

---

## Step 4: Meter Detail + Run Analysis (3 minutes) ⭐ KEY DEMO

1. Click on the meter you just created
2. Click **"Generate Readings"** to create sample smart meter data
3. Click **"Run ML Analysis"**

> *"Watch what happens — the system sends 6-dimensional telemetry (consumption kWh, voltage, current, power factor, frequency, tamper flag) to our FastAPI ML service."*

**After analysis completes, show:**

### Theft Probability Score
> *"This is the ensemble prediction. Our system uses **5 ML models** — Random Forest, XGBoost, DNN, Isolation Forest, and LSTM — combined through **soft voting**. As described in our paper, using an ensemble reduces false positives because no single model's blind spots dominate."*

### Anomaly Breakdown (8 measures)
> *"This is the **explainability layer** — instead of just a black-box score, we show exactly WHY the system flagged this meter. Each of the 8 measures shows its individual score. This is critical for field inspection teams — they need to know WHAT to look for when they visit."*

### Risk Level Classification
> *"We classify into 4 risk levels: Low (<30%), Medium (30-49%), High (50-74%), Critical (≥75%). This creates a **prioritized inspection queue** — field teams inspect Critical cases first."*

---

## Step 5: Alerts Page (1 minute)

1. Go to **Alerts**
2. Show the alert that was auto-created from the analysis
3. Click the status badge to change it: `Pending → Investigating → Resolved`

> *"Alerts are auto-generated when theft probability exceeds the threshold. There's a workflow — operators can mark alerts as investigating, then resolved. Each alert stores the full anomaly breakdown for audit trails."*

---

## Step 6: Reports Page (2 minutes)

1. Go to **Reports**
2. Click **"Run Bulk Analysis"** (analyzes all meters at once)
3. Show the risk distribution chart
4. Click **"Export CSV"**

> *"This is the **operational dashboard** for utility managers. One click runs analysis across the entire network, generates a risk-ranked chart, and the CSV export enables regulatory reporting. As our paper discusses, optimizing limited field-inspection capacity is a key objective."*

---

## Step 7: ML Models Page (3 minutes) ⭐ RESEARCH HIGHLIGHT

1. Go to **ML Models**

### Dataset Info Cards
> *"We used the **SGCC (State Grid Corporation of China) dataset** — 42,372 consumers, 1,034 days of readings, with an 8.5% theft rate. This severe class imbalance is exactly the challenge our paper addresses using SMOTE and cost-sensitive learning."*

### Model Comparison Bar Chart
> *"Here you can see all 6 models compared — Random Forest, XGBoost, DNN, Isolation Forest, LSTM, and the Soft Voting Ensemble. The Ensemble achieves the best **AUC-ROC of 0.809** and F1-score of 0.423, validating our paper's hypothesis that combining complementary learners improves robustness."*

### Key metrics to highlight:

| Model | Accuracy | AUC-ROC | F1-Score |
|-------|----------|---------|----------|
| Random Forest | 85.3% | 0.794 | 0.365 |
| XGBoost | 90.2% | 0.786 | 0.397 |
| DNN | 87.1% | 0.787 | 0.378 |
| Isolation Forest | 85.0% | 0.587 | 0.192 |
| LSTM | 87.9% | 0.747 | 0.368 |
| **Soft Voting Ensemble** | **89.9%** | **0.809** | **0.423** |

> *"Notice the Ensemble outperforms every individual model on AUC-ROC and F1. This is because:*
> - *Random Forest captures feature interactions*
> - *XGBoost handles class imbalance well*
> - *DNN learns non-linear patterns*
> - *Isolation Forest detects unsupervised anomalies*
> - *LSTM captures temporal sequences"*

### Radar Chart
> *"This radar visualization shows each model's strengths. Notice how Isolation Forest has poor recall but each model excels in different areas — that's exactly why ensemble works."*

### Cross-Validation Results
> *"We used **5-fold stratified cross-validation** to ensure our results are not due to data leakage. The low standard deviations (accuracy std ~1.3%) confirm our model generalizes well."*

### Feature Engineering
> *"We engineered **47 features** across 7 categories — statistical (mean, std, kurtosis), temporal (weekday/weekend ratio, seasonal patterns), anomaly (zero-day count, sudden drops, flatline detection), comparative (zone deviation), metadata (consumer type, sanctioned load), and advanced (entropy, autocorrelation). This comprehensive feature set is a key contribution of our paper."*

---

## 🎯 Closing (1 minute)

> *"To summarize — PowerGuard is a **complete, deployed, production-ready** electricity theft detection system that:*
> 1. *Uses a **5-model ensemble** (RF, XGBoost, DNN, Isolation Forest, LSTM)*
> 2. *Engineers **47 features** from raw smart meter data*
> 3. *Handles **8.5% class imbalance** using SMOTE and threshold optimization*
> 4. *Provides **explainable predictions** with per-measure breakdowns*
> 5. *Runs on a **microservice architecture** — React, Node.js, FastAPI, MongoDB*
> 6. *Is **fully deployed** and accessible online"*

---

## ❓ Common Questions Teachers May Ask

### "Why ensemble instead of a single model?"
> *"As shown in our results, no single model dominates across all metrics. The ensemble achieves AUC-ROC of 0.809 vs the best individual model (Random Forest at 0.794). By combining complementary learners, we reduce the risk of model-specific blind spots."*

### "How do you handle class imbalance?"
> *"The SGCC dataset has only 8.5% theft cases. We use three strategies: (1) SMOTE for synthetic minority oversampling, (2) class-weighted loss functions, and (3) threshold optimization — we don't use the default 0.5 cutoff but optimize per model using PR curves."*

### "What's the real-world impact?"
> *"If a utility with 1 million consumers deploys this, and our system correctly identifies even 50% of the ~85,000 theft cases at an average of ₹10,000 annual loss per case, that's ₹425 crore in recovered revenue."*

### "Why microservices?"
> *"The ML service needs Python (scikit-learn, TensorFlow, XGBoost). The backend needs Node.js for real-time API performance. Separating them means we can scale the ML service independently during bulk analysis."*

### "What are the limitations?"
> *"Be honest: (1) SHAP importance is not yet implemented per-prediction (global only), (2) the dataset is the SGCC benchmark — real Indian consumption patterns may differ, (3) the free tier deployment has cold starts. These are areas for future work."*

---

## 🔧 Pre-Demo Checklist

- [ ] Open the site 2 minutes before demo (wakes up Render free tier)
- [ ] Have a test account ready, or register one live
- [ ] Add at least 1 meter + generate readings + run analysis beforehand so there's data to show
- [ ] Keep the ML Models page loaded — it's the most impressive visual
- [ ] Have this script open on your phone/second screen as a reference
