from PIL import Image, ImageDraw, ImageFont
import os

prompt_text = """Please rewrite my draft research paper into a final, highly technical IEEE-format publication. Use the 
attached sample paper (Kawoosa et al.) as a structural guide, but strictly use MY project data, methodology, 
and results provided below.

CRITICAL FORMATTING INSTRUCTIONS:
1. IEEE Format: Use strict IEEE structure (two-column layout assumption, Roman numerals for main headings: 
   I. INTRODUCTION, II. LITERATURE REVIEW, III. METHODOLOGY, IV. RESULTS, V. CONCLUSION).
2. Formulas: You MUST include LaTeX mathematical derivations for SMOTE, Soft Voting Ensemble, Accuracy, 
   Precision, Recall, F1-Score, and AUC-ROC in their respective sections.
3. Figure Placeholders: Throughout the text, you MUST insert explicit placeholders (e.g., [INSERT FIG 1: 
   CLASS IMBALANCE PIE CHART HERE]) exactly where the 10 images should go, accompanied by a formal 
   IEEE-style figure caption.

### MY PROJECT FACT SHEET & FIGURE MAPPING

I. INTRODUCTION & II. LITERATURE REVIEW
* Context: SGCC dataset, severe NTL losses.
* Contribution: A 5-model Soft Voting Ensemble paired with a deployable Microservice architecture (React, 
  Node.js, FastAPI) and a custom 8-measure heuristic explainability engine.

III. METHODOLOGY
* A. Dataset: 42,372 consumers, 1,034 days, 8.53% theft rate. -> [INSERT FIG 1 HERE]
* B. Data Pre-processing & Imbalance: Add mathematical derivation for SMOTE oversampling here. Mention 
  Cost-Sensitive learning and PR-curve threshold optimization. We did NOT use artificial attacks. -> [INSERT FIG 2 HERE]
* C. Feature Engineering: 47 features (Statistical, Temporal, Anomaly, Comparative). -> [INSERT FIG 3 HERE]
* D. Model Paradigms: Briefly define RF, XGBoost, DNN, Isolation Forest, and LSTM mathematically.
* E. Ensemble Strategy (Core Contribution): Add the mathematical derivation for Soft Voting here.
* F. Explainability: Mention SHAP and the custom 8-measure heuristic engine. -> [INSERT FIG 4 HERE]

IV. RESULTS AND DISCUSSION
* Provide the LaTeX formulas for Precision, Recall, F1, and AUC.
* A. Model Performance: Present the exact results table: Random Forest (AUC 0.793), XGBoost (AUC 0.785), 
  DNN (AUC 0.786), IsoForest (AUC 0.587), LSTM (AUC 0.746). 
* The Winner: Soft Voting Ensemble achieved 89.88% Accuracy, 0.411 Precision, 0.435 Recall, 0.423 F1-Score, 
  and 0.809 AUC-ROC. -> [INSERT FIG 6 HERE] & [INSERT FIG 7 HERE]
* B. Cross-Validation Stability: 5-Fold Stratified. RF Mean Acc: 89.13% (+/-1.3%). XGBoost Mean Acc: 
  88.95% (+/-0.78%). -> [INSERT FIG 5 HERE]
* C. ROC and PR Curves: Discuss why PR is critical for imbalanced data. -> [INSERT FIG 8] & [INSERT FIG 9]
* D. Confusion Matrix Analysis: For the Ensemble: 7,302 TN, 450 FP, 408 FN, 315 TP. Discuss the trade-off of 
  false positives vs field inspection costs. -> [INSERT FIG 10 HERE]

V. CONCLUSION
* Write in the past tense. Summarize the success of the 0.809 AUC-ROC ensemble and the successful 
  deployment of the microservice dashboard architecture.
"""

# Create a blank white image for the text
img_text = Image.new('RGB', (900, 1100), color=(255, 255, 255))
d = ImageDraw.Draw(img_text)
# We use default font since we don't know what TTF files are installed, 
# but we will scale it up manually or just use default.
d.text((20, 20), prompt_text, fill=(0, 0, 0))

images_list = []
graph_dir = "paper_graphs"
order = [
    'fig1_class_imbalance.png',
    'fig2_smote_impact.png',
    'fig3_consumption_profiles.png',
    'fig4_feature_importance.png',
    'fig5_cross_validation.png',
    'model_comparison_bar.png',
    'fig7_radar_chart.png',
    'roc_curves.png',
    'fig6_pr_curves.png',
    'confusion_matrix.png'
]

for img_name in order:
    img_path = os.path.join(graph_dir, img_name)
    if os.path.exists(img_path):
        img = Image.open(img_path).convert('RGB')
        images_list.append(img)

img_text.save("Claude_Master_Prompt_With_Images.pdf", save_all=True, append_images=images_list)
print("PDF created successfully!")
