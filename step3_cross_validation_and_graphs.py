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
import matplotlib
matplotlib.use('Agg')  # Must be before pyplot import — fixes tkinter thread crash on Windows
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GroupKFold, GroupShuffleSplit
from sklearn.metrics import roc_curve, auc, classification_report, f1_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from tensorflow.keras.models import load_model
import xgboost as xgb

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
sns.set_context("paper", font_scale=1.3)
plt.style.use('seaborn-v0_8-whitegrid')

def ensure_dirs():
    os.makedirs('paper_graphs', exist_ok=True)
    os.makedirs('paper_figures_final', exist_ok=True)
    os.makedirs('model_results/reports', exist_ok=True)

# ─── 1. DATA LOADERS (Identical to Step 2) ───────────────────────────────

def load_dataset_a():
    """
    Load CEEW pre-SMOTE dataset with base meter IDs.
    SMOTE is applied inside each CV fold's training split to prevent leakage.
    GroupKFold ensures physical meters are never split across train and test.
    """
    path = os.path.join("processed_data", "ceew_features_pre_smote.csv")
    if not os.path.exists(path): return None, None, None
    df = pd.read_csv(path)
    exclude = ['label', 'theft_type', 'meter']
    feature_cols = [c for c in df.columns if c not in exclude]
    X = df[feature_cols].values
    y = df['label'].values
    groups = df['meter'].apply(lambda x: str(x).split('_')[0]).values
    return X, y, groups

def load_dataset_b():
    path = os.path.join("data", "smart_meter_data.csv")
    if not os.path.exists(path): return None, None, None
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
    
    # Abnormal (Theft) = 1, Normal = 0 — explicit to avoid LabelEncoder alphabetical inversion
    df['label'] = (df['Anomaly_Label'] == 'Abnormal').astype(int)
    feature_cols = ['Electricity_Consumed', 'Temperature', 'Humidity', 'Wind_Speed',
                    'Avg_Past_Consumption', 'Hour', 'DayOfWeek', 'IsWeekend', 'IsPeak',
                    'Consumption_Deviation', 'Consumption_Ratio', 'Temp_Consumption',
                    'Humidity_Consumption']
    X = df[feature_cols].values
    y = df['label'].values
    return X, y, None

def load_dataset_c():
    path = os.path.join("github_datasets", "fraud-detection-CNN",
                        "200Consumer_preprocessed_Data_with_Scaling.csv")
    if not os.path.exists(path): return None, None, None
    df = pd.read_csv(path)
    y = df['FLAG'].values
    X = df.drop(columns=['FLAG', 'CONS_NO']).values
    return X, y, None

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
    plt.savefig(os.path.join('paper_figures_final', 'Fig10_Performance_Bar_SmartMeter.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Bar chart saved to {out_path}")

def plot_real_roc_curves():
    print("\nGenerating Real ROC Curves from Trained Models...")
    
    datasets = {
        'CEEW': load_dataset_a(),
        'SmartMeter': load_dataset_b(),
        'GitHub': load_dataset_c()
    }
    
    models_to_plot = ['Random_Forest', 'XGBoost', 'DNN', 'LSTM']
    colors = ['#4c72b0', '#dd8452', '#55a868', '#9467bd']
    
    for ds_name, (X, y, groups) in datasets.items():
        if X is None: continue
        
        # Exact same split as training in Step 2
        if ds_name == 'CEEW' and groups is not None:
            gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
            train_idx, test_idx = next(gss.split(X, y, groups=groups))
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        scaler_path = os.path.join("model_results", "models", f"{ds_name}_scaler.pkl")
        if not os.path.exists(scaler_path): continue
        scaler = joblib.load(scaler_path)
        X_test_scaled = scaler.transform(X_test)
        
        plt.figure(figsize=(10, 8))
        
        prob_dict = {}
        for i, model_name in enumerate(models_to_plot):
            model_path_pkl = os.path.join("model_results", "models", f"{ds_name}_{model_name}.pkl")
            model_path_keras = os.path.join("model_results", "models", f"{ds_name}_{model_name}.keras")
            
            y_prob = None
            if os.path.exists(model_path_pkl):
                model = joblib.load(model_path_pkl)
                y_prob = model.predict_proba(X_test_scaled)[:, 1]
            elif os.path.exists(model_path_keras):
                model = load_model(model_path_keras)
                if model_name == 'LSTM':
                    X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))
                    y_prob = model.predict(X_test_lstm, verbose=0).flatten()
                else:
                    y_prob = model.predict(X_test_scaled, verbose=0).flatten()
            
            if y_prob is not None:
                prob_dict[model_name] = y_prob
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, color=colors[i], lw=2, label=f'{model_name.replace("_", " ")} (AUC = {roc_auc:.3f})')
        
        # Add Soft-Voting Ensemble curve
        if len(prob_dict) >= 2:
            ens_prob = np.mean(list(prob_dict.values()), axis=0)
            fpr, tpr, _ = roc_curve(y_test, ens_prob)
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, color='#e74c3c', lw=3, linestyle='--', label=f'Soft-Voting Ensemble (AUC = {roc_auc:.3f})')
        
        plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle=':')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontweight='bold', fontsize=12)
        plt.ylabel('True Positive Rate', fontweight='bold', fontsize=12)
        plt.title(f'ROC Curves — {ds_name} Dataset', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=11)
        plt.tight_layout()
        
        out_path = os.path.join('paper_graphs', f'real_roc_curve_{ds_name}.png')
        plt.savefig(out_path, dpi=300)
        
        fig_map = {
            'CEEW': 'Fig03_ROC_Curve_CEEW_Dataset.png',
            'SmartMeter': 'Fig04_ROC_Curve_SmartMeter_Dataset.png',
            'GitHub': 'Fig05_ROC_Curve_GitHub_Dataset.png'
        }
        if ds_name in fig_map:
            fig_path = os.path.join('paper_figures_final', fig_map[ds_name])
            plt.savefig(fig_path, dpi=300)
        
        plt.close()
        print(f"ROC curve for {ds_name} saved to {out_path}")

# ─── 3. 5-FOLD CROSS VALIDATION ──────────────────────────────────────────

def perform_5_fold_cv():
    """
    5-Fold Cross-Validation.
    
    CEEW: GroupKFold by base meter ID (zero meter leakage, unseen physical meters per fold).
    SMOTE applied inside each fold on training split only.
    
    SmartMeter & GitHub: StratifiedKFold.
    Computes both sample SD (ddof=1) and population SD (ddof=0).
    """
    print("\n" + "=" * 60)
    print("  5-FOLD CROSS VALIDATION (Robustness & Leak-Free)")
    print("=" * 60)
    
    cv_summary = {}
    
    # 1. CEEW Dataset — GroupKFold
    X, y, groups = load_dataset_a()
    if X is not None:
        print("\n--- [Dataset A: CEEW] 5-Fold GroupKFold (grouped by base meter ID, SMOTE per fold) ---")
        gkf = GroupKFold(n_splits=5)
        
        for model_name, clf_fn in [
            ('Random Forest', lambda: RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)),
            ('XGBoost', lambda: xgb.XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.05, random_state=42, eval_metric='logloss'))
        ]:
            fold_f1_scores, fold_acc_scores = [], []
            for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups)):
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X[train_idx])
                X_val = scaler.transform(X[val_idx])
                y_train = y[train_idx]
                y_val = y[val_idx]
                
                # Apply SMOTE only on training fold
                n_minority = min(sum(y_train == 0), sum(y_train == 1))
                k = min(5, n_minority - 1) if n_minority > 1 else 1
                smote = SMOTE(random_state=42, k_neighbors=k)
                X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
                
                clf = clf_fn()
                clf.fit(X_train_sm, y_train_sm)
                y_pred_val = clf.predict(X_val)
                
                f1 = f1_score(y_val, y_pred_val, zero_division=0)
                acc = (y_val == y_pred_val).mean()
                fold_f1_scores.append(f1)
                fold_acc_scores.append(acc)
                print(f"  {model_name} Fold {fold_idx+1} (val meters: {sorted(list(set(groups[val_idx])))}): Acc={acc:.4f}, F1={f1:.4f}")
            
            f1s = np.array(fold_f1_scores)
            accs = np.array(fold_acc_scores)
            key = f"CEEW_{model_name.replace(' ', '_')}"
            cv_summary[key] = {
                'folds_f1': [round(x, 4) for x in f1s],
                'mean_f1': round(f1s.mean(), 4),
                'sample_sd_f1': round(f1s.std(ddof=1), 4),
                'pop_sd_f1': round(f1s.std(), 4),
                'mean_acc': round(accs.mean(), 4),
                'sample_sd_acc': round(accs.std(ddof=1), 4)
            }
            print(f"  --> {model_name} CEEW 5-Fold F1: Mean={f1s.mean():.4f} (Sample SD={f1s.std(ddof=1):.4f}, Pop SD={f1s.std():.4f})")
            print(f"  --> {model_name} CEEW 5-Fold Acc: Mean={accs.mean():.4f} (Sample SD={accs.std(ddof=1):.4f}, Pop SD={accs.std():.4f})")
    
    # 2. SmartMeter Dataset — StratifiedKFold
    X, y, _ = load_dataset_b()
    if X is not None:
        print("\n--- [Dataset B: SmartMeter] 5-Fold Stratified CV ---")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        for model_name, clf_fn in [
            ('Random Forest', lambda: RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)),
            ('XGBoost', lambda: xgb.XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.05, scale_pos_weight=4750/250, random_state=42, eval_metric='logloss'))
        ]:
            fold_f1_scores, fold_acc_scores = [], []
            for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X, y)):
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X[train_idx])
                X_val = scaler.transform(X[val_idx])
                y_train = y[train_idx]
                y_val = y[val_idx]
                
                clf = clf_fn()
                clf.fit(X_train, y_train)
                y_pred_val = clf.predict(X_val)
                fold_f1_scores.append(f1_score(y_val, y_pred_val, zero_division=0))
                fold_acc_scores.append((y_val == y_pred_val).mean())
            
            f1s = np.array(fold_f1_scores)
            accs = np.array(fold_acc_scores)
            key = f"SmartMeter_{model_name.replace(' ', '_')}"
            cv_summary[key] = {
                'folds_f1': [round(x, 4) for x in f1s],
                'mean_f1': round(f1s.mean(), 4),
                'sample_sd_f1': round(f1s.std(ddof=1), 4),
                'pop_sd_f1': round(f1s.std(), 4),
                'mean_acc': round(accs.mean(), 4),
                'sample_sd_acc': round(accs.std(ddof=1), 4)
            }
            print(f"  --> {model_name} SmartMeter 5-Fold F1 Scores: {[round(x, 4) for x in f1s]}")
            print(f"  --> {model_name} SmartMeter Mean F1: {f1s.mean():.4f} (Sample SD={f1s.std(ddof=1):.4f}, Pop SD={f1s.std():.4f})")
            print(f"  --> {model_name} SmartMeter Mean Acc: {accs.mean():.4f} (Sample SD={accs.std(ddof=1):.4f}, Pop SD={accs.std():.4f})")
    
    # 3. GitHub Dataset — StratifiedKFold
    X, y, _ = load_dataset_c()
    if X is not None:
        print("\n--- [Dataset C: GitHub] 5-Fold Stratified CV ---")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        neg = sum(y == 0); pos = sum(y == 1)
        for model_name, clf_fn in [
            ('XGBoost', lambda: xgb.XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.05, scale_pos_weight=neg/pos, random_state=42, eval_metric='logloss', subsample=0.8, colsample_bytree=0.8))
        ]:
            fold_f1_scores, fold_acc_scores = [], []
            for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X, y)):
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X[train_idx])
                X_val = scaler.transform(X[val_idx])
                y_train = y[train_idx]
                y_val = y[val_idx]
                
                clf = clf_fn()
                clf.fit(X_train, y_train)
                y_pred_val = clf.predict(X_val)
                fold_f1_scores.append(f1_score(y_val, y_pred_val, zero_division=0))
                fold_acc_scores.append((y_val == y_pred_val).mean())
            
            f1s = np.array(fold_f1_scores)
            accs = np.array(fold_acc_scores)
            key = f"GitHub_{model_name.replace(' ', '_')}"
            cv_summary[key] = {
                'folds_f1': [round(x, 4) for x in f1s],
                'mean_f1': round(f1s.mean(), 4),
                'sample_sd_f1': round(f1s.std(ddof=1), 4),
                'pop_sd_f1': round(f1s.std(), 4),
                'mean_acc': round(accs.mean(), 4),
                'sample_sd_acc': round(accs.std(ddof=1), 4)
            }
            print(f"  --> {model_name} GitHub 5-Fold F1 Scores: {[round(x, 4) for x in f1s]}")
            print(f"  --> {model_name} GitHub Mean F1: {f1s.mean():.4f} (Sample SD={f1s.std(ddof=1):.4f}, Pop SD={f1s.std():.4f})")
            print(f"  --> {model_name} GitHub Mean Acc: {accs.mean():.4f} (Sample SD={accs.std(ddof=1):.4f}, Pop SD={accs.std():.4f})")
    
    # Save CV summary JSON for paper citation
    import json
    cv_out_path = os.path.join("model_results", "reports", "cv_results.json")
    with open(cv_out_path, "w") as f:
        json.dump(cv_summary, f, indent=2)
    print(f"\nCV results saved to {cv_out_path}")


if __name__ == "__main__":
    ensure_dirs()
    generate_bar_chart()
    plot_real_roc_curves()
    perform_5_fold_cv()
    print("\nStep 3 Complete! Check 'paper_graphs' and 'paper_figures_final' folders.")
