"""
=============================================================================
 Step 4: Hyperparameter Tuning (Optuna / RandomizedSearchCV)
=============================================================================
Tunes the Random Forest and XGBoost models on the CEEW Dataset to 
maximize F1 score and find the absolute optimal parameters.
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import joblib
import warnings
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

def load_data():
    path = os.path.join("processed_data", "ceew_features_smote_balanced.csv")
    if not os.path.exists(path): 
        print("Data not found.")
        return None, None
    df = pd.read_csv(path)
    X = df.drop(columns=['label']).values
    y = df['label'].values
    return X, y

def tune_random_forest(X, y):
    print("\n--- Tuning Random Forest ---")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    rf = RandomForestClassifier(class_weight='balanced', random_state=42)
    
    param_dist = {
        'n_estimators': [100, 300, 500, 800],
        'max_depth': [10, 20, 30, 40, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2', None]
    }
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    random_search = RandomizedSearchCV(
        estimator=rf, param_distributions=param_dist, 
        n_iter=20, cv=cv, scoring='f1', n_jobs=-1, random_state=42, verbose=1
    )
    
    random_search.fit(X_scaled, y)
    print(f"Best RF F1 Score: {random_search.best_score_:.4f}")
    print(f"Best RF Params: {random_search.best_params_}")
    
    # Save the tuned model
    os.makedirs('model_results/models_tuned', exist_ok=True)
    joblib.dump(random_search.best_estimator_, 'model_results/models_tuned/CEEW_Random_Forest_Tuned.pkl')
    return random_search.best_estimator_

def tune_xgboost(X, y):
    print("\n--- Tuning XGBoost ---")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    neg = sum(y == 0)
    pos = sum(y == 1)
    scale_weight = neg / pos if pos > 0 else 1
    
    xgb_model = xgb.XGBClassifier(
        scale_pos_weight=scale_weight, random_state=42,
        use_label_encoder=False, eval_metric='logloss'
    )
    
    param_dist = {
        'n_estimators': [100, 300, 500],
        'max_depth': [3, 5, 7, 9],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0]
    }
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    random_search = RandomizedSearchCV(
        estimator=xgb_model, param_distributions=param_dist, 
        n_iter=20, cv=cv, scoring='f1', n_jobs=-1, random_state=42, verbose=1
    )
    
    random_search.fit(X_scaled, y)
    print(f"Best XGB F1 Score: {random_search.best_score_:.4f}")
    print(f"Best XGB Params: {random_search.best_params_}")
    
    joblib.dump(random_search.best_estimator_, 'model_results/models_tuned/CEEW_XGBoost_Tuned.pkl')
    return random_search.best_estimator_

if __name__ == "__main__":
    X, y = load_data()
    if X is not None:
        tune_random_forest(X, y)
        tune_xgboost(X, y)
        print("\nTuning Complete! Tuned models saved in 'model_results/models_tuned/'.")
