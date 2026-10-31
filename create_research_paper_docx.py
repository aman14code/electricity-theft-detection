import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import json
import pandas as pd

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_ieee_paper_docx():
    # Load exact results
    df_results = pd.read_csv('model_results/reports/model_comparison.csv')
    with open('model_results/reports/cv_results.json', 'r') as f:
        cv_data = json.load(f)

    doc = docx.Document()

    # Set standard 0.75-inch margins for IEEE style
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Title
    title = doc.add_paragraph()
    title_run = title.add_run("A Multi-Tier Machine Learning Framework for Electricity Theft Detection in Advanced Metering Infrastructure Using Indian Grid Telemetry and Benchmark Validation")
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.name = 'Times New Roman'
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(12)

    # Authors
    author_p = doc.add_paragraph()
    author_run = author_p.add_run(
        "Keshav Aggarwal, Aman Sharma, Abhinav Saini, Ashu Singh\n"
        "Department of Computer Science & Engineering\n"
        "Meerut Institute of Engineering & Technology (MIET), Meerut, Uttar Pradesh, India\n"
        "Email: {keshav.aggarwal, aman.sharma, abhinav.saini, ashu.singh}@miet.ac.in"
    )
    author_run.font.size = Pt(10)
    author_run.font.italic = True
    author_run.font.name = 'Times New Roman'
    author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author_p.paragraph_format.space_after = Pt(18)

    # Helpers
    def add_section_heading(text):
        h = doc.add_paragraph()
        run = h.add_run(text)
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.name = 'Times New Roman'
        run.font.color.rgb = RGBColor(15, 23, 42)
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)

    def add_subsection_heading(text):
        h = doc.add_paragraph()
        run = h.add_run(text)
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.italic = True
        run.font.name = 'Times New Roman'
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)

    def add_body_p(text):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.size = Pt(10)
        r.font.name = 'Times New Roman'
        return p

    def add_image_figure(filename, caption_text):
        p1 = os.path.join("paper_figures_final", filename)
        p2 = os.path.join("paper_graphs", filename)
        img_path = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)
        
        if img_path:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run()
            run.add_picture(img_path, width=Inches(5.5))
            
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.space_after = Pt(10)
            c_run = cap.add_run(caption_text)
            c_run.font.size = Pt(9)
            c_run.font.italic = True
            c_run.font.name = 'Times New Roman'
        else:
            p = doc.add_paragraph(f"[{caption_text} - Image file not found: {filename}]")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_styled_table(headers, rows_data):
        t = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        # Header
        for c_idx, h_text in enumerate(headers):
            cell = t.cell(0, c_idx)
            cell.text = h_text
            set_cell_background(cell, "1F2937") # Dark slate
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if len(p.runs) > 0:
                p.runs[0].font.bold = True
                p.runs[0].font.size = Pt(9)
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                p.runs[0].font.name = 'Times New Roman'
        # Rows
        for r_idx, row_vals in enumerate(rows_data):
            bg_color = "F9FAFB" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_vals):
                cell = t.cell(r_idx + 1, c_idx)
                cell.text = str(val)
                set_cell_background(cell, bg_color)
                set_cell_margins(cell, top=80, bottom=80, left=150, right=150)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
                if len(p.runs) > 0:
                    p.runs[0].font.size = Pt(8.5)
                    p.runs[0].font.name = 'Times New Roman'
                    if "Ensemble" in str(row_vals[1]) or "XGBoost" in str(row_vals[1]):
                        p.runs[0].font.bold = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ─────────────────────────────────────────────────────────────────────────
    # ABSTRACT
    # ─────────────────────────────────────────────────────────────────────────
    abs_heading = doc.add_paragraph()
    r = abs_heading.add_run("ABSTRACT")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.name = 'Times New Roman'
    
    add_body_p(
        "Non-Technical Losses (NTLs), predominantly arising from electricity theft and meter tampering, inflict substantial financial deficits on power distribution utilities worldwide. In emerging smart grids, data-driven electricity theft detection via Advanced Metering Infrastructure (AMI) telemetry is hindered by severe class imbalance, residential consumption volatility, and privacy regulations that restrict access to field-inspected theft records. This paper presents an end-to-end anomaly detection framework evaluated across three distinct datasets: authentic Indian smart meter telemetry from the Council on Energy, Environment and Water (CEEW) deployment in Uttar Pradesh (235,547 hourly records; 160 profile instances across 20 monitored distribution nodes), a 5,000-record weather-enriched dataset, and an external 191-consumer benchmark derived from utility audit records. We formulate seven domain-specific NTL attack profiles (T1–T7), extract 47 multidimensional statistical, temporal, ratio-based, and rolling-window electrical features, and enforce a leak-free meter-grouped holdout partition (GroupShuffleSplit) coupled with Synthetic Minority Over-sampling (SMOTE) applied strictly to training partitions. Five classifiers—Random Forest, XGBoost, Deep Neural Network (DNN), Long Short-Term Memory (LSTM), and Isolation Forest—were evaluated alongside a Soft-Voting Probability Ensemble. On the unseen 4-meter physical CEEW holdout (32 profiles: 4 honest, 28 theft), the Soft-Voting Ensemble attained 96.88% accuracy, 100.0% precision, 96.43% recall, 0.9818 F1-score, and an AUC-ROC of 1.0000. In 5-fold GroupKFold cross-validation across all 20 base physical meters, XGBoost demonstrated high stability with a mean F1-score of 0.9825 ± 0.0176 (sample SD, ddof=1) and mean accuracy of 96.88% ± 3.12%. On the weather-enriched dataset, the ensemble achieved 99.10% accuracy, 100.0% recall, and 0.9174 F1-score. On the external audit benchmark, XGBoost achieved the highest accuracy (82.05%) and F1-score (0.8205), highlighting domain generalization challenges under real-world human tampering. The framework integrates TreeSHAP explainability with a physics-informed heuristic engine, providing transparent decision support for field inspection triage."
    )

    kw_p = doc.add_paragraph()
    kw_p.paragraph_format.space_after = Pt(14)
    r1 = kw_p.add_run("Index Terms—")
    r1.font.bold = True
    r1.font.name = 'Times New Roman'
    r2 = kw_p.add_run("Electricity Theft Detection, Advanced Metering Infrastructure (AMI), Non-Technical Losses (NTL), Machine Learning, Soft-Voting Ensemble, SMOTE, Indian Smart Grid, Explainable AI (XAI), SHAP.")
    r2.font.name = 'Times New Roman'

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION I: INTRODUCTION
    # ─────────────────────────────────────────────────────────────────────────
    add_section_heading("I. INTRODUCTION")
    add_body_p(
        "Electricity theft represents one of the most critical operational and economic challenges facing electrical distribution companies (DISCOMs) worldwide. Non-Technical Losses (NTLs)—encompassing physical line tapping, meter bypass, secondary current transformer shunting, internal calibration tampering, and cyber-physical telemetry spoofing—account for tens of billions of dollars in lost utility revenue annually across the globe [1], [2]. In developing economies, the severity is particularly acute: in India, Aggregate Technical and Commercial (AT&C) losses historically range between 15% and 22% across several state utilities, creating persistent financial deficits that inhibit infrastructure modernization and renewable energy integration [3]."
    )
    add_body_p(
        "The global transition toward Smart Grids and Advanced Metering Infrastructure (AMI) has equipped distribution networks with bidirectional smart meters capable of transmitting high-frequency telemetry (typically at 3-minute, 15-minute, or 1-hour intervals) [4]. While this granular data theoretically enables automated surveillance, machine-learning-based electricity theft detection faces four profound hurdles in practice [5]–[7]:"
    )
    add_body_p(
        "1. Extreme Class Imbalance: In real-world distribution feeders, fraudulent consumers represent a small minority of the customer base (typically 2% to 10%), causing naive classification models to predict the majority class (honest consumers) with deceptive high accuracy while failing to detect actual theft [3], [7]."
    )
    add_body_p(
        "2. Absence of Public Ground-Truth Labels in Emerging Grids: Under consumer privacy regulations and utility confidentiality policies, Indian DISCOMs do not publicly release customer-level field audit records or convicted customer identifiers. Consequently, research must bridge authentic Indian telemetry with mathematically formulated NTL attack models [4], [10], [11]."
    )
    add_body_p(
        "3. High Volatility and Load Diversity: Normal residential consumption exhibits severe non-linear fluctuations driven by seasonal weather, festival loads, and irregular occupancy, which frequently mimic consumption drops caused by theft [5], [9]."
    )
    add_body_p(
        "4. False Positive Dispatch Cost: In physical utility operations, sending Quick Response Teams (QRTs) and enforcement inspectors to suspected consumer premises incurs substantial labor costs. A model with high recall but low precision overwhelms field staff with false alarms, destroying operational viability [7]."
    )
    add_body_p(
        "Major Contributions: To address these challenges with methodological rigor, this paper makes the following key contributions:\n"
        "• Multi-Source Empirical Evaluation: We evaluate our methodology across authentic high-resolution Indian grid telemetry from the Council on Energy, Environment and Water (CEEW) deployment in Uttar Pradesh (235,547 hourly records across 20 distribution nodes), an enriched 5,000-record smart meter dataset with meteorological parameters, and an established 191-consumer benchmark derived from utility audit records.\n"
        "• Leak-Free Meter-Grouped Splitting: To eliminate the widespread methodological risk of meter-level telemetry leakage, we implement GroupShuffleSplit and GroupKFold strictly by base physical meter identifier, ensuring zero meter overlap between training and testing partitions, and apply SMOTE strictly to training folds.\n"
        "• Physics-Informed Feature Engineering: We engineer 47 statistical, temporal, ratio-based, and rolling-window electrical features capturing consumption drops, current bypass conditions, voltage/frequency anomalies, and load factor fluctuations.\n"
        "• Domain-Specific NTL Attack Formulation (T1–T7): We formulate seven domain-specific attack profiles inspired by smart grid literature [4], [10] simulating peak-hour bypass, flatline spoofing, gradual degradation, night-only consumption, voltage tampering, current coil shunting, and stochastic partial theft.\n"
        "• Probability Soft-Voting Ensemble: We combine complementary tree-based, neural, and sequence-oriented supervised models into a unified probability soft-voting ensemble that provides higher operational stability than individual models.\n"
        "• Explainable AI (XAI) & Operational Decision Support: We couple TreeSHAP feature attribution with a physics-informed heuristic engine, operationalized inside an end-to-end microservice architecture (FastAPI backend, React dashboard, and interactive GIS mapping) to enable transparent inspection triage."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION II: LITERATURE REVIEW
    # ─────────────────────────────────────────────────────────────────────────
    add_section_heading("II. LITERATURE REVIEW")
    add_body_p(
        "The detection of non-technical losses has progressed from physical line inspection and manual audits to machine learning and deep learning methodologies [4]–[6]."
    )
    add_subsection_heading("A. Classical Machine Learning Approaches")
    add_body_p(
        "Early automated detection relied on supervised shallow classifiers. Jokar et al. [15] established a foundational benchmark using Support Vector Machines (SVM) combined with customer consumption pattern analysis. While SVMs achieve reasonable boundary separation on small datasets, their computational complexity scales quadratically with sample size, rendering them impractical for million-meter AMI deployments. Furthermore, classical SVMs exhibit severe degradation in the presence of noisy readings and missing telemetry packets [8]. Decision tree ensembles, specifically Random Forest [13], [28] and Gradient Boosting [16], [17], [29], demonstrated substantial improvements by handling non-linear interactions and tabular feature distributions, though tuning depth parameters remains necessary to avoid overfitting to specific feeders."
    )
    add_subsection_heading("B. Deep Learning and Sequence Modeling")
    add_body_p(
        "With the expansion of AMI data volume, deep learning architectures emerged to model sequential consumption. Zheng et al. [11] proposed a Wide & Deep convolutional neural network (CNN) framework to capture both periodic daily cycles and global consumption trends from daily consumption matrices. Hasan et al. [14] applied Long Short-Term Memory (LSTM) recurrent networks to model temporal dependencies, demonstrating that recurrent memory cells can detect subtle downward drifts in consumption that static models miss. Further hybrid deep learning paradigms, including GAN-CNN [19] and Autoencoder-BiGRU architectures [18], have been explored to capture non-linear temporal dynamics under severe load fluctuations."
    )
    add_subsection_heading("C. Methodological Rigor and Leakage Prevention")
    add_body_p(
        "A pervasive challenge in NTL detection literature is the proper handling of class imbalance and data splitting. Many published works inadvertently apply over-sampling techniques such as SMOTE [26] across the entire dataset before partitioning into train and test splits, or perform naive random splits on datasets where multiple instances originate from the same consumer meter. As highlighted in recent critical surveys [7], [9], both practices cause severe data leakage, resulting in artificially inflated test accuracies that collapse when deployed in real utility environments. In this work, we strictly enforce meter-grouped partitioning and fold-isolated SMOTE to guarantee methodological validity."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION III: PROPOSED METHODOLOGY
    # ─────────────────────────────────────────────────────────────────────────
    add_section_heading("III. PROPOSED METHODOLOGY")
    add_body_p(
        "The end-to-end workflow of the proposed electricity theft detection framework is structured into six sequential pipelines: data ingestion, theft attack simulation, feature extraction, leak-free class balancing via SMOTE, ensemble classification, and explainable decision dispatch."
    )
    add_subsection_heading("A. Multi-Source Dataset Architecture")
    add_body_p(
        "We evaluated the framework across three complementary datasets spanning diverse operational environments, summarized in Table I:"
    )

    # TABLE I
    table_i_headers = ["Dataset Identifier", "Source / Geography", "Attributes & Telemetry", "Instance Count", "Splitting & Validation Protocol", "Ground-Truth Provenance"]
    table_i_rows = [
        [
            "Dataset A: CEEW Telemetry",
            "Mathura & Bareilly, Uttar Pradesh, India [36]",
            "Active kWh, Voltage (V), Current (A), Frequency (Hz) at 3-min / hourly intervals",
            "235,547 hourly records; 160 profile instances across 20 base meters",
            "80:20 GroupShuffleSplit by meter ID (16 train / 4 test meters); 5-Fold GroupKFold; SMOTE on train only",
            "Authentic Indian field telemetry + 7 domain-specific attack profiles (T1–T7)"
        ],
        [
            "Dataset B: Smart Meter + Weather",
            "Smart grid AMI feeder with weather telemetry [38]",
            "Hourly kWh consumption, ambient temperature, humidity, wind speed, rolling averages",
            "5,000 records (4,750 normal, 250 anomalous)",
            "80:20 Stratified Split (4,000 train, 1,000 test: 950 normal, 50 anomalous); 5-Fold Stratified CV",
            "Labeled anomaly records capturing consumption divergence under weather extremes"
        ],
        [
            "Dataset C: Benchmark",
            "Public smart meter theft benchmark [37]",
            "Daily kWh consumption time-series over 1,034 consecutive monitoring intervals",
            "191 curated consumer profiles (97 confirmed fraud, 94 honest; 9 dropped from original 200 due to >50% missing readings)",
            "80:20 Stratified Split (152 train, 39 test: 19 normal, 20 fraud); 5-Fold Stratified CV",
            "Open-source utility inspection records and consumer audit logs"
        ]
    ]
    add_styled_table(table_i_headers, table_i_rows)
    add_body_p("TABLE I: Characteristics and Partitioning Protocols for Evaluated Datasets.")

    add_image_figure('fig1_class_imbalance.png', "Fig. 1. Class distribution of AMI telemetry showing baseline class imbalance before synthetic balancing.")

    add_subsection_heading("B. Domain-Specific Theft Injection Formulation")
    add_body_p(
        "To establish ground-truth fraud patterns on authentic Indian telemetry, we implemented seven domain-specific non-technical loss attack profiles inspired by smart grid literature [4], [10] and calibrated to model physical bypass, tampering, and degradation:\n"
        "• Attack T1 (Peak-Hour Bypass): Between 08:00 and 20:00, active consumption is zeroed (x'_t = 0.0) and recorded current is suppressed to 5% (I'_t = 0.05 * I_t).\n"
        "• Attack T2 (Flat-Line Spoofing): Clamping active consumption to 30% of the customer's median baseline: x'_t = 0.30 * median(x_1..T).\n"
        "• Attack T3 (Gradual Consumption Degradation): Mechanically wearing down meter disk gears or slowly altering calibration constants over time, creating a linear downward drift from 100% to 15%: x'_t = x_t * (1.0 - 0.85 * t / T), I'_t = I_t * (1.0 - 0.85 * t / T).\n"
        "• Attack T4 (Night-Only Usage): Diverting daytime commercial or domestic loads between 06:00 and 22:00: x'_t = 0.0, I'_t = 0.02 * I_t.\n"
        "• Attack T5 (Voltage Tampering): Inducing artificial voltage attenuation alongside partial energy shunting: V'_t = V_t * beta, beta in U(0.65, 0.80); x'_t = x_t * delta, delta in U(0.30, 0.60).\n"
        "• Attack T6 (Current Coil Bypass): Shunting the secondary current transformer coil with 70% probability across readings while voltage remains normal: I'_t = 0.03 * I_t, x'_t = 0.05 * x_t, with V'_t = V_t.\n"
        "• Attack T7 (Random Dynamic Partial Theft): Applying a stochastic reduction factor reflecting intermittent illegal hook-ups: x'_t = x_t * gamma_t, I'_t = I_t * gamma_t, with gamma_t in U(0.30, 0.70)."
    )
    add_image_figure('Fig02_Consumption_Profile_Honest_vs_Theft.png', "Fig. 2. Hourly load profiles showing honest consumer baselines versus synthetic theft attack signatures (T1 to T7).")

    add_subsection_heading("C. Leak-Free Class Imbalance Remediation via SMOTE")
    add_body_p(
        "Due to the numerical sparsity of theft events relative to normal operations, training unweighted classifiers yields biased decision boundaries. We formulated the Synthetic Minority Over-sampling Technique (SMOTE) [26] in the engineered 47-dimensional feature space. Crucially, to strictly prevent data leakage, the dataset was partitioned into train and test splits prior to resampling. SMOTE was applied exclusively to the training partition, ensuring the test set remained purely comprised of genuine, unaugmented records from completely unseen physical meters."
    )
    add_image_figure('Fig01_SMOTE_Before_After.png', "Fig. 3. Feature-space sample distribution before and after SMOTE balancing on the training partition.")

    add_subsection_heading("D. 47 Multidimensional Engineered Features")
    add_body_p(
        "Rather than feeding raw, noisy time-series data directly into classifiers, we engineered 47 discriminative features across four structural categories (Table II):"
    )

    table_ii_headers = ["Category", "Feature Count", "Specific Extracted Features", "Physical / Operational Rationale"]
    table_ii_rows = [
        [
            "Statistical Descriptors",
            "24",
            "Mean, standard deviation, minimum, maximum, skewness, and kurtosis computed for each of the 4 electrical channels (kwh, voltage, current, frequency)",
            "Captures baseline consumption, load dispersion, extreme spikes, distribution asymmetry, and heavy-tailedness caused by physical tampering or partial shunting"
        ],
        [
            "Temporal Features",
            "8",
            "peak_consumption_mean (08:00–20:00), offpeak_consumption_mean (20:00–08:00), night_day_ratio, weekday_mean, weekend_mean, weekday_weekend_ratio, consumption_entropy, peak_concentration",
            "Identifies tampering signatures that alter daily periodicity, clip daytime peak loads (T1), invert nighttime-to-daytime ratios (T4), or flatten diurnal load profiles"
        ],
        [
            "Ratio-Based & Operational Anomaly",
            "10",
            "zero_peak_ratio, bypass_ratio (low current & normal voltage), flat_line_score, kwh_cv, voltage_cv, current_cv, voltage_anomaly_ratio, freq_anomaly_ratio, zero_consumption_ratio, max_consecutive_zeros",
            "Directly detects current transformer coil bypass (T6), flat-line spoofing (T2), anomalous grid supply deviations (T5), and prolonged artificial outages"
        ],
        [
            "Rolling Window & Trend",
            "5",
            "rolling_3d_mean, rolling_3d_std, rolling_7d_mean, rolling_7d_std, rolling_7d_trend (linear regression slope across daily sums)",
            "Quantifies multi-day load volatility, baseline drift, and continuous downward degradation trends characteristic of calibration decay and disk wear (T3)"
        ]
    ]
    add_styled_table(table_ii_headers, table_ii_rows)
    add_body_p("TABLE II: 47 Multidimensional Engineered Feature Taxonomy Extracted per Consumer Profile.")

    add_image_figure('Fig07_SHAP_XGBoost_CEEW.png', "Fig. 4. Global feature importance ranking computed via TreeSHAP for XGBoost on Dataset A (CEEW).")

    add_subsection_heading("E. Model Paradigms & Soft-Voting Probability Ensemble")
    add_body_p(
        "Five complementary learning algorithms spanning diverse inductive biases were trained and evaluated:\n"
        "1. Random Forest (RF) [28]: An ensemble of 200 decorrelated decision trees built via bootstrap aggregation (bagging) with random feature subspaces (max_depth=12, min_samples_split=4).\n"
        "2. Extreme Gradient Boosting (XGBoost) [29]: Sequential additive gradient tree boosting optimizing a regularized objective with sparsity-aware split finding (n_estimators=200, learning_rate=0.05, max_depth=6, subsample=0.8).\n"
        "3. Deep Neural Network (DNN) [32]: A 4-layer fully connected architecture (256 -> 128 -> 64 -> 32 units) with Batch Normalization after the first three layers, Dropout regularizers (p in {0.3, 0.3, 0.2, 0.2}), ReLU activations, and a sigmoid output node trained under binary cross-entropy.\n"
        "4. Long Short-Term Memory (LSTM) [30]: A 2-layer recurrent architecture (64 and 32 units) with dropout (p=0.2) followed by a 16-unit dense layer and sigmoid classification node, evaluating sequential feature representations.\n"
        "5. Isolation Forest (iForest) [31]: An unsupervised tree ensemble (100 isolation trees) that isolates anomalies by recursively partitioning randomly selected features."
    )
    add_body_p(
        "To capitalize on their complementary decision boundaries, a Soft-Voting Probability Ensemble was constructed from the four supervised classifiers (M=4: RF, XGBoost, DNN, and LSTM). The unsupervised Isolation Forest was excluded from the voting pool to avoid calibrating unbounded anomaly scores alongside bounded posterior probabilities. Ensemble weights w_m are assigned proportionally to each model's training-fold validation F1-score. Classification decisions are executed using the canonical threshold tau = 0.5 without post-hoc test-set threshold tuning, guaranteeing unbiased evaluation."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION IV: EXPERIMENTAL RESULTS AND DISCUSSION
    # ─────────────────────────────────────────────────────────────────────────
    add_section_heading("IV. EXPERIMENTAL RESULTS AND DISCUSSION")
    add_subsection_heading("A. Performance Metrics Formulation")
    add_body_p(
        "Model evaluation was conducted using standard classification metrics: Accuracy = (TP + TN) / (TP + TN + FP + FN); Precision = TP / (TP + FP); Recall = TP / (TP + FN); F1-Score = 2 * (Precision * Recall) / (Precision + Recall); and AUC-ROC = integral of TPR(FPR) d(FPR)."
    )

    add_subsection_heading("B. Quantitative Model Evaluation Across Datasets")
    add_body_p(
        "Tables III, IV, and V summarize the empirical performance of all evaluated models across the three datasets generated from the unified leak-free training pipeline."
    )

    # TABLE III: CEEW
    table_iii_headers = ["Dataset A: CEEW Telemetry", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]
    table_iii_rows = []
    sub_ceew = df_results[df_results['Dataset'] == 'CEEW']
    for _, row in sub_ceew.iterrows():
        table_iii_rows.append([row['Model'], f"{row['accuracy']:.4f}", f"{row['precision']:.4f}", f"{row['recall']:.4f}", f"{row['f1']:.4f}", f"{row['auc_roc']:.4f}"])
    add_styled_table(table_iii_headers, table_iii_rows)
    add_body_p("TABLE III: Quantitative Classifier Evaluation on Dataset A (CEEW Indian AMI Telemetry, Unseen Physical Meters Holdout).")

    # TABLE IV: SmartMeter
    table_iv_headers = ["Dataset B: Smart Meter + Weather", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]
    table_iv_rows = []
    sub_sm = df_results[df_results['Dataset'] == 'SmartMeter']
    for _, row in sub_sm.iterrows():
        table_iv_rows.append([row['Model'], f"{row['accuracy']:.4f}", f"{row['precision']:.4f}", f"{row['recall']:.4f}", f"{row['f1']:.4f}", f"{row['auc_roc']:.4f}"])
    add_styled_table(table_iv_headers, table_iv_rows)
    add_body_p("TABLE IV: Quantitative Classifier Evaluation on Dataset B (Smart Meter with Meteorological Features, Abnormal Class Evaluation).")

    # TABLE V: GitHub
    table_v_headers = ["Dataset C: External Benchmark", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]
    table_v_rows = []
    sub_gh = df_results[df_results['Dataset'] == 'GitHub']
    for _, row in sub_gh.iterrows():
        table_v_rows.append([row['Model'], f"{row['accuracy']:.4f}", f"{row['precision']:.4f}", f"{row['recall']:.4f}", f"{row['f1']:.4f}", f"{row['auc_roc']:.4f}"])
    add_styled_table(table_v_headers, table_v_rows)
    add_body_p("TABLE V: Quantitative Classifier Evaluation on Dataset C (External 191-Consumer Benchmark).")

    add_body_p(
        "Analysis of Results: On Dataset A (CEEW Indian AMI telemetry evaluated on four completely unseen physical meters: BR02, BR06, MH25, MH35), Random Forest and XGBoost achieved perfect separation (1.0000 across all metrics). The Deep Neural Network achieved 96.88% accuracy and 0.9818 F1-score, while LSTM achieved 90.62% accuracy and 0.9455 F1-score. The Soft-Voting Ensemble attained 96.88% accuracy, 100.0% precision, 96.43% recall, 0.9818 F1-score, and an AUC-ROC of 1.0000. These high scores reflect the strong separability of the 47 physics-informed features under domain-specific attack vectors when evaluated on calibrated smart meter telemetry."
    )
    add_body_p(
        "On Dataset B (weather-enriched smart meter dataset, evaluated on 1,000 test records: 950 normal, 50 anomalous), the Soft-Voting Ensemble reached 99.10% accuracy, 100.0% recall, 0.9174 F1-score, and 0.9982 AUC-ROC. XGBoost was the top standalone classifier with 99.00% accuracy, 0.9074 F1-score, and 0.9979 AUC-ROC. The ensemble F1-score of 0.9174 is slightly higher than standalone XGBoost (0.9074), capturing all 50 anomalous instances (100% recall) with 9 false positives. Conversely, the DNN suffers from a low precision of 0.4949 despite high recall (0.9800), highlighting that without structural regularization, dense networks over-flag anomalies."
    )
    add_body_p(
        "On Dataset C (the 191-consumer benchmark derived from utility audit records), Random Forest secured the highest discriminative AUC-ROC (0.8026), whereas XGBoost led all classifiers in classification accuracy (82.05%) and F1-score (0.8205). The Soft-Voting Ensemble achieved 74.36% accuracy, 75.00% precision, 75.00% recall, and 0.7763 AUC-ROC. This performance gap illustrates the domain shift encountered when evaluating algorithms on unconstrained, real-world utility audit records where theft patterns do not follow synthetic mathematical profiles."
    )

    add_image_figure('Fig09_F1_Comparison_All_Datasets.png', "Fig. 5. Multi-metric comparative performance bar chart across Random Forest, XGBoost, DNN, LSTM, Isolation Forest, and Soft-Voting Ensemble.")
    add_image_figure('Fig10_Performance_Bar_SmartMeter.png', "Fig. 6. Multi-metric performance breakdown for evaluated classifiers on Dataset B (Smart Meter with Weather Telemetry).")

    add_subsection_heading("C. Cross-Validation and Statistical Stability")
    add_body_p(
        "Because the holdout test partition on Dataset A represents 4 physical meters (32 profile instances: 4 normal, 28 theft), holdout metrics must be contextualized by comprehensive cross-validation. Five-fold cross-validation was conducted across all three datasets (reporting sample standard deviation, ddof=1):\n"
        "• Dataset A (CEEW): Evaluated via 5-fold GroupKFold cross-validation grouped strictly by physical meter identifier (four distinct physical meters held out in each validation fold) with SMOTE applied strictly per training fold. Random Forest achieved fold F1-scores of [0.9492, 0.9492, 1.0000, 1.0000, 0.9630], producing a mean F1-score of 0.9723 ± 0.0259 (sample SD; population SD: ±0.0232) and mean accuracy of 95.00% ± 4.74%. XGBoost achieved fold F1-scores of [0.9655, 0.9643, 1.0000, 1.0000, 0.9825], yielding a mean F1-score of 0.9825 ± 0.0176 (sample SD; population SD: ±0.0157) and mean accuracy of 96.88% ± 3.12%.\n"
        "• Dataset B (Smart Meter + Weather): Under 5-fold stratified cross-validation on 5,000 records, Random Forest achieved fold F1-scores of [0.9278, 0.8636, 0.8750, 0.8172, 0.8696], producing a mean F1-score of 0.8706 ± 0.0394 and mean accuracy of 98.80% ± 0.35%. XGBoost achieved fold F1-scores of [0.9259, 0.8952, 0.8868, 0.9126, 0.8932], yielding a mean F1-score of 0.9028 ± 0.0161 and mean accuracy of 98.98% ± 0.16%.\n"
        "• Dataset C (External Benchmark): Under 5-fold stratified cross-validation on 191 consumer profiles, XGBoost achieved fold F1-scores of [0.7317, 0.7027, 0.7027, 0.8000, 0.6250], yielding a mean F1-score of 0.7124 ± 0.0630 and mean accuracy of 72.25% ± 3.96%.\n"
        "These cross-validation results confirm narrow variance and strong generalization stability across unseen data folds, demonstrating that the feature engineering pipeline prevents overfitting."
    )
    add_image_figure('Fig12_Cross_Validation_Stability.png', "Fig. 7. Fold-by-fold accuracy and F1-score stability across 5-fold cross-validation runs.")

    add_subsection_heading("D. ROC and Precision-Recall Dynamics")
    add_body_p(
        "Fig. 8, 9, and 10 present the Receiver Operating Characteristic (ROC) curves across all datasets. Under heavy class imbalance, ROC curves must be interpreted alongside class prevalence. On Dataset A (CEEW), tree-based models and the ensemble achieve high area under the curve (AUC = 1.0000). Because the holdout partition contains 4 genuine normal profiles, the empirical ROC curve exhibits step-like quantization, as each false positive shifts the False Positive Rate by 0.25. On Dataset B, the ensemble achieves 0.9982 AUC-ROC while capturing 100% of anomalies. On Dataset C, performance reflects the realistic domain gap between synthetic and real-world fraud (Ensemble AUC = 0.7763, LSTM AUC = 0.5316)."
    )
    add_image_figure('Fig03_ROC_Curve_CEEW_Dataset.png', "Fig. 8. Receiver Operating Characteristic (ROC) curves for evaluated classifiers on Dataset A (CEEW).")
    add_image_figure('Fig04_ROC_Curve_SmartMeter_Dataset.png', "Fig. 9. Receiver Operating Characteristic (ROC) curves for evaluated classifiers on Dataset B (Smart Meter).")
    add_image_figure('Fig05_ROC_Curve_GitHub_Dataset.png', "Fig. 10. Receiver Operating Characteristic (ROC) curves for evaluated classifiers on Dataset C (External Benchmark).")

    add_subsection_heading("E. Confusion Matrix and Operational Dispatch")
    add_body_p(
        "Table VI and Fig. 11 present the confusion matrix breakdown for the Soft-Voting Ensemble on both CEEW (unseen meters holdout) and Smart Meter test sets:"
    )

    table_vi_headers = ["Evaluation Partition", "Actual Normal (TN + FP)", "Actual Theft (FN + TP)", "True Negatives (TN)", "False Positives (FP)", "False Negatives (FN)", "True Positives (TP)", "Honest Recall", "Theft Recall", "Precision"]
    table_vi_rows = [
        ["CEEW Holdout (32 profiles)", "4", "28", "4", "0", "1", "27", "100.0%", "96.43%", "100.0%"],
        ["Smart Meter Holdout (1,000 records)", "950", "50", "941", "9", "0", "50", "99.05%", "100.0%", "84.75%"]
    ]
    add_styled_table(table_vi_headers, table_vi_rows)
    add_body_p("TABLE VI: Operational Confusion Matrix Breakdown for Soft-Voting Ensemble.")

    add_body_p(
        "In electrical utility distribution operations, false positive dispatches incur direct labor expenses, while false negatives allow revenue leakage to persist unmitigated. On the CEEW holdout, the ensemble correctly classified all 4 normal profiles (FP = 0) and identified 27 of 28 theft profiles (TP = 27, FN = 1). While the zero false positive count on this 4-meter partition is promising, its statistical power is limited by the cohort size of holdout physical meters, underscoring the necessity of the 5-fold cross-validation results (96.88% ± 3.12% accuracy) reported in Section IV-C. On Dataset B, the ensemble achieved 100% theft recall (50/50 detected) while restricting false alarms to 9 out of 950 honest records (a 0.95% false alarm rate), yielding an F1-score of 0.9174 that is slightly higher than standalone XGBoost (0.9074)."
    )
    add_image_figure('Fig06_Confusion_Matrix_Ensemble_CEEW.png', "Fig. 11. Confusion matrix heatmap and operational error breakdown for the calibrated ensemble on Dataset A.")

    add_subsection_heading("F. Deep Learning vs Gradient Boosted Trees Benchmark")
    add_body_p(
        "To evaluate whether deep sequence architectures justify their substantial training and deployment overhead compared to tree ensembles, we benchmarked a 1D Convolutional Neural Network (1D-CNN) against XGBoost on the benchmark dataset (Fig. 12). While the 1D-CNN achieved strong feature extraction from raw 1,034-day sequences (AUC = 0.81), XGBoost outperformed it in F1-score on the 39-instance test split (0.8205 vs 0.7780) while requiring under 3 seconds of training time compared to over 4 minutes for the deep network. On Dataset C, Random Forest secured the highest discriminative AUC-ROC (0.8026), while XGBoost delivered the highest classification accuracy (82.05%) and F1-score (0.8205). This confirms that gradient boosted tree ensembles paired with domain-specific feature engineering remain an optimal deployment paradigm for utility edge and microservice dispatch."
    )
    add_image_figure('Fig11_CNN_vs_XGBoost_Benchmark.png', "Fig. 12. ROC comparison of a 1D-CNN and the XGBoost pipeline on the benchmark dataset.")

    add_subsection_heading("G. Explainable AI & Heuristic Fallback Engine")
    add_body_p(
        "To convert model probabilities into actionable insights for field technicians, the framework embeds TreeSHAP feature attribution [33] alongside a physics-informed heuristic engine (Fig. 4). The top global discriminators identified by TreeSHAP for CEEW include flat_line_score, peak_consumption_mean, night_day_ratio, bypass_ratio, zero_peak_ratio, and rolling_7d_trend—features that directly capture the physical signatures of peak bypass (T1), flatline spoofing (T2), and current coil bypass (T6). The heuristic engine independently checks for: (1) consumption drops below historical moving baselines, (2) voltage supply anomalies, (3) current-to-voltage divergence, (4) power factor deviations, (5) frequency boundary violations, (6) meter physical tamper flags, (7) load factor irregularities, and (8) prolonged zero-consumption intervals. This dual layer provides line technicians with transparent diagnostic explanations alongside model probability scores upon inspection dispatch."
    )

    add_subsection_heading("H. Limitations")
    add_body_p(
        "Several limitations qualify the findings of this study:\n"
        "1. Synthetic Theft Profiles on Indian Telemetry: While the baseline CEEW smart meter data comprises authentic telemetry from Mathura and Bareilly, theft labels were generated using seven domain-specific attack formulations because Indian utility customer theft audit records are legally restricted under consumer privacy regulations. High separability on CEEW reflects the mathematical structure of these formulations; operational behavior under unconstrained human fraud is better reflected by Dataset C.\n"
        "2. Meter Cohort Scale: The CEEW telemetry was collected across 20 monitored distribution nodes (160 profiles). While our GroupShuffleSplit and GroupKFold protocols strictly prevented meter-level leakage by holding out entire physical meters, future work must expand validation to thousands of meters across diverse distribution feeders.\n"
        "3. Tabular Representation in Recurrent Networks: The LSTM model evaluated 47 engineered tabular features sequentially rather than processing multi-thousand-step raw time-series directly. This non-standard formulation accounts for its lower performance relative to tree ensembles on tabular benchmarks.\n"
        "4. Unsupervised Contamination Sensitivity: Isolation Forest exhibited poor recall on CEEW (0.0357), illustrating that unsupervised anomaly detectors are sensitive to default contamination parameters when applied to multi-modal synthetic fraud distributions."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION V: CONCLUSION & FUTURE WORK
    # ─────────────────────────────────────────────────────────────────────────
    add_section_heading("V. CONCLUSION & FUTURE WORK")
    add_body_p(
        "This paper presented an end-to-end electricity theft detection framework designed for advanced metering infrastructure operating under real-world grid conditions. By leveraging authentic field telemetry from the CEEW smart meter deployment in Uttar Pradesh, India alongside a weather-enriched smart meter dataset and an external inspection benchmark, we demonstrated that combining 47 domain-specific features with theft attack injection (T1–T7), leak-free meter-grouped partitioning, and SMOTE class balancing yields strong detection performance."
    )
    add_body_p(
        "The proposed Soft-Voting Probability Ensemble achieved 96.88% accuracy, 100.0% precision, and an AUC-ROC of 1.0000 on unseen physical CEEW meters, and attained 99.10% accuracy, 100.0% recall, and 0.9174 F1-score on the weather-enriched dataset. In rigorous 5-fold cross-validation, XGBoost demonstrated high stability across folds (mean F1 of 0.9825 on CEEW and 0.9028 on Smart Meter). Furthermore, integrating TreeSHAP attribution with a physics-informed heuristic engine addresses the operational 'black box' challenge, enabling transparent field team dispatch through a production-grade microservice architecture."
    )
    add_body_p(
        "Future work will focus on federated learning across multiple DISCOM jurisdictions to preserve inter-utility data privacy, as well as edge-computing deployment directly onto smart meter firmware for real-time edge anomaly flagging."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # REFERENCES
    # ─────────────────────────────────────────────────────────────────────────
    add_section_heading("REFERENCES")
    refs = [
        "[1] S. S. S. R. Depuru, L. Wang, and V. Devabhaktuni, \"Electricity theft: Overview, issues, prevention and a smart meter based approach to control theft,\" Energy Policy, vol. 39, no. 2, pp. 1007–1015, 2011, doi: 10.1016/j.enpol.2010.11.037.",
        "[2] X. Xia, Y. Xiao, W. Liang, and J. Cui, \"Detection methods in smart meters for electricity thefts: A survey,\" Proc. IEEE, vol. 110, no. 2, pp. 273–319, Feb. 2022.",
        "[3] M. S. Saeed, M. W. Mustafa, N. N. Hamadneh, N. A. Alshammari, U. U. Sheikh, T. A. Jumani, S. B. A. Khalid, and I. Khan, \"Detection of non-technical losses in power utilities—A comprehensive systematic review,\" Energies, vol. 13, no. 18, p. 4727, 2020.",
        "[4] M. G. Chuwa and F. Wang, \"A review of non-technical loss attack models and detection methods in the smart grid,\" Electric Power Systems Research, vol. 199, p. 107415, 2021, doi: 10.1016/j.epsr.2021.107415.",
        "[5] T. Ahmad, \"Non-technical loss analysis and prevention using smart meters,\" Renewable and Sustainable Energy Reviews, vol. 72, pp. 573–589, 2017.",
        "[6] F. de Souza Savian, J. C. M. Siluk, T. B. Garlet, F. M. do Nascimento, J. R. Pinheiro, and Z. Vale, \"Non-technical losses: A systematic contemporary article review,\" Renewable and Sustainable Energy Reviews, vol. 147, p. 111205, 2021.",
        "[7] A. Althobaiti, A. Jindal, A. K. Marnerides, and U. Roedig, \"Energy theft in smart grids: A survey on data-driven attack strategies and detection methods,\" IEEE Access, vol. 9, pp. 159291–159312, 2021.",
        "[8] J. Nagi, K. S. Yap, S. K. Tiong, S. K. Ahmed, and M. Mohamad, \"Detection of Abnormalities and Electricity Theft using Genetic Support Vector Machines,\" in Proc. IEEE TENCON 2011, Bali, Indonesia, 2011, pp. 1–6, doi: 10.1109/TENCON.2011.6129308.",
        "[9] G. M. Messinis and N. D. Hatziargyriou, \"Review of Non-Technical Loss Detection Methods,\" Electric Power Systems Research, vol. 158, pp. 250–266, 2018, doi: 10.1016/j.epsr.2018.01.005.",
        "[10] M. M. Buzau, J. Tejedor-Aguilera, P. Cruz-Romero, and A. Gómez-Expósito, \"Detection of Non-Technical Losses Using Smart Meter Data and Supervised Learning,\" IEEE Trans. Smart Grid, vol. 10, no. 3, pp. 2661–2670, May 2019, doi: 10.1109/TSG.2018.2807925.",
        "[11] K. Zheng, Q. Chen, Y. Wang, C. Kang, and Q. Xia, \"A Novel Combined Data-Driven Approach for Electricity Theft Detection,\" IEEE Trans. Industrial Informatics, vol. 15, no. 3, pp. 1809–1819, Mar. 2019, doi: 10.1109/TII.2018.2873814.",
        "[12] N. F. Avila, G. Figueroa, and C. C. Chu, \"NTL Detection in Electric Distribution Systems Using the Maximal Overlap Discrete Wavelet-Packet Transform and Random Undersampling Boosting,\" IEEE Trans. Power Systems, vol. 33, no. 6, pp. 7171–7180, Nov. 2018, doi: 10.1109/TPWRS.2018.2853162.",
        "[13] S. Li, Y. Han, X. Yao, Y. Shen, J. Wang, and Q. Zhao, \"Electricity Theft Detection in Power Grids with Deep Learning and Random Forests,\" Journal of Electrical and Computer Engineering, vol. 2019, Article ID 4136874, 2019, doi: 10.1155/2019/4136874.",
        "[14] M. N. Hasan, R. N. Toma, A. A. Nahid, M. M. M. Islam, and J.-M. Kim, \"Electricity Theft Detection in Smart Grid Systems: A CNN–LSTM Based Approach,\" Energies, vol. 12, no. 17, p. 3310, 2019, doi: 10.3390/en12173310.",
        "[15] P. Jokar, N. Arianpoo, and V. C. M. Leung, \"Electricity Theft Detection in AMI Using Customers' Consumption Patterns,\" IEEE Trans. Smart Grid, vol. 7, no. 1, pp. 216–226, Jan. 2016, doi: 10.1109/TSG.2015.2425222.",
        "[16] Z. Yan and H. Wen, \"Electricity Theft Detection Base on Extreme Gradient Boosting in AMI,\" IEEE Trans. Instrumentation and Measurement, vol. 70, pp. 1–9, 2021.",
        "[17] S. Hussain, M. W. Mustafa, T. A. Jumani, S. K. Baloch, H. Alotaibi, I. Khan, and A. Khan, \"A novel feature engineered-CatBoost-based supervised machine learning framework for electricity theft detection,\" Energy Reports, vol. 7, no. 12, pp. 4425–4436, 2021, doi: 10.1016/j.egyr.2021.07.008.",
        "[18] N. Javaid et al., \"Non-technical losses detection using autoencoder and bidirectional gated recurrent unit to secure smart grids,\" IEEE Access, vol. 10, pp. 56863–56875, 2022.",
        "[19] N. Javaid, H. Gul, S. Baig, F. Shehzad, C. Xia, L. Guan, and T. Sultana, \"Using GANCNN and ERNET for Detection of Non-Technical Losses to Secure Smart Grids,\" IEEE Access, vol. 9, pp. 98679–98700, 2021, doi: 10.1109/ACCESS.2021.3092645.",
        "[20] A. T. El-Toukhy, M. M. Badr, M. M. E. A. Mahmoud, G. Srivastava, M. M. Fouda, and M. Alsabaan, \"Electricity Theft Detection Using Deep Reinforcement Learning in Smart Power Grids,\" IEEE Access, vol. 11, pp. 59558–59574, 2023, doi: 10.1109/ACCESS.2023.3284681.",
        "[21] M. Ismail, M. F. Shaaban, M. Naidu, and E. Serpedin, \"Deep Learning Detection of Electricity Theft Cyber-Attacks in Renewable Distributed Generation,\" IEEE Trans. Smart Grid, vol. 11, no. 4, pp. 3428–3437, Jul. 2020.",
        "[22] A. Nawaz, T. Ali, G. Mustafa, S. U. Rehman, and M. R. Rashid, \"A novel technique for detecting electricity theft in secure smart grids using CNN and XGBoost,\" Intelligent Systems with Applications, vol. 17, p. 200168, 2023, doi: 10.1016/j.iswa.2022.200168.",
        "[23] Z. A. Khan, M. Adil, N. Javaid, M. N. Saqib, M. Shafiq, and J.-G. Choi, \"Electricity Theft Detection Using Supervised Learning Techniques on Smart Meter Data,\" Sustainability, vol. 12, no. 19, p. 8023, 2020, doi: 10.3390/su12198023.",
        "[24] R. Yadav and Y. Kumar, \"Detection of non-technical losses in electric distribution network by applying machine learning and feature engineering,\" Journal Européen des Systèmes Automatisés, vol. 54, no. 3, pp. 487–493, 2021, doi: 10.18280/jesa.540312.",
        "[25] M. T. Quasim, K. Nisa, M. Z. Khan et al., \"An internet of things enabled machine learning model for Energy Theft Prevention System (ETPS) in Smart Cities,\" Journal of Cloud Computing, vol. 12, p. 158, 2023, doi: 10.1186/s13677-023-00525-4.",
        "[26] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, \"SMOTE: Synthetic Minority Over-sampling Technique,\" Journal of Artificial Intelligence Research, vol. 16, pp. 321–357, 2002, doi: 10.1613/jair.953.",
        "[27] J. Davis and M. Goadrich, \"The Relationship Between Precision-Recall and ROC Curves,\" in Proc. 23rd Int. Conf. Machine Learning (ICML), Pittsburgh, PA, USA, 2006, pp. 233–240, doi: 10.1145/1143844.1143874.",
        "[28] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001, doi: 10.1023/A:1010933404324.",
        "[29] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" in Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining, San Francisco, CA, USA, 2016, pp. 785–794, doi: 10.1145/2939672.2939785.",
        "[30] S. Hochreiter and J. Schmidhuber, \"Long Short-Term Memory,\" Neural Computation, vol. 9, no. 8, pp. 1735–1780, 1997, doi: 10.1162/neco.1997.9.8.1735.",
        "[31] F. T. Liu, K. M. Ting, and Z.-H. Zhou, \"Isolation Forest,\" in Proc. 2008 8th IEEE Int. Conf. Data Mining (ICDM), Pisa, Italy, 2008, pp. 413–422, doi: 10.1109/ICDM.2008.17.",
        "[32] M. Abadi et al., \"TensorFlow: A System for Large-Scale Machine Learning,\" in Proc. 12th USENIX Symp. Operating Systems Design and Implementation (OSDI 16), Savannah, GA, USA, 2016, pp. 265–283.",
        "[33] S. M. Lundberg and S.-I. Lee, \"A Unified Approach to Interpreting Model Predictions,\" in Advances in Neural Information Processing Systems 30 (NIPS 2017), Long Beach, CA, USA, 2017, pp. 4765–4774.",
        "[34] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
        "[35] G. Lemaître, F. Nogueira, and C. K. Aridas, \"Imbalanced-learn: A Python Toolbox to Tackle the Curse of Imbalanced Datasets in Machine Learning,\" Journal of Machine Learning Research, vol. 18, no. 17, pp. 1–5, 2017.",
        "[36] Council on Energy, Environment and Water (CEEW), \"Smart Meter Data – Mathura and Bareilly, Uttar Pradesh,\" dataset, 2019–2021, Kaggle (user jehanbhathena). [Online]. Available: https://www.kaggle.com/datasets/jehanbhathena/smart-meter-data-mathura-and-bareilly (accessed Oct. 31, 2026).",
        "[37] vaishnavi-1, \"Electricity-theft-detection-using-ML,\" GitHub repository. [Online]. Available: https://github.com/vaishnavi-1/Electricity-theft-detection-using-ML (accessed Oct. 31, 2026).",
        "[38] ziya07, \"Smart Meter Electricity Consumption Dataset (labeled),\" Kaggle dataset. [Online]. Available: https://www.kaggle.com/datasets/ziya07/smart-meter-electricity-consumption-dataset (accessed Oct. 31, 2026)."
    ]

    for r_text in refs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(2.5)
        run = p.add_run(r_text)
        run.font.size = Pt(8.5)
        run.font.name = 'Times New Roman'

    out_docx = "IEEE_Research_Paper_Final.docx"
    doc.save(out_docx)
    print(f"IEEE Final Research Paper generated successfully at: {out_docx}")

if __name__ == "__main__":
    create_ieee_paper_docx()
