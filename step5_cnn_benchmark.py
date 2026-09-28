"""
=============================================================================
 Step 5: CNN Benchmarking
=============================================================================
Trains a 1D Convolutional Neural Network (CNN) on the GitHub dataset
(Dataset C) to benchmark against our XGBoost and Soft-Voting Ensemble.
The architecture mirrors standard approaches for sequential NTL detection.
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import warnings
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve, auc
import joblib

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.random.set_seed(42)
np.random.seed(42)

def load_data():
    path = os.path.join("github_datasets", "fraud-detection-CNN", "200Consumer_preprocessed_Data_with_Scaling.csv")
    if not os.path.exists(path):
        print(f"Dataset not found at {path}")
        return None, None
        
    df = pd.read_csv(path)
    y = df['FLAG'].values
    X = df.drop(columns=['FLAG', 'CONS_NO']).values
    return X, y

def build_cnn(input_shape):
    model = Sequential([
        Conv1D(filters=64, kernel_size=7, activation='relu', input_shape=input_shape),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        Dropout(0.3),
        
        Conv1D(filters=128, kernel_size=5, activation='relu'),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        Dropout(0.3),
        
        Conv1D(filters=64, kernel_size=3, activation='relu'),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        Dropout(0.3),
        
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.4),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.0005),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model

def main():
    print("--- Starting 1D-CNN Benchmarking ---")
    X, y = load_data()
    if X is None: return
    
    print(f"Loaded GitHub dataset: {X.shape[0]} samples, {X.shape[1]} timesteps (days)")
    
    # Scale data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Reshape for CNN: (samples, timesteps, features) -> (samples, 1034, 1)
    X_cnn = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_cnn, y, test_size=0.2, random_state=42, stratify=y)
    
    # Class weights due to any minor imbalance
    neg = sum(y_train == 0)
    pos = sum(y_train == 1)
    class_weights = {0: 1.0, 1: neg / pos if pos > 0 else 1.0}
    
    model = build_cnn((X_train.shape[1], 1))
    es = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    
    print("\nTraining CNN...")
    history = model.fit(X_train, y_train, epochs=100, batch_size=16,
                        validation_split=0.2, callbacks=[es],
                        class_weight=class_weights, verbose=0)
    
    # Evaluate
    print("\nEvaluating CNN...")
    y_prob = model.predict(X_test, verbose=0).flatten()
    y_pred = (y_prob >= 0.5).astype(int)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    print("\n--- 1D CNN Results ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"AUC-ROC:   {roc_auc:.4f}")
    
    # Compare with our XGBoost model (load if available)
    xgb_path = os.path.join("model_results", "models", "GitHub_XGBoost.pkl")
    xgb_prob = None
    if os.path.exists(xgb_path):
        xgb_model = joblib.load(xgb_path)
        # XGBoost was trained on 2D data, not 3D
        X_test_2d = X_test.reshape((X_test.shape[0], X_test.shape[1]))
        xgb_prob = xgb_model.predict_proba(X_test_2d)[:, 1]
    
    # Plot ROC comparison
    plt.figure(figsize=(10, 8))
    plt.style.use('seaborn-v0_8-whitegrid')
    
    fpr_cnn, tpr_cnn, _ = roc_curve(y_test, y_prob)
    plt.plot(fpr_cnn, tpr_cnn, lw=2, color='#c44e52', label=f'1D-CNN (AUC = {roc_auc:.3f})')
    
    if xgb_prob is not None:
        fpr_xgb, tpr_xgb, _ = roc_curve(y_test, xgb_prob)
        xgb_auc = auc(fpr_xgb, tpr_xgb)
        plt.plot(fpr_xgb, tpr_xgb, lw=2, color='#4c72b0', label=f'XGBoost Our Pipeline (AUC = {xgb_auc:.3f})')
        
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontweight='bold', fontsize=12)
    plt.ylabel('True Positive Rate', fontweight='bold', fontsize=12)
    plt.title('ROC Curve Comparison: 1D-CNN vs Tree-Based Pipeline', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=12)
    
    os.makedirs('paper_graphs', exist_ok=True)
    out_path = os.path.join('paper_graphs', 'benchmark_cnn_vs_xgboost.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save the model
    os.makedirs('model_results/models_tuned', exist_ok=True)
    model.save('model_results/models_tuned/GitHub_1D_CNN.keras')
    
    print(f"\nROC comparison graph saved to {out_path}")
    print("Benchmarking Complete!")

if __name__ == "__main__":
    main()
