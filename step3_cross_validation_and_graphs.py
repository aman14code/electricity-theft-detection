"""
=============================================================================
 Step 3: Cross-Validation, Real ROC Curves & Publication-Ready Graphs
=============================================================================
1. Loads the exact datasets and models trained in Step 2.
2. Performs 5-Fold Cross Validation on the best model per dataset to verify robustness.
3. Generates real ROC curves for all models across datasets.
4. Generates a styled, publication-ready Bar Chart of F1/Accuracy/AUC scores.
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import joblib
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import roc_curve, auc, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import load_model

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
sns.set_context("paper", font_scale=1.3)
plt.style.use('seaborn-v0_8-whitegrid')

def ensure_dirs():
    os.makedirs('paper_graphs', exist_ok=True)
    os.makedirs('model_results/reports', exist_ok=True)

# ─── 1. DATA LOADERS (Identical to Step 2) ───────────────────────────────

def load_dataset_a():
    path = os.path.join("processed_data", "ceew_features_smote_balanced.csv")
    if not os.path.exists(path): return None, None
    df = pd.read_csv(path)
    X = df.drop(columns=['label']).values
    y = df['label'].values
    return X, y

def load_dataset_b():
    path = os.path.join("data", "smart_meter_data.csv")
    if not os.path.exists(path): return None, None
    df = pd.read_csv(path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
    df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
    df['IsPeak'] = df['Hour'].between(8, 20).astype(int)
    df['Consumption_Deviation'] = df['Electricity_Consumed'] - df['Avg_Past_Consumption']
    df['Consumption_Ratio'] = df['Electricity_Consumed'] / (df['Avg_Past_Consumption'] + 1e-6)
    df['Temp_Consumption'] = df['Temperature'] * df['Electricity_Consumed']
    df['Humidity_Consumption'] = df['Humidity'] * df['Electricity_Consumed']
    
    df['label'] = LabelEncoder().fit_transform(df['Anomaly_Label'])
    feature_cols = ['Electricity_Consumed', 'Temperature', 'Humidity', 'Wind_Speed',
                    'Avg_Past_Consumption', 'Hour', 'DayOfWeek', 'IsWeekend', 'IsPeak',
                    'Consumption_Deviation', 'Consumption_Ratio', 'Temp_Consumption',
                    'Humidity_Consumption']
    X = df[feature_cols].values
    y = df['label'].values
    return X, y

def load_dataset_c():
    path = os.path.join("github_datasets", "fraud-detection-CNN",
                        "200Consumer_preprocessed_Data_with_Scaling.csv")
    if not os.path.exists(path): return None, None
    df = pd.read_csv(path)
    y = df['FLAG'].values
    X = df.drop(columns=['FLAG', 'CONS_NO']).values
    return X, y

# ─── 2. PUBLICATION GRAPHS ──────────────────────────────────────────────

def generate_bar_chart():
    print("\nGenerating Publication-Ready Bar Chart...")
    report_path = os.path.join("model_results", "reports", "model_comparison.csv")
    if not os.path.exists(report_path):
        print(f"File not found: {report_path}")
        return
        
    df = pd.read_csv(report_path)
    
    # We will plot the comparison for the SmartMeter dataset as the main graph
    df_sm = df[df['Dataset'] == 'SmartMeter'].copy()
    if df_sm.empty:
        print("No SmartMeter data in comparison.")
        return
        
    models = df_sm['Model'].tolist()
    models = [m.replace('Soft-Voting Ensemble', 'Soft Voting\nEnsemble') for m in models]
    
    accuracy = df_sm['accuracy'].values
    f1 = df_sm['f1'].values
    auc_score = df_sm['auc_roc'].values
    
    x = np.arange(len(models))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(14, 8))
    rects1 = ax.bar(x - width, accuracy, width, label='Accuracy', color='#4c72b0')
    rects2 = ax.bar(x, f1, width, label='F1-Score', color='#55a868')
    rects3 = ax.bar(x + width, auc_score, width, label='AUC-ROC', color='#c44e52')
    
    ax.set_ylabel('Score', fontweight='bold', fontsize=14)
    ax.set_title('Performance Comparison on Smart Meter Dataset (Weather Enriched)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=12)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=12)
    ax.set_ylim(0, 1.1)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, rotation=90)
    
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    
    plt.tight_layout()
    out_path = os.path.join('paper_graphs', 'publication_model_comparison.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Bar chart saved to {out_path}")

def plot_real_roc_curves():
    print("\nGenerating Real ROC Curves from Trained Models...")
    
    datasets = {
        'CEEW': load_dataset_a(),
        'SmartMeter': load_dataset_b(),
        'GitHub': load_dataset_c()
    }
    
    models_to_plot = ['Random_Forest', 'XGBoost', 'DNN']
    colors = ['#4c72b0', '#dd8452', '#55a868']
    
    for ds_name, (X, y) in datasets.items():
        if X is None: continue
        
        # Exact same split as training
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        scaler_path = os.path.join("model_results", "models", f"{ds_name}_scaler.pkl")
        if not os.path.exists(scaler_path): continue
        scaler = joblib.load(scaler_path)
        X_test_scaled = scaler.transform(X_test)
        
        plt.figure(figsize=(10, 8))
        
        for i, model_name in enumerate(models_to_plot):
            model_path_pkl = os.path.join("model_results", "models", f"{ds_name}_{model_name}.pkl")
            model_path_keras = os.path.join("model_results", "models", f"{ds_name}_{model_name}.keras")
            
            y_prob = None
            if os.path.exists(model_path_pkl):
                model = joblib.load(model_path_pkl)
                y_prob = model.predict_proba(X_test_scaled)[:, 1]
            elif os.path.exists(model_path_keras):
                model = load_model(model_path_keras)
                y_prob = model.predict(X_test_scaled, verbose=0).flatten()
            
            if y_prob is not None:
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, color=colors[i], lw=2, label=f'{model_name.replace("_", " ")} (AUC = {roc_auc:.3f})')
        
        plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontweight='bold')
        plt.ylabel('True Positive Rate', fontweight='bold')
        plt.title(f'ROC Curves — {ds_name} Dataset', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=12)
        plt.tight_layout()
        
        out_path = os.path.join('paper_graphs', f'real_roc_curve_{ds_name}.png')
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"ROC curve for {ds_name} saved to {out_path}")

# ─── 3. 5-FOLD CROSS VALIDATION ──────────────────────────────────────────

def perform_5_fold_cv():
    print("\nPerforming 5-Fold Cross Validation on Best Models...")
    
    # 1. CEEW Dataset -> Random Forest is Best
    X, y = load_dataset_a()
    if X is not None:
        model_path = os.path.join("model_results", "models", "CEEW_Random_Forest.pkl")
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1', n_jobs=-1)
            print(f"  CEEW (Random Forest) 5-Fold F1 Scores: {scores}")
            print(f"  CEEW Mean F1: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
            
    # 2. SmartMeter -> Random Forest is Best
    X, y = load_dataset_b()
    if X is not None:
        model_path = os.path.join("model_results", "models", "SmartMeter_Random_Forest.pkl")
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1', n_jobs=-1)
            print(f"  SmartMeter (Random Forest) 5-Fold F1 Scores: {scores}")
            print(f"  SmartMeter Mean F1: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
            
    # 3. GitHub -> XGBoost is Best
    X, y = load_dataset_c()
    if X is not None:
        model_path = os.path.join("model_results", "models", "GitHub_XGBoost.pkl")
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1', n_jobs=-1)
            print(f"  GitHub (XGBoost) 5-Fold F1 Scores: {scores}")
            print(f"  GitHub Mean F1: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")


if __name__ == "__main__":
    ensure_dirs()
    generate_bar_chart()
    plot_real_roc_curves()
    perform_5_fold_cv()
    print("\nStep 3 Complete! Check 'paper_graphs' folder.")
