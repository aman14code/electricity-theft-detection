# 🧠 PowerGuard — Complete Deep Dive Study Guide

This guide is written assuming you have **zero prior knowledge**. Read this carefully, and you will be able to confidently explain every single technical concept in your project.

---

## 1. The Core Problem
**What is NTL?**
NTL stands for **Non-Technical Loss**. In power distribution, technical losses are things like heat loss in wires. Non-technical losses are almost entirely **electricity theft** (meter tampering, bypassing the meter, etc.). 

**Why is it hard to detect?**
Currently, power companies just send people to randomly inspect meters. But you can only inspect 2-5% of meters a year. It's expensive and slow.

**The Solution:**
Smart meters send data (consumption, voltage, current) every hour or day. We use **Machine Learning (ML)** to find hidden patterns in this data that prove someone is stealing electricity, so inspectors know exactly *who* to check and *why*.

---

## 2. The Dataset: What is SGCC?
In your project, you used the **State Grid Corporation of China (SGCC) dataset**.

**Why this dataset?**
It is the gold standard benchmark dataset for electricity theft research. It contains real smart meter data from 42,372 consumers over 1,034 days. 

**The BIG Problem: Class Imbalance**
In the SGCC dataset, only **8.5%** of consumers are stealing electricity. The rest (91.5%) are honest. 
*Why is this bad for ML?* If an ML model just guesses "Honest" every single time, it will be 91.5% accurate! But it will have caught zero thieves. We call this the **Class Imbalance Problem**, and your project uses special techniques to fix it.

---

## 3. How We Fixed Class Imbalance
You used three main techniques to force the model to care about the 8.5% thieves:

1. **SMOTE (Synthetic Minority Over-sampling Technique):** 
   - *What it is:* We don't have enough data on thieves. SMOTE mathematically creates "fake" (synthetic) data points that look like the real thieves to balance the dataset.
2. **Cost-Sensitive Learning (Class Weights):**
   - *What it is:* We tell the ML model: "If you misclassify an honest person, it's a small penalty. But if you miss a thief, it's a MASSIVE penalty."
3. **Threshold Optimization:**
   - *What it is:* Usually, ML models say "If probability > 50%, it's a thief." We mathematically analyze the results to find the perfect custom threshold (e.g., 45%) that catches the most thieves without falsely accusing too many honest people.

---

## 4. Feature Engineering (The 47 Features)
Raw smart meter data just says "User used 10 kWh today." That's not enough for ML. We "engineered" (calculated) **47 new data points (features)** from the raw data.

**Categories of Features we created:**
- **Statistical:** Mean, standard deviation. (Thieves have highly erratic data).
- **Temporal (Time):** Weekday vs Weekend ratio. (Thieves often steal at specific times).
- **Anomaly:** How many days did they use exactly 0 kWh? (A huge red flag).
- **Comparative:** How does this user's consumption compare to their neighbors?

*If they ask:* "Why feature engineering?"
*Answer:* "Raw consumption data is too simple. Derived statistical features like the coefficient of variation or zero-consumption-day-count are much stronger indicators of theft."

---

## 5. The 5 Machine Learning Models
You didn't just use one model; you trained 5 completely different types of AI to look at the problem from different angles. 

1. **Random Forest (RF):** 
   - *How it works:* It creates hundreds of "decision trees" (like flowcharts). Each tree votes on whether it's a thief.
   - *Why we used it:* It is very robust and tells us *which* features (like zero-days) were most important.
2. **XGBoost:**
   - *How it works:* It builds trees sequentially, where each new tree focuses entirely on fixing the mistakes of the previous tree.
   - *Why we used it:* It is the absolute best model for tabular data and handles class imbalance very well.
3. **Deep Neural Network (DNN):**
   - *How it works:* Mimics the human brain with layers of "neurons". 
   - *Why we used it:* It can find deep, hidden, non-linear patterns that standard math misses.
4. **LSTM (Long Short-Term Memory):**
   - *How it works:* A special neural network designed specifically for time-series data (sequences of events).
   - *Why we used it:* Electricity usage happens over time. LSTM remembers what happened 30 days ago to predict if today's drop is suspicious.
5. **Isolation Forest:**
   - *How it works:* It doesn't look for thieves. It just looks for "weird" data that is isolated from normal behavior. (Unsupervised learning).
   - *Why we used it:* To catch brand new theft techniques that we haven't seen before.

---

## 6. The Ensemble (The Crown Jewel)
Instead of picking the "best" model, your system combines them into an **Ensemble**.

**Soft Voting:** 
Every model outputs a probability (e.g., RF says 60%, XGBoost says 70%). The Ensemble takes the mathematical average (65%).
*Why this is brilliant:* No single model is perfect. Isolation Forest might have a blind spot, but XGBoost will cover for it. The Ensemble achieved the highest overall score (AUC-ROC: 0.809).

---

## 7. The Evaluation Metrics (How we score the models)
Never say "We used Accuracy." Because of class imbalance (91.5% honest), Accuracy is a bad metric. You used:

- **Precision:** Out of all the people we *accused* of theft, how many were *actually* thieves? (Reduces false alarms).
- **Recall:** Out of all the *actual* thieves in the world, how many did we *catch*?
- **F1-Score:** The harmonic mean (balance) between Precision and Recall.
- **AUC-ROC (Area Under the Curve):** The ultimate metric. It measures the model's ability to distinguish between thieves and honest users across all possible thresholds. **Our Ensemble won with 0.809.**

---

## 8. Explainable AI (SHAP & Heuristics)
**The Problem:** If the AI says "This user is 90% a thief," the inspector will ask "Why?" If you say "Because the Neural Network said so," they will reject it. (Black-box problem).

**The Solution:**
1. **SHAP (SHapley Additive exPlanations):** A game-theory math technique that breaks down exactly which feature caused the high score (e.g., "Score is high because `anom_zero_day_count` is abnormally high").
2. **The 8-Measure Heuristic Engine:** We built a backup rule-based engine. It physically looks at 8 things (Voltage drops, Current bypass, Tampering flags) and shows exactly which physical law was broken. This gives the inspector a "Breakdown" on the dashboard.

---

## 9. System Architecture (How it's built)
Your system is not just a Python script. It is a **Microservice Architecture** ready for the real world:

1. **Frontend (Vercel):** React + Vite. The dashboard the utility worker looks at.
2. **Backend API (Render):** Node.js + Express. Handles user logins, saves meters to the database.
3. **ML Service (Render):** FastAPI (Python). The heavy-lifter. The backend sends meter data here, Python runs the Ensemble model, and sends the probability score back.
4. **Database (MongoDB Atlas):** Stores all the meters, alerts, and historical data.

*Why Microservices?* Because Python is best for ML, but Node.js is much faster for a web API. We split them up so they can work independently.

---

## 🌟 Summary to Memorize
"We took the **SGCC smart meter dataset**, engineered **47 features**, and fixed the **8.5% class imbalance** using **SMOTE**. We trained **5 different models** (RF, XGBoost, DNN, LSTM, Isolation Forest) and combined them using a **Soft Voting Ensemble**, achieving an **AUC-ROC of 0.809**. Finally, we wrapped it in a **Microservice web app** with an **Explainability layer** so utility workers can actually use it in the real world."
