"""
=============================================================================
 Step 2: Multi-Model Training & Evaluation
=============================================================================
Trains and evaluates 5 models on the processed datasets:
  1. Random Forest
  2. XGBoost
  3. DNN (Deep Neural Network)
  4. LSTM (Long Short-Term Memory)
  5. Isolation Forest (unsupervised baseline)

Evaluates on:
  - Dataset A: CEEW (Mathura/Bareilly) — synthetic theft + SMOTE
  - Dataset B: Enriched Smart Meter — labeled anomalies + weather
  - Dataset C: GitHub Theft Detection — pre-labeled consumers

Outputs:
  - Model comparison tables (accuracy, precision, recall, F1, AUC)
  - Confusion matrices
  - SHAP explanations for tree-based models
  - Soft-voting ensemble results
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import warnings
import joblib
import json
from datetime import datetime

# Sklearn
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix, 
                             classification_report)
from sklearn.ensemble import RandomForestClassifier, IsolationForest, VotingClassifier
import xgboost as xgb

# Deep Learning
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, Reshape, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

# Visualization
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import shap

warnings.filterwarnings('ignore')
tf.get_logger().setLevel('ERROR')
np.random.seed(42)
tf.random.set_seed(42)


# ─── UTILITIES ──────────────────────────────────────────────────────────────

def create_output_dirs():
    dirs = ['model_results', 'model_results/plots', 'model_results/models', 
            'model_results/reports']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    return dirs[0]


def plot_confusion_matrix(y_true, y_pred, title, save_path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Theft'],
                yticklabels=['Normal', 'Theft'])
    plt.title(title, fontsize=13, fontweight='bold')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def evaluate_model(y_true, y_pred, y_prob=None):
    """Return a dict of evaluation metrics."""
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
    }
    if y_prob is not None:
        try:
            metrics['auc_roc'] = roc_auc_score(y_true, y_prob)
        except ValueError:
            metrics['auc_roc'] = 0.0
    return metrics


# ─── DATASET LOADERS ────────────────────────────────────────────────────────

def load_dataset_a():
    """Load CEEW SMOTE-balanced dataset."""
    path = os.path.join("processed_data", "ceew_features_smote_balanced.csv")
    if not os.path.exists(path):
        print(f"  [SKIP] Dataset A not found: {path}")
        print("  Run step1_ceew_theft_injection.py first.")
        return None, None, None
    
    df = pd.read_csv(path)
    feature_cols = [c for c in df.columns if c != 'label']
    X = df[feature_cols].values
    y = df['label'].values
    
    print(f"  Dataset A (CEEW+SMOTE): {X.shape[0]} samples, {X.shape[1]} features")
    print(f"  Class distribution: Normal={sum(y==0)}, Theft={sum(y==1)}")
    return X, y, feature_cols


def load_dataset_b():
    """Load enriched smart meter dataset with weather features."""
    path = os.path.join("data", "smart_meter_data.csv")
    if not os.path.exists(path):
        print(f"  [SKIP] Dataset B not found: {path}")
        return None, None, None
    
    df = pd.read_csv(path)
    
    # Feature engineering
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
    df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
    df['IsPeak'] = df['Hour'].between(8, 20).astype(int)
    
    # Consumption deviation from rolling average
    df['Consumption_Deviation'] = df['Electricity_Consumed'] - df['Avg_Past_Consumption']
    df['Consumption_Ratio'] = df['Electricity_Consumed'] / (df['Avg_Past_Consumption'] + 1e-6)
    
    # Weather interaction features
    df['Temp_Consumption'] = df['Temperature'] * df['Electricity_Consumed']
    df['Humidity_Consumption'] = df['Humidity'] * df['Electricity_Consumed']
    
    # Encode target
    le = LabelEncoder()
    df['label'] = le.fit_transform(df['Anomaly_Label'])
    
    feature_cols = ['Electricity_Consumed', 'Temperature', 'Humidity', 'Wind_Speed',
                    'Avg_Past_Consumption', 'Hour', 'DayOfWeek', 'IsWeekend', 'IsPeak',
                    'Consumption_Deviation', 'Consumption_Ratio', 'Temp_Consumption',
                    'Humidity_Consumption']
    
    X = df[feature_cols].values
    y = df['label'].values
    
    print(f"  Dataset B (Smart Meter+Weather): {X.shape[0]} samples, {X.shape[1]} features")
    print(f"  Class distribution: Normal={sum(y==0)}, Theft={sum(y==1)}")
    return X, y, feature_cols


def load_dataset_c():
    """Load GitHub pre-labeled theft dataset (CNN repo)."""
    path = os.path.join("github_datasets", "fraud-detection-CNN",
                        "200Consumer_preprocessed_Data_with_Scaling.csv")
    if not os.path.exists(path):
        print(f"  [SKIP] Dataset C not found: {path}")
        return None, None, None
    
    df = pd.read_csv(path)
    
    y = df['FLAG'].values
    X = df.drop(columns=['FLAG', 'CONS_NO']).values
    feature_cols = [c for c in df.columns if c not in ['FLAG', 'CONS_NO']]
    
    print(f"  Dataset C (GitHub Labeled): {X.shape[0]} samples, {X.shape[1]} features")
    print(f"  Class distribution: Normal={sum(y==0)}, Theft={sum(y==1)}")
    return X, y, feature_cols


# ─── MODEL TRAINERS ─────────────────────────────────────────────────────────

def train_random_forest(X_train, y_train, X_test, y_test):
    model = RandomForestClassifier(
        n_estimators=500, max_depth=25, min_samples_split=5,
        class_weight='balanced', random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = evaluate_model(y_test, y_pred, y_prob)
    return model, y_pred, y_prob, metrics


def train_xgboost(X_train, y_train, X_test, y_test):
    # Calculate scale_pos_weight for imbalance
    neg = sum(y_train == 0)
    pos = sum(y_train == 1)
    scale_weight = neg / pos if pos > 0 else 1
    
    model = xgb.XGBClassifier(
        n_estimators=300, max_depth=8, learning_rate=0.05,
        scale_pos_weight=scale_weight, random_state=42,
        use_label_encoder=False, eval_metric='logloss',
        subsample=0.8, colsample_bytree=0.8
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = evaluate_model(y_test, y_pred, y_prob)
    return model, y_pred, y_prob, metrics


def train_dnn(X_train, y_train, X_test, y_test):
    n_features = X_train.shape[1]
    
    model = Sequential([
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
    
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='binary_crossentropy', metrics=['accuracy'])
    
    es = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # Handle class imbalance with class weights
    neg = sum(y_train == 0)
    pos = sum(y_train == 1)
    class_weights = {0: 1.0, 1: neg / pos if pos > 0 else 1.0}
    
    model.fit(X_train, y_train, epochs=100, batch_size=32,
              validation_split=0.15, callbacks=[es],
              class_weight=class_weights, verbose=0)
    
    y_prob = model.predict(X_test, verbose=0).flatten()
    y_pred = (y_prob >= 0.5).astype(int)
    metrics = evaluate_model(y_test, y_pred, y_prob)
    return model, y_pred, y_prob, metrics


def train_lstm(X_train, y_train, X_test, y_test):
    n_features = X_train.shape[1]
    
    # Reshape for LSTM: (samples, timesteps, features)
    # We treat each feature as a timestep for tabular data
    X_train_lstm = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(n_features, 1)),
        Dropout(0.3),
        LSTM(64, return_sequences=False),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='binary_crossentropy', metrics=['accuracy'])
    
    es = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    neg = sum(y_train == 0)
    pos = sum(y_train == 1)
    class_weights = {0: 1.0, 1: neg / pos if pos > 0 else 1.0}
    
    model.fit(X_train_lstm, y_train, epochs=50, batch_size=32,
              validation_split=0.15, callbacks=[es],
              class_weight=class_weights, verbose=0)
    
    y_prob = model.predict(X_test_lstm, verbose=0).flatten()
    y_pred = (y_prob >= 0.5).astype(int)
    metrics = evaluate_model(y_test, y_pred, y_prob)
    return model, y_pred, y_prob, metrics


def train_isolation_forest(X_train, y_train, X_test, y_test):
    model = IsolationForest(
        n_estimators=300, contamination=0.1,
        random_state=42, n_jobs=-1
    )
    model.fit(X_train)
    
    raw_pred = model.predict(X_test)
    # IsolationForest: -1 = anomaly, 1 = normal → convert to 0/1
    y_pred = (raw_pred == -1).astype(int)
    
    # Use decision function as probability proxy
    scores = -model.decision_function(X_test)  # Higher = more anomalous
    # Normalize to 0-1 range
    y_prob = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
    
    metrics = evaluate_model(y_test, y_pred, y_prob)
    return model, y_pred, y_prob, metrics


# ─── SOFT-VOTING ENSEMBLE ───────────────────────────────────────────────────

def soft_voting_ensemble(probabilities, weights=None):
    """Combine probabilities from multiple models using soft voting."""
    if weights is None:
        weights = [1.0] * len(probabilities)
    
    weighted_sum = np.zeros_like(probabilities[0], dtype=float)
    for prob, w in zip(probabilities, weights):
        weighted_sum += prob * w
    
    avg_prob = weighted_sum / sum(weights)
    return avg_prob, (avg_prob >= 0.5).astype(int)


# ─── MAIN PIPELINE ──────────────────────────────────────────────────────────

def run_pipeline_for_dataset(dataset_name, X, y, feature_cols, output_dir):
    """Run all 5 models + ensemble on a single dataset."""
    
    print(f"\n{'='*60}")
    print(f"  TRAINING PIPELINE: {dataset_name}")
    print(f"{'='*60}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Train models
    results = {}
    all_probs = {}
    
    model_trainers = {
        'Random Forest': train_random_forest,
        'XGBoost': train_xgboost,
        'DNN': train_dnn,
        'LSTM': train_lstm,
        'Isolation Forest': train_isolation_forest,
    }
    
    for model_name, trainer in model_trainers.items():
        print(f"\n--- Training {model_name} ---")
        try:
            model, y_pred, y_prob, metrics = trainer(X_train, y_train, X_test, y_test)
            results[model_name] = metrics
            all_probs[model_name] = y_prob
            
            print(f"  Accuracy:  {metrics['accuracy']:.4f}")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1:        {metrics['f1']:.4f}")
            if 'auc_roc' in metrics:
                print(f"  AUC-ROC:   {metrics['auc_roc']:.4f}")
            
            # Confusion matrix plot
            cm_path = os.path.join(output_dir, "plots",
                                   f"cm_{dataset_name}_{model_name.replace(' ', '_')}.png")
            plot_confusion_matrix(y_test, y_pred,
                                 f"{model_name} — {dataset_name}", cm_path)
            
            # SHAP for tree-based models
            if model_name in ['Random Forest', 'XGBoost'] and feature_cols is not None:
                try:
                    print(f"  Generating SHAP plot...")
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(X_test[:200])  # Sample for speed
                    
                    plt.figure(figsize=(10, 8))
                    if isinstance(shap_values, list):
                        shap.summary_plot(shap_values[1], X_test[:200],
                                          feature_names=feature_cols, show=False)
                    else:
                        shap.summary_plot(shap_values, X_test[:200],
                                          feature_names=feature_cols, show=False)
                    
                    shap_path = os.path.join(output_dir, "plots",
                                             f"shap_{dataset_name}_{model_name.replace(' ', '_')}.png")
                    plt.savefig(shap_path, bbox_inches='tight', dpi=200)
                    plt.close()
                    print(f"  SHAP plot saved: {shap_path}")
                except Exception as e:
                    print(f"  SHAP failed: {e}")
            
            # Save model
            model_path = os.path.join(output_dir, "models",
                                      f"{dataset_name}_{model_name.replace(' ', '_')}")
            if model_name in ['DNN', 'LSTM']:
                model.save(model_path + ".keras")
            else:
                joblib.dump(model, model_path + ".pkl")
                
        except Exception as e:
            print(f"  ERROR: {e}")
            results[model_name] = {'accuracy': 0, 'precision': 0, 'recall': 0, 'f1': 0, 'auc_roc': 0}
    
    # Soft-Voting Ensemble
    supervised_probs = {k: v for k, v in all_probs.items() if k != 'Isolation Forest'}
    if len(supervised_probs) >= 2:
        print(f"\n--- Soft-Voting Ensemble (RF + XGB + DNN + LSTM) ---")
        prob_list = list(supervised_probs.values())
        # Weight by individual F1 scores
        weights = [results[k].get('f1', 0.5) for k in supervised_probs.keys()]
        
        ensemble_prob, ensemble_pred = soft_voting_ensemble(prob_list, weights)
        ensemble_metrics = evaluate_model(y_test, ensemble_pred, ensemble_prob)
        results['Soft-Voting Ensemble'] = ensemble_metrics
        
        print(f"  Accuracy:  {ensemble_metrics['accuracy']:.4f}")
        print(f"  Precision: {ensemble_metrics['precision']:.4f}")
        print(f"  Recall:    {ensemble_metrics['recall']:.4f}")
        print(f"  F1:        {ensemble_metrics['f1']:.4f}")
        if 'auc_roc' in ensemble_metrics:
            print(f"  AUC-ROC:   {ensemble_metrics['auc_roc']:.4f}")
        
        cm_path = os.path.join(output_dir, "plots",
                               f"cm_{dataset_name}_Soft_Voting_Ensemble.png")
        plot_confusion_matrix(y_test, ensemble_pred,
                              f"Soft-Voting Ensemble — {dataset_name}", cm_path)
    
    # Save scaler
    joblib.dump(scaler, os.path.join(output_dir, "models", f"{dataset_name}_scaler.pkl"))
    
    return results


def main():
    output_dir = create_output_dirs()
    
    all_results = {}
    
    # Load all datasets
    print("\n" + "=" * 60)
    print("  LOADING DATASETS")
    print("=" * 60)
    
    datasets = {}
    
    print("\n[Dataset A] CEEW (Mathura/Bareilly + Synthetic Theft + SMOTE)")
    X_a, y_a, cols_a = load_dataset_a()
    if X_a is not None:
        datasets['CEEW'] = (X_a, y_a, cols_a)
    
    print("\n[Dataset B] Enriched Smart Meter (Weather + Anomaly Labels)")
    X_b, y_b, cols_b = load_dataset_b()
    if X_b is not None:
        datasets['SmartMeter'] = (X_b, y_b, cols_b)
    
    print("\n[Dataset C] GitHub Labeled Theft Detection")
    X_c, y_c, cols_c = load_dataset_c()
    if X_c is not None:
        datasets['GitHub'] = (X_c, y_c, cols_c)
    
    if not datasets:
        print("\nNo datasets available! Ensure data files exist.")
        return
    
    # Run pipeline for each dataset
    for ds_name, (X, y, cols) in datasets.items():
        results = run_pipeline_for_dataset(ds_name, X, y, cols, output_dir)
        all_results[ds_name] = results
    
    # ─── COMPREHENSIVE COMPARISON TABLE ─────────────────────────────────
    
    print("\n\n" + "=" * 80)
    print("  COMPREHENSIVE MODEL COMPARISON")
    print("=" * 80)
    
    comparison_rows = []
    for ds_name, results in all_results.items():
        for model_name, metrics in results.items():
            row = {'Dataset': ds_name, 'Model': model_name}
            row.update(metrics)
            comparison_rows.append(row)
    
    comparison_df = pd.DataFrame(comparison_rows)
    comparison_df = comparison_df.round(4)
    
    print("\n" + comparison_df.to_string(index=False))
    
    # Save comparison table
    report_path = os.path.join(output_dir, "reports", "model_comparison.csv")
    comparison_df.to_csv(report_path, index=False)
    print(f"\nComparison table saved to {report_path}")
    
    # Find best model per dataset
    print("\n--- Best Model Per Dataset ---")
    for ds_name in all_results:
        ds_df = comparison_df[comparison_df['Dataset'] == ds_name]
        best = ds_df.loc[ds_df['f1'].idxmax()]
        print(f"  {ds_name}: {best['Model']} (F1={best['f1']:.4f}, Acc={best['accuracy']:.4f})")
    
    # Generate summary plot
    fig, axes = plt.subplots(1, len(all_results), figsize=(7 * len(all_results), 6))
    if len(all_results) == 1:
        axes = [axes]
    
    for idx, (ds_name, results) in enumerate(all_results.items()):
        models = list(results.keys())
        f1_scores = [results[m]['f1'] for m in models]
        
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
        bars = axes[idx].barh(models, f1_scores, color=colors[:len(models)])
        axes[idx].set_xlabel('F1 Score', fontsize=11)
        axes[idx].set_title(f'{ds_name} Dataset', fontsize=13, fontweight='bold')
        axes[idx].set_xlim(0, 1.05)
        
        for bar, score in zip(bars, f1_scores):
            axes[idx].text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                           f'{score:.3f}', va='center', fontsize=10)
    
    plt.suptitle('Model Comparison — F1 Scores Across Datasets',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    summary_path = os.path.join(output_dir, "plots", "model_comparison_summary.png")
    plt.savefig(summary_path, bbox_inches='tight', dpi=200)
    plt.close()
    print(f"\nSummary plot saved to {summary_path}")
    
    print("\n" + "=" * 60)
    print("  ALL TRAINING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
