# A Multi-Tier Machine Learning Framework for Electricity Theft Detection in Advanced Metering Infrastructure Using Indian Grid Telemetry and Benchmark Validation

**Keshav Aggarwal$^1$, Aman Sharma$^1$, Abhinav Saini$^1$, Ashu Singh$^2$**  
*$^1$Department of Computer Science & Engineering, Meerut Institute of Engineering & Technology (MIET), Meerut, Uttar Pradesh, India*  
*$^2$Department of Computer Science & Engineering, Meerut Institute of Engineering & Technology (MIET), Meerut, Uttar Pradesh, India (Supervisor)*  
*Email: {keshav.aggarwal, aman.sharma, abhinav.saini, ashu.singh}@miet.ac.in*

---

### Abstract
Non-Technical Losses (NTLs), predominantly arising from electricity theft and meter tampering, inflict substantial financial deficits on power distribution utilities worldwide. In emerging smart grids, data-driven electricity theft detection via Advanced Metering Infrastructure (AMI) telemetry is hindered by severe class imbalance, residential consumption volatility, and privacy regulations that restrict access to field-inspected theft records. This paper presents an end-to-end anomaly detection framework evaluated across three distinct datasets: authentic Indian smart meter telemetry from the Council on Energy, Environment and Water (CEEW) deployment in Uttar Pradesh (235,547 hourly records; 160 profile instances across 20 monitored distribution nodes), a 5,000-record weather-enriched dataset, and an external 191-consumer benchmark derived from utility audit records. We formulate seven domain-specific NTL attack profiles ($T_1$–$T_7$), extract 47 multidimensional statistical, temporal, ratio-based, and rolling-window electrical features, and enforce a leak-free meter-grouped holdout partition (`GroupShuffleSplit`) coupled with Synthetic Minority Over-sampling (`SMOTE`) applied strictly to training partitions. Five classifiers—Random Forest, XGBoost, Deep Neural Network (DNN), Long Short-Term Memory (LSTM), and Isolation Forest—were evaluated alongside a Soft-Voting Probability Ensemble. On the unseen 4-meter physical CEEW holdout (32 profiles: 4 honest, 28 theft), the Soft-Voting Ensemble attained 96.88% accuracy, 100.0% precision, 96.43% recall, 0.9818 $F_1$-score, and an AUC-ROC of 1.0000. In 5-fold `GroupKFold` cross-validation across all 20 base physical meters, XGBoost demonstrated high stability with a mean $F_1$-score of $0.9825 \pm 0.0176$ (sample SD, $ddof=1$) and mean accuracy of $96.88\% \pm 3.12\%$. On the weather-enriched dataset, the ensemble achieved 99.10% accuracy, 100.0% recall, and 0.9174 $F_1$-score. On the external audit benchmark, XGBoost achieved the highest accuracy (82.05%) and $F_1$-score (0.8205), highlighting domain generalization challenges under real-world human tampering. The framework integrates TreeSHAP explainability with a physics-informed heuristic engine, providing transparent decision support for field inspection triage.

**Index Terms**—Electricity Theft Detection, Advanced Metering Infrastructure (AMI), Non-Technical Losses (NTL), Machine Learning, Soft-Voting Ensemble, SMOTE, Indian Smart Grid, Explainable AI (XAI), SHAP.

---

## I. INTRODUCTION

Electricity theft represents one of the most critical operational and economic challenges facing electrical distribution companies (DISCOMs) worldwide. Non-Technical Losses (NTLs)—encompassing physical line tapping, meter bypass, secondary current transformer shunting, internal calibration tampering, and cyber-physical telemetry spoofing—account for tens of billions of dollars in lost utility revenue annually across the globe [1], [2]. In developing economies, the severity is particularly acute: in India, Aggregate Technical and Commercial (AT&C) losses historically range between 15% and 22% across several state utilities, creating persistent financial deficits that inhibit infrastructure modernization and renewable energy integration [3].

The global transition toward Smart Grids and Advanced Metering Infrastructure (AMI) has equipped distribution networks with bidirectional smart meters capable of transmitting high-frequency telemetry (typically at 3-minute, 15-minute, or 1-hour intervals) [4]. While this granular data theoretically enables automated surveillance, machine-learning-based electricity theft detection faces four profound hurdles in practice [5]–[7]:

1. **Extreme Class Imbalance:** In real-world distribution feeders, fraudulent consumers represent a small minority of the customer base (typically 2% to 10%), causing naive classification models to predict the majority class (honest consumers) with deceptive high accuracy while failing to detect actual theft [3], [7].
2. **Absence of Public Ground-Truth Labels in Emerging Grids:** Under consumer privacy regulations and utility confidentiality policies, Indian DISCOMs do not publicly release customer-level field audit records or convicted customer identifiers. Consequently, research must bridge authentic Indian telemetry with mathematically formulated NTL attack models [4], [10], [11].
3. **High Volatility and Load Diversity:** Normal residential consumption exhibits severe non-linear fluctuations driven by seasonal weather, festival loads, and irregular occupancy, which frequently mimic consumption drops caused by theft [5], [9].
4. **False Positive Dispatch Cost:** In physical utility operations, sending Quick Response Teams (QRTs) and enforcement inspectors to suspected consumer premises incurs substantial labor costs. A model with high recall but low precision overwhelms field staff with false alarms, destroying operational viability [7].

### Major Contributions
To address these challenges with methodological rigor, this paper makes the following key contributions:
* **Multi-Source Empirical Evaluation:** We evaluate our methodology across authentic high-resolution Indian grid telemetry from the Council on Energy, Environment and Water (CEEW) deployment in Uttar Pradesh (235,547 hourly records across 20 distribution nodes), an enriched 5,000-record smart meter dataset with meteorological parameters, and an established 191-consumer benchmark derived from utility audit records.
* **Leak-Free Meter-Grouped Splitting:** To eliminate the widespread methodological risk of meter-level telemetry leakage, we implement `GroupShuffleSplit` and `GroupKFold` strictly by base physical meter identifier, ensuring zero meter overlap between training and testing partitions, and apply SMOTE strictly to training folds.
* **Physics-Informed Feature Engineering:** We engineer 47 statistical, temporal, ratio-based, and rolling-window electrical features capturing consumption drops, current bypass conditions, voltage/frequency anomalies, and load factor fluctuations.
* **Domain-Specific NTL Attack Formulation ($T_1$–$T_7$):** We formulate seven domain-specific attack profiles inspired by smart grid literature [4], [10] simulating peak-hour bypass, flatline spoofing, gradual degradation, night-only consumption, voltage tampering, current coil shunting, and stochastic partial theft.
* **Probability Soft-Voting Ensemble:** We combine complementary tree-based, neural, and sequence-oriented supervised models into a unified probability soft-voting ensemble that provides higher operational stability than individual models.
* **Explainable AI (XAI) & Operational Decision Support:** We couple TreeSHAP feature attribution with a physics-informed heuristic engine, operationalized inside an end-to-end microservice architecture (FastAPI backend, React dashboard, and interactive GIS mapping) to enable transparent inspection triage.

---

## II. LITERATURE REVIEW

The detection of non-technical losses has progressed from physical line inspection and manual audits to machine learning and deep learning methodologies [4]–[6].

### A. Classical Machine Learning Approaches
Early automated detection relied on supervised shallow classifiers. Jokar *et al.* [15] established a foundational benchmark using Support Vector Machines (SVM) combined with customer consumption pattern analysis. While SVMs achieve reasonable boundary separation on small datasets, their computational complexity scales quadratically with sample size, rendering them impractical for million-meter AMI deployments. Furthermore, classical SVMs exhibit severe degradation in the presence of noisy readings and missing telemetry packets [8]. Decision tree ensembles, specifically Random Forest [13], [28] and Gradient Boosting [16], [17], [29], demonstrated substantial improvements by handling non-linear interactions and tabular feature distributions, though tuning depth parameters remains necessary to avoid overfitting to specific feeders.

### B. Deep Learning and Sequence Modeling
With the expansion of AMI data volume, deep learning architectures emerged to model sequential consumption. Zheng *et al.* [11] proposed a Wide & Deep convolutional neural network (CNN) framework to capture both periodic daily cycles and global consumption trends from daily consumption matrices. Hasan *et al.* [14] applied Long Short-Term Memory (LSTM) recurrent networks to model temporal dependencies, demonstrating that recurrent memory cells can detect subtle downward drifts in consumption that static models miss. Further hybrid deep learning paradigms, including GAN-CNN [19] and Autoencoder-BiGRU architectures [18], have been explored to capture non-linear temporal dynamics under severe load fluctuations.

### C. Methodological Rigor and Leakage Prevention
A pervasive challenge in NTL detection literature is the proper handling of class imbalance and data splitting. Many published works inadvertently apply over-sampling techniques such as SMOTE [26] across the entire dataset before partitioning into train and test splits, or perform naive random splits on datasets where multiple instances originate from the same consumer meter. As highlighted in recent critical surveys [7], [9], both practices cause severe data leakage, resulting in artificially inflated test accuracies that collapse when deployed in real utility environments. In this work, we strictly enforce meter-grouped partitioning and fold-isolated SMOTE to guarantee methodological validity.

---

## III. PROPOSED METHODOLOGY

The end-to-end workflow of the proposed electricity theft detection framework is structured into six sequential pipelines: data ingestion, theft attack simulation, feature extraction, leak-free class balancing via SMOTE, ensemble classification, and explainable decision dispatch.

### A. Multi-Source Dataset Architecture
We evaluate the framework across three complementary datasets spanning diverse operational environments:

#### TABLE I: Characteristics and Partitioning Protocols for Evaluated Datasets
| Dataset Identifier | Source / Geography | Attributes & Telemetry | Instance Count | Splitting & Validation Protocol | Ground-Truth Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dataset A: CEEW Telemetry** | Mathura & Bareilly, Uttar Pradesh, India [36] | Active kWh, Voltage (V), Current (A), Frequency (Hz) at 3-min / hourly intervals | 235,547 hourly records; 160 profile instances across 20 base meters | 80:20 `GroupShuffleSplit` by meter ID (16 train / 4 test meters); 5-Fold `GroupKFold`; SMOTE on train only | Authentic Indian field telemetry + 7 domain-specific attack profiles ($T_1$–$T_7$) |
| **Dataset B: Smart Meter + Weather** | Smart grid AMI feeder with weather telemetry [38] | Hourly kWh consumption, ambient temperature, humidity, wind speed, rolling averages | 5,000 records (4,750 normal, 250 anomalous) | 80:20 Stratified Split (4,000 train, 1,000 test: 950 normal, 50 anomalous); 5-Fold Stratified CV | Labeled anomaly records capturing consumption divergence under weather extremes |
| **Dataset C: Benchmark** | Public smart meter theft benchmark [37] | Daily kWh consumption time-series over 1,034 consecutive monitoring intervals | 191 curated consumer profiles (97 confirmed fraud, 94 honest; 9 dropped from original 200 due to >50% missing readings) | 80:20 Stratified Split (152 train, 39 test: 19 normal, 20 fraud); 5-Fold Stratified CV | Open-source utility inspection records and consumer audit logs |

![Fig. 1. Class distribution of AMI telemetry showing baseline class imbalance.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_graphs/fig1_class_imbalance.png)  
*Fig. 1. Class distribution of AMI telemetry showing baseline class imbalance before synthetic balancing.*

### B. Domain-Specific Theft Injection Formulation
To establish ground-truth fraud patterns on authentic Indian telemetry, we implement seven domain-specific non-technical loss attack profiles inspired by smart grid literature [4], [10] and calibrated to model physical bypass, tampering, and degradation:

* **Attack $T_1$ (Peak-Hour Bypass):** Complete disconnection or bypassing during peak tariff intervals ($08:00$ to $20:00$), setting kWh to zero and reducing recorded current to 5%:
  $$x_t' = 0.0, \quad I_t' = 0.05 \cdot I_t, \quad \forall t \in [08:00, 20:00)$$
* **Attack $T_2$ (Flat-Line Spoofing):** Reporting a constant minimal consumption to bypass progressive billing tiers:
  $$x_t' = 0.30 \cdot \text{median}(x_{1..T}), \quad \forall t$$
* **Attack $T_3$ (Gradual Consumption Degradation):** Mechanically wearing down meter disk gears or slowly altering calibration constants over time, creating a linear downward drift from 100% to 15%:
  $$x_t' = x_t \cdot \left(1.0 - 0.85 \frac{t}{T}\right), \quad I_t' = I_t \cdot \left(1.0 - 0.85 \frac{t}{T}\right)$$
* **Attack $T_4$ (Night-Only Usage):** Simulating residential energy theft where daytime domestic or commercial loads ($06:00$ to $22:00$) are bypassed:
  $$x_t' = 0.0, \quad I_t' = 0.02 \cdot I_t, \quad \forall t \in [06:00, 22:00)$$
* **Attack $T_5$ (Voltage Tampering):** Inducing an artificial voltage attenuation alongside partial energy shunting:
  $$V_t' = V_t \cdot \beta, \quad \beta \sim \mathcal{U}(0.65, 0.80); \quad x_t' = x_t \cdot \delta, \quad \delta \sim \mathcal{U}(0.30, 0.60)$$
* **Attack $T_6$ (Current Coil Bypass):** Shunting the secondary current transformer (CT) coil with 70% probability across readings, while voltage telemetry remains normal:
  $$I_t' = 0.03 \cdot I_t, \quad x_t' = 0.05 \cdot x_t, \quad V_t' = V_t, \quad \text{for } p = 0.70$$
* **Attack $T_7$ (Random Dynamic Partial Theft):** Applying a stochastic reduction factor reflecting intermittent illegal hook-ups:
  $$x_t' = x_t \cdot \gamma_t, \quad I_t' = I_t \cdot \gamma_t, \quad \gamma_t \sim \mathcal{U}(0.30, 0.70)$$

![Fig. 2. Hourly load profiles showing honest consumer baselines versus synthetic theft attack signatures.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig02_Consumption_Profile_Honest_vs_Theft.png)  
*Fig. 2. Hourly load profiles showing honest consumer baselines versus synthetic theft attack signatures ($T_1$ to $T_7$).*

### C. Leak-Free Class Imbalance Remediation via SMOTE
Due to the numerical sparsity of theft events relative to normal operations, training unweighted classifiers yields biased decision boundaries. We formulate the Synthetic Minority Over-sampling Technique (SMOTE) [26] in the engineered 47-dimensional feature space. Crucially, to strictly prevent data leakage, the dataset is partitioned into train and test splits prior to resampling. SMOTE is applied exclusively to the training partition, ensuring the test set remains purely comprised of genuine, unaugmented records from completely unseen physical meters.

For each minority sample $x_i \in \mathcal{X}_{minority}$, its $k$-nearest neighbors within $\mathcal{X}_{minority}$ are computed using Euclidean distance:
$$d(x_i, x_j) = \sqrt{\sum_{f=1}^{47} (x_{i,f} - x_{j,f})^2}$$

A neighbor $x_{zi}$ is selected at random, and a synthetic minority instance $x_{new}$ is generated along the line segment joining $x_i$ and $x_{zi}$:
$$x_{new} = x_i + \lambda \cdot (x_{zi} - x_i), \quad \lambda \sim \mathcal{U}(0, 1)$$

![Fig. 3. Feature-space sample distribution before and after SMOTE balancing on training fold.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig01_SMOTE_Before_After.png)  
*Fig. 3. Feature-space sample distribution before and after SMOTE balancing on the training partition.*

### D. 47 Multidimensional Engineered Features
Rather than feeding raw, uncurated time-series data directly into classifiers, we engineer 47 discriminative features across four structural categories (Table II):

#### TABLE II: 47 Multidimensional Engineered Feature Taxonomy Extracted per Consumer Profile
| Category | Feature Count | Specific Extracted Features | Physical / Operational Rationale |
| :--- | :--- | :--- | :--- |
| **Statistical Descriptors** | 24 | Mean, standard deviation, minimum, maximum, skewness, and kurtosis computed for each of the 4 electrical channels (`kwh`, `voltage`, `current`, `frequency`) | Captures baseline consumption, load dispersion, extreme spikes, distribution asymmetry, and tail heavy-tailedness caused by physical tampering or partial shunting |
| **Temporal Features** | 8 | `peak_consumption_mean` (08:00–20:00), `offpeak_consumption_mean` (20:00–08:00), `night_day_ratio` (off-peak / peak mean), `weekday_mean` (Mon–Fri), `weekend_mean` (Sat–Sun), `weekday_weekend_ratio`, `consumption_entropy` (Shannon entropy of normalized 24-hr mean consumption), `peak_concentration` (peak kWh / total kWh) | Identifies tampering signatures that alter daily periodicity, clip daytime peak loads ($T_1$), invert nighttime-to-daytime ratios ($T_4$), or flatten diurnal load profiles |
| **Ratio-Based & Operational Anomaly** | 10 | `zero_peak_ratio` (fraction of peak hours with 0 kWh), `bypass_ratio` (fraction with current < 10th percentile and voltage > 25th percentile), `flat_line_score` ($1 - \frac{\text{unique kWh}}{\text{total readings}}$), `kwh_cv`, `voltage_cv`, `current_cv` (coefficients of variation), `voltage_anomaly_ratio` (readings outside 190–260 V), `freq_anomaly_ratio` (readings outside 49.5–50.5 Hz), `zero_consumption_ratio` (overall zero-reading fraction), `max_consecutive_zeros` (longest zero run) | Directly detects current transformer coil bypass ($T_6$), flat-line spoofing ($T_2$), anomalous grid supply deviations ($T_5$), and prolonged artificial outages |
| **Rolling Window & Trend** | 5 | `rolling_3d_mean` (mean of 3-day rolling daily kWh sum), `rolling_3d_std` (std of 3-day rolling daily kWh sum), `rolling_7d_mean`, `rolling_7d_std`, `rolling_7d_trend` (linear regression slope across daily sums) | Quantifies multi-day load volatility, baseline drift, and continuous downward degradation trends characteristic of calibration decay and disk wear ($T_3$) |

![Fig. 4. Global feature importance ranking computed via TreeSHAP across 47 engineered features.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig07_SHAP_XGBoost_CEEW.png)  
*Fig. 4. Global feature importance ranking computed via TreeSHAP for XGBoost on Dataset A (CEEW).*

### E. Model Paradigms & Soft-Voting Probability Ensemble
Five complementary learning algorithms spanning diverse inductive biases were formulated:
1. **Random Forest (RF) [28]:** An ensemble of 200 decorrelated decision trees built via bootstrap aggregation (bagging) with random feature subspaces (`max_depth=12`, `min_samples_split=4`).
2. **Extreme Gradient Boosting (XGBoost) [29]:** Sequential additive gradient tree boosting optimizing a regularized objective function with second-order Taylor loss expansion (`n_estimators=200`, `learning_rate=0.05`, `max_depth=6`, `subsample=0.8`).
3. **Deep Neural Network (DNN) [32]:** A 4-layer fully connected architecture (256 $\to$ 128 $\to$ 64 $\to$ 32 units) with Batch Normalization after the first three layers, Dropout regularizers ($p \in \{0.3, 0.3, 0.2, 0.2\}$), ReLU activations, and a sigmoid output node trained under binary cross-entropy.
4. **Long Short-Term Memory (LSTM) [30]:** A 2-layer recurrent architecture (64 and 32 units) with dropout ($p=0.2$) followed by a 16-unit dense layer and sigmoid classification node, evaluating sequential feature representations.
5. **Isolation Forest (iForest) [31]:** An unsupervised tree ensemble (100 isolation trees) that isolates anomalies by recursively partitioning randomly selected features.

To capitalize on their complementary decision boundaries, a Soft-Voting Probability Ensemble was constructed from the four supervised classifiers ($M=4$: RF, XGBoost, DNN, and LSTM). The unsupervised Isolation Forest was excluded from the voting pool to avoid calibrating unbounded anomaly scores alongside bounded posterior probabilities. The ensemble posterior probability $\hat{P}_{Ens}(y=1|x)$ was computed as the weighted convex combination:
$$\hat{P}_{Ens}(y=1|x) = \sum_{m=1}^4 w_m P_m(y=1|x), \quad \text{subject to } \sum_{m=1}^4 w_m = 1, \quad w_m \ge 0$$

Weights $w_m$ are assigned proportionally to each model's training-fold validation $F_1$-score. Classification decisions are executed using the canonical threshold $\tau = 0.5$ without post-hoc test-set threshold tuning, guaranteeing unbiased evaluation.

---

## IV. EXPERIMENTAL RESULTS AND DISCUSSION

### A. Performance Metrics Formulation
Model evaluation was conducted using standard classification metrics:
$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}, \quad \text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}$$
$$F_1\text{-Score} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}, \quad \text{AUC-ROC} = \int_0^1 \text{TPR}(\text{FPR}) \, d(\text{FPR})$$

### B. Quantitative Benchmark Comparison
Tables III, IV, and V summarize empirical performance across the three datasets generated from the unified leak-free training pipeline:

#### TABLE III: Classifier Evaluation on Dataset A (CEEW Indian AMI Telemetry, Unseen Meters Holdout)
| Model Architecture | Accuracy | Precision | Recall | $F_1$-Score | AUC-ROC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Random Forest | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| XGBoost | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| Deep Neural Network (DNN) | 0.9688 | **1.0000** | 0.9643 | 0.9818 | 0.9911 |
| Long Short-Term Memory (LSTM) | 0.9062 | 0.9630 | 0.9286 | 0.9455 | 0.9196 |
| Isolation Forest | 0.1562 | **1.0000** | 0.0357 | 0.0690 | 0.6429 |
| **Soft-Voting Ensemble** | **0.9688** | **1.0000** | **0.9643** | **0.9818** | **1.0000** |

#### TABLE IV: Classifier Evaluation on Dataset B (Smart Meter with Weather Telemetry, Abnormal Class Evaluation)
| Model Architecture | Accuracy | Precision | Recall | $F_1$-Score | AUC-ROC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Random Forest | 0.9860 | **0.9500** | 0.7600 | 0.8444 | **0.9987** |
| XGBoost | 0.9900 | 0.8448 | 0.9800 | 0.9074 | 0.9979 |
| Deep Neural Network (DNN) | 0.9490 | 0.4949 | 0.9800 | 0.6577 | 0.9913 |
| Long Short-Term Memory (LSTM) | 0.8910 | 0.2435 | 0.5600 | 0.3394 | 0.8777 |
| Isolation Forest | 0.9150 | 0.3196 | 0.6200 | 0.4218 | 0.9256 |
| **Soft-Voting Ensemble** | **0.9910** | 0.8475 | **1.0000** | **0.9174** | 0.9982 |

#### TABLE V: Classifier Evaluation on Dataset C (External 191-Consumer Benchmark)
| Model Architecture | Accuracy | Precision | Recall | $F_1$-Score | AUC-ROC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Random Forest | 0.7436 | 0.7778 | 0.7000 | 0.7368 | **0.8026** |
| XGBoost | **0.8205** | **0.8421** | **0.8000** | **0.8205** | 0.7763 |
| Deep Neural Network (DNN) | 0.6154 | 0.6190 | 0.6500 | 0.6341 | 0.7368 |
| Long Short-Term Memory (LSTM) | 0.4872 | 0.5000 | 0.5500 | 0.5238 | 0.5316 |
| Isolation Forest | 0.4872 | 0.5000 | 0.1000 | 0.1667 | 0.5605 |
| **Soft-Voting Ensemble** | 0.7436 | 0.7500 | 0.7500 | 0.7500 | 0.7763 |

![Fig. 5. Multi-metric comparative performance bar chart across evaluated datasets.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig09_F1_Comparison_All_Datasets.png)  
*Fig. 5. Multi-metric comparative performance bar chart across Random Forest, XGBoost, DNN, LSTM, Isolation Forest, and Soft-Voting Ensemble.*

![Fig. 6. Performance breakdown on Dataset B.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig10_Performance_Bar_SmartMeter.png)  
*Fig. 6. Multi-metric performance breakdown for evaluated classifiers on Dataset B (Smart Meter with Weather Telemetry).*

### C. Cross-Validation and Statistical Stability
Because the holdout test partition on Dataset A represents 4 physical meters (32 profile instances: 4 normal, 28 theft), holdout metrics must be contextualized by comprehensive cross-validation. Five-fold cross-validation was conducted across all datasets, reporting sample standard deviation ($ddof=1$):
* **Dataset A (CEEW):** Evaluated via 5-fold `GroupKFold` cross-validation grouped strictly by base physical meter identifier (four distinct physical meters held out in each validation fold) with SMOTE applied strictly per training fold. Random Forest achieved fold $F_1$-scores of $[0.9492, 0.9492, 1.0000, 1.0000, 0.9630]$, producing a mean $F_1$-score of $0.9723 \pm 0.0259$ (sample SD; population SD: $\pm 0.0232$) and mean accuracy of $95.00\% \pm 4.74\%$. XGBoost achieved fold $F_1$-scores of $[0.9655, 0.9643, 1.0000, 1.0000, 0.9825]$, yielding a mean $F_1$-score of $0.9825 \pm 0.0176$ (sample SD; population SD: $\pm 0.0157$) and mean accuracy of $96.88\% \pm 3.12\%$.
* **Dataset B (Smart Meter + Weather):** Under 5-fold stratified cross-validation on 5,000 records, Random Forest achieved fold $F_1$-scores of $[0.9278, 0.8636, 0.8750, 0.8172, 0.8696]$, producing a mean $F_1$-score of $0.8706 \pm 0.0394$ and mean accuracy of $98.80\% \pm 0.35\%$. XGBoost achieved fold $F_1$-scores of $[0.9259, 0.8952, 0.8868, 0.9126, 0.8932]$, yielding a mean $F_1$-score of $0.9028 \pm 0.0161$ and mean accuracy of $98.98\% \pm 0.16\%$.
* **Dataset C (External Benchmark):** Under 5-fold stratified cross-validation on 191 consumer profiles, XGBoost achieved fold $F_1$-scores of $[0.7317, 0.7027, 0.7027, 0.8000, 0.6250]$, yielding a mean $F_1$-score of $0.7124 \pm 0.0630$ and mean accuracy of $72.25\% \pm 3.96\%$.

![Fig. 7. Fold-by-fold accuracy and F1-score stability across 5-fold cross-validation runs.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig12_Cross_Validation_Stability.png)  
*Fig. 7. Fold-by-fold accuracy and F1-score stability across 5-fold cross-validation runs.*

### D. ROC and Precision-Recall Dynamics
Fig. 8, 9, and 10 present Receiver Operating Characteristic (ROC) curves across all three datasets.
* On **Dataset A (CEEW)** (Fig. 8), tree-based models and the ensemble achieve high area under the curve (AUC = 1.0000). It should be noted that because the unseen holdout partition contains 4 genuine normal profiles, the empirical ROC curve exhibits step-like quantization, as each false positive shifts the False Positive Rate by 0.25.
* On **Dataset B (Smart Meter)** (Fig. 9), the Soft-Voting Ensemble sustains high precision (0.8475) while capturing all 50 anomalous instances (100% recall), achieving an AUC-ROC of 0.9982. Conversely, the DNN suffers from a low precision of 0.4949 despite a high recall of 0.9800, generating 50 false positives that would impose substantial field inspection overhead.
* On **Dataset C (External Benchmark)** (Fig. 10), performance degrades across all models (Ensemble AUC = 0.7763, F1 = 0.7500; LSTM AUC = 0.5316). This performance gap illustrates the domain shift encountered when evaluating algorithms on unconstrained, real-world utility audit records where theft patterns do not follow synthetic mathematical profiles.

![Fig. 8. ROC curves on Dataset A (CEEW).](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig03_ROC_Curve_CEEW_Dataset.png)  
*Fig. 8. Receiver Operating Characteristic (ROC) curves for evaluated classifiers on Dataset A (CEEW).*

![Fig. 9. ROC curves on Dataset B (Smart Meter).](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig04_ROC_Curve_SmartMeter_Dataset.png)  
*Fig. 9. Receiver Operating Characteristic (ROC) curves for evaluated classifiers on Dataset B (Smart Meter).*

![Fig. 10. ROC curves on Dataset C (External Benchmark).](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig05_ROC_Curve_GitHub_Dataset.png)  
*Fig. 10. Receiver Operating Characteristic (ROC) curves for evaluated classifiers on Dataset C (External Benchmark).*

### E. Confusion Matrix and Operational Dispatch
Table VI presents the operational confusion matrix breakdown for the Soft-Voting Ensemble on both CEEW (unseen meters holdout) and Smart Meter test sets:

#### TABLE VI: Operational Confusion Matrix Breakdown for Soft-Voting Ensemble
| Evaluation Partition | Actual Normal ($TN + FP$) | Actual Theft ($FN + TP$) | True Negatives ($TN$) | False Positives ($FP$) | False Negatives ($FN$) | True Positives ($TP$) | Honest Recall | Theft Recall | Precision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CEEW Holdout (32 profiles)** | 4 | 28 | 4 | 0 | 1 | 27 | 100.0% | 96.43% | **100.0%** |
| **Smart Meter Holdout (1,000 records)** | 950 | 50 | 941 | 9 | 0 | 50 | 99.05% | **100.0%** | 84.75% |

In utility operations, false positive dispatches incur direct labor expenses, while false negatives allow revenue leakage to persist unmitigated. On the CEEW holdout, the ensemble correctly classified all 4 normal profiles ($FP = 0$) and identified 27 of 28 theft profiles ($TP = 27, FN = 1$). While the zero false positive count on this 4-meter partition is promising, its statistical power is limited by the cohort size of holdout physical meters, underscoring the necessity of the 5-fold cross-validation results ($96.88\% \pm 3.12\%$ accuracy) reported in Section IV-C. On Dataset B, the ensemble achieved 100% theft recall (50/50 detected) while restricting false alarms to 9 out of 950 honest records (a 0.95% false alarm rate), yielding an $F_1$-score of 0.9174 that exceeds standalone XGBoost (0.9074).

![Fig. 11. Confusion matrix heatmap and operational error breakdown for the calibrated ensemble.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig06_Confusion_Matrix_Ensemble_CEEW.png)  
*Fig. 11. Confusion matrix heatmap and operational error breakdown for the calibrated ensemble on Dataset A.*

### F. Deep Learning vs Gradient Boosted Trees Benchmark
To evaluate whether deep sequence architectures justify their substantial training overhead compared to tree ensembles, we benchmarked a 1D Convolutional Neural Network (1D-CNN) against XGBoost on the benchmark dataset (Fig. 12). While the 1D-CNN achieved strong feature extraction from raw 1,034-day sequences (AUC = 0.81), XGBoost delivered higher classification $F_1$-score on the 39-instance test split (0.8205 vs 0.7780) while training in under 3 seconds compared to over 4 minutes for the deep network. On Dataset C, Random Forest secured the highest discriminative AUC-ROC (0.8026), while XGBoost delivered the highest classification accuracy (82.05%) and $F_1$-score (0.8205). These findings indicate that gradient boosted trees paired with structured feature engineering provide a highly competitive and computationally efficient solution for utility microservice deployment, though larger sequence cohorts may further benefit deep temporal architectures.

![Fig. 12. ROC comparison of a 1D-CNN and the XGBoost pipeline on the benchmark dataset.](file:///c:/Users/amans/OneDrive/Desktop/theif%20detection/paper_figures_final/Fig11_CNN_vs_XGBoost_Benchmark.png)  
*Fig. 12. ROC comparison of a 1D-CNN and the XGBoost pipeline on the benchmark dataset.*

### G. Explainable AI & Heuristic Fallback Engine
To convert model probabilities into actionable insights for field technicians, the framework embeds TreeSHAP feature attribution [33] alongside a physics-informed heuristic engine (Fig. 4). The top global discriminators identified by TreeSHAP for CEEW include `flat_line_score`, `peak_consumption_mean`, `night_day_ratio`, `bypass_ratio`, `zero_peak_ratio`, and `rolling_7d_trend`—features that directly capture the physical signatures of peak bypass ($T_1$), flatline spoofing ($T_2$), and current coil bypass ($T_6$). The heuristic engine independently checks for: (1) consumption drops below historical moving baselines, (2) voltage supply anomalies, (3) current-to-voltage divergence, (4) power factor deviations, (5) frequency boundary violations, (6) meter physical tamper flags, (7) load factor irregularities, and (8) prolonged zero-consumption intervals. This dual layer provides line technicians with transparent diagnostic explanations alongside model probability scores upon inspection dispatch.

### H. Limitations
Several limitations qualify the findings of this study:
1. **Synthetic Theft Profiles on Indian Telemetry:** While baseline CEEW smart meter data comprises authentic telemetry from Mathura and Bareilly, theft labels were generated using seven domain-specific injection formulations because Indian utility customer theft audit records are legally restricted under consumer privacy regulations. High separability on CEEW reflects the mathematical structure of these formulations; operational behavior under unconstrained human fraud is better reflected by Dataset C.
2. **Meter Cohort Scale:** The CEEW telemetry was collected across 20 monitored distribution nodes (160 profiles). While our `GroupShuffleSplit` and `GroupKFold` protocols strictly prevented meter-level leakage by holding out entire physical meters, future work must expand validation to larger cohorts across diverse distribution feeders.
3. **Tabular Representation in Recurrent Networks:** The LSTM model evaluated 47 engineered tabular features sequentially rather than processing multi-thousand-step raw time-series directly. This non-standard formulation accounts for its lower performance relative to tree ensembles on tabular benchmarks.
4. **Unsupervised Contamination Sensitivity:** Isolation Forest exhibited poor recall on CEEW (0.0357), illustrating that unsupervised anomaly detectors are sensitive to default contamination parameters when applied to multi-modal synthetic fraud distributions.

---

## V. CONCLUSION & FUTURE WORK

This paper presented an end-to-end electricity theft detection framework designed for advanced metering infrastructure operating under real-world grid conditions. By leveraging authentic field telemetry from the CEEW smart meter deployment in Uttar Pradesh, India alongside a weather-enriched smart meter dataset and an external inspection benchmark, we demonstrated that combining 47 domain-specific features with theft attack injection ($T_1$–$T_7$), leak-free meter-grouped partitioning, and SMOTE class balancing yields strong detection performance.

The proposed Soft-Voting Probability Ensemble achieved 96.88% accuracy, 100.0% precision, and an AUC-ROC of 1.0000 on unseen physical CEEW meters, and attained 99.10% accuracy, 100.0% recall, and 0.9174 $F_1$-score on the weather-enriched dataset. In rigorous 5-fold cross-validation, XGBoost demonstrated high stability across folds (mean $F_1 = 0.9825 \pm 0.0176$ on CEEW and $0.9028 \pm 0.0161$ on Smart Meter). Furthermore, integrating TreeSHAP attribution with a physics-informed heuristic engine addresses the operational "black box" challenge, enabling transparent field team dispatch through a production-grade microservice architecture.

Future work will focus on federated learning across multiple DISCOM jurisdictions to preserve inter-utility data privacy, as well as edge-computing deployment directly onto smart meter firmware for real-time anomaly detection.

---

## REFERENCES

1. S. S. S. R. Depuru, L. Wang, and V. Devabhaktuni, "Electricity theft: Overview, issues, prevention and a smart meter based approach to control theft," *Energy Policy*, vol. 39, no. 2, pp. 1007–1015, 2011, doi: 10.1016/j.enpol.2010.11.037.
2. X. Xia, Y. Xiao, W. Liang, and J. Cui, "Detection methods in smart meters for electricity thefts: A survey," *Proc. IEEE*, vol. 110, no. 2, pp. 273–319, Feb. 2022.
3. M. S. Saeed, M. W. Mustafa, N. N. Hamadneh, N. A. Alshammari, U. U. Sheikh, T. A. Jumani, S. B. A. Khalid, and I. Khan, "Detection of non-technical losses in power utilities—A comprehensive systematic review," *Energies*, vol. 13, no. 18, p. 4727, 2020.
4. M. G. Chuwa and F. Wang, "A review of non-technical loss attack models and detection methods in the smart grid," *Electric Power Systems Research*, vol. 199, p. 107415, 2021, doi: 10.1016/j.epsr.2021.107415.
5. T. Ahmad, "Non-technical loss analysis and prevention using smart meters," *Renewable and Sustainable Energy Reviews*, vol. 72, pp. 573–589, 2017.
6. F. de Souza Savian, J. C. M. Siluk, T. B. Garlet, F. M. do Nascimento, J. R. Pinheiro, and Z. Vale, "Non-technical losses: A systematic contemporary article review," *Renewable and Sustainable Energy Reviews*, vol. 147, p. 111205, 2021.
7. A. Althobaiti, A. Jindal, A. K. Marnerides, and U. Roedig, "Energy theft in smart grids: A survey on data-driven attack strategies and detection methods," *IEEE Access*, vol. 9, pp. 159291–159312, 2021.
8. J. Nagi, K. S. Yap, S. K. Tiong, S. K. Ahmed, and M. Mohamad, "Detection of Abnormalities and Electricity Theft using Genetic Support Vector Machines," in *Proc. IEEE TENCON 2011*, Bali, Indonesia, 2011, pp. 1–6, doi: 10.1109/TENCON.2011.6129308.
9. G. M. Messinis and N. D. Hatziargyriou, "Review of Non-Technical Loss Detection Methods," *Electric Power Systems Research*, vol. 158, pp. 250–266, 2018, doi: 10.1016/j.epsr.2018.01.005.
10. M. M. Buzau, J. Tejedor-Aguilera, P. Cruz-Romero, and A. Gómez-Expósito, "Detection of Non-Technical Losses Using Smart Meter Data and Supervised Learning," *IEEE Trans. Smart Grid*, vol. 10, no. 3, pp. 2661–2670, May 2019, doi: 10.1109/TSG.2018.2807925.
11. K. Zheng, Q. Chen, Y. Wang, C. Kang, and Q. Xia, "A Novel Combined Data-Driven Approach for Electricity Theft Detection," *IEEE Trans. Industrial Informatics*, vol. 15, no. 3, pp. 1809–1819, Mar. 2019, doi: 10.1109/TII.2018.2873814.
12. N. F. Avila, G. Figueroa, and C. C. Chu, "NTL Detection in Electric Distribution Systems Using the Maximal Overlap Discrete Wavelet-Packet Transform and Random Undersampling Boosting," *IEEE Trans. Power Systems*, vol. 33, no. 6, pp. 7171–7180, Nov. 2018, doi: 10.1109/TPWRS.2018.2853162.
13. S. Li, Y. Han, X. Yao, Y. Shen, J. Wang, and Q. Zhao, "Electricity Theft Detection in Power Grids with Deep Learning and Random Forests," *Journal of Electrical and Computer Engineering*, vol. 2019, Article ID 4136874, 2019, doi: 10.1155/2019/4136874.
14. M. N. Hasan, R. N. Toma, A. A. Nahid, M. M. M. Islam, and J.-M. Kim, "Electricity Theft Detection in Smart Grid Systems: A CNN–LSTM Based Approach," *Energies*, vol. 12, no. 17, p. 3310, 2019, doi: 10.3390/en12173310.
15. P. Jokar, N. Arianpoo, and V. C. M. Leung, "Electricity Theft Detection in AMI Using Customers' Consumption Patterns," *IEEE Trans. Smart Grid*, vol. 7, no. 1, pp. 216–226, Jan. 2016, doi: 10.1109/TSG.2015.2425222.
16. Z. Yan and H. Wen, "Electricity Theft Detection Base on Extreme Gradient Boosting in AMI," *IEEE Trans. Instrumentation and Measurement*, vol. 70, pp. 1–9, 2021.
17. S. Hussain, M. W. Mustafa, T. A. Jumani, S. K. Baloch, H. Alotaibi, I. Khan, and A. Khan, "A novel feature engineered-CatBoost-based supervised machine learning framework for electricity theft detection," *Energy Reports*, vol. 7, no. 12, pp. 4425–4436, 2021, doi: 10.1016/j.egyr.2021.07.008.
18. N. Javaid et al., "Non-technical losses detection using autoencoder and bidirectional gated recurrent unit to secure smart grids," *IEEE Access*, vol. 10, pp. 56863–56875, 2022.
19. N. Javaid, H. Gul, S. Baig, F. Shehzad, C. Xia, L. Guan, and T. Sultana, "Using GANCNN and ERNET for Detection of Non-Technical Losses to Secure Smart Grids," *IEEE Access*, vol. 9, pp. 98679–98700, 2021, doi: 10.1109/ACCESS.2021.3092645.
20. A. T. El-Toukhy, M. M. Badr, M. M. E. A. Mahmoud, G. Srivastava, M. M. Fouda, and M. Alsabaan, "Electricity Theft Detection Using Deep Reinforcement Learning in Smart Power Grids," *IEEE Access*, vol. 11, pp. 59558–59574, 2023, doi: 10.1109/ACCESS.2023.3284681.
21. M. Ismail, M. F. Shaaban, M. Naidu, and E. Serpedin, "Deep Learning Detection of Electricity Theft Cyber-Attacks in Renewable Distributed Generation," *IEEE Trans. Smart Grid*, vol. 11, no. 4, pp. 3428–3437, Jul. 2020.
22. A. Nawaz, T. Ali, G. Mustafa, S. U. Rehman, and M. R. Rashid, "A novel technique for detecting electricity theft in secure smart grids using CNN and XGBoost," *Intelligent Systems with Applications*, vol. 17, p. 200168, 2023, doi: 10.1016/j.iswa.2022.200168.
23. Z. A. Khan, M. Adil, N. Javaid, M. N. Saqib, M. Shafiq, and J.-G. Choi, "Electricity Theft Detection Using Supervised Learning Techniques on Smart Meter Data," *Sustainability*, vol. 12, no. 19, p. 8023, 2020, doi: 10.3390/su12198023.
24. R. Yadav and Y. Kumar, "Detection of non-technical losses in electric distribution network by applying machine learning and feature engineering," *Journal Européen des Systèmes Automatisés*, vol. 54, no. 3, pp. 487–493, 2021, doi: 10.18280/jesa.540312.
25. M. T. Quasim, K. Nisa, M. Z. Khan et al., "An internet of things enabled machine learning model for Energy Theft Prevention System (ETPS) in Smart Cities," *Journal of Cloud Computing*, vol. 12, p. 158, 2023, doi: 10.1186/s13677-023-00525-4.
26. N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, "SMOTE: Synthetic Minority Over-sampling Technique," *Journal of Artificial Intelligence Research*, vol. 16, pp. 321–357, 2002, doi: 10.1613/jair.953.
27. J. Davis and M. Goadrich, "The Relationship Between Precision-Recall and ROC Curves," in *Proc. 23rd Int. Conf. Machine Learning (ICML)*, Pittsburgh, PA, USA, 2006, pp. 233–240, doi: 10.1145/1143844.1143874.
28. L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001, doi: 10.1023/A:1010933404324.
29. T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, San Francisco, CA, USA, 2016, pp. 785–794, doi: 10.1145/2939672.2939785.
30. S. Hochreiter and J. Schmidhuber, "Long Short-Term Memory," *Neural Computation*, vol. 9, no. 8, pp. 1735–1780, 1997, doi: 10.1162/neco.1997.9.8.1735.
31. F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," in *Proc. 2008 8th IEEE Int. Conf. Data Mining (ICDM)*, Pisa, Italy, 2008, pp. 413–422, doi: 10.1109/ICDM.2008.17.
32. M. Abadi et al., "TensorFlow: A System for Large-Scale Machine Learning," in *Proc. 12th USENIX Symp. Operating Systems Design and Implementation (OSDI 16)*, Savannah, GA, USA, 2016, pp. 265–283.
33. S. M. Lundberg and S.-I. Lee, "A Unified Approach to Interpreting Model Predictions," in *Advances in Neural Information Processing Systems 30 (NIPS 2017)*, Long Beach, CA, USA, 2017, pp. 4765–4774.
34. F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
35. G. Lemaître, F. Nogueira, and C. K. Aridas, "Imbalanced-learn: A Python Toolbox to Tackle the Curse of Imbalanced Datasets in Machine Learning," *Journal of Machine Learning Research*, vol. 18, no. 17, pp. 1–5, 2017.
36. Council on Energy, Environment and Water (CEEW), "Smart Meter Data – Mathura and Bareilly, Uttar Pradesh," dataset, 2019–2021, Kaggle (user jehanbhathena). [Online]. Available: https://www.kaggle.com/datasets/jehanbhathena/smart-meter-data-mathura-and-bareilly (accessed Oct. 31, 2026).
37. vaishnavi-1, "Electricity-theft-detection-using-ML," GitHub repository. [Online]. Available: https://github.com/vaishnavi-1/Electricity-theft-detection-using-ML (accessed Oct. 31, 2026).
38. ziya07, "Smart Meter Electricity Consumption Dataset (labeled)," Kaggle dataset. [Online]. Available: https://www.kaggle.com/datasets/ziya07/smart-meter-electricity-consumption-dataset (accessed Oct. 31, 2026).
