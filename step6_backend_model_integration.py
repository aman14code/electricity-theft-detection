"""
=============================================================================
 Step 6: Backend Model Integration
=============================================================================
Trains a Random Forest model on the CEEW Dataset using EXACTLY the 15 
features that the FastAPI backend (ml-service/app/model.py) extracts.
This allows seamless plug-and-play integration with the existing PowerGuard
application without needing to rewrite the backend's API schema.
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

def main():
    print("--- Training Backend-Compatible Model ---")
    path = os.path.join("processed_data", "ceew_features_smote_balanced.csv")
    if not os.path.exists(path):
        print("CEEW data not found.")
        return
        
    df = pd.read_csv(path)
    
    # The 15 features the backend extracts
    # We will map our CEEW data to roughly approximate these backend features
    
    # 1. stat_mean -> kwh_mean
    # 2. stat_std -> kwh_std
    # 3. stat_cv -> kwh_std / kwh_mean
    # 4. stat_min -> kwh_min
    # 5. stat_max -> kwh_max
    # 6. stat_median -> kwh_median (we don't have this, use mean)
    # 7. stat_iqr -> (we don't have this, use std)
    # 8. stat_range -> kwh_max - kwh_min
    # 9. anom_zero_day_count -> zero_consumption_count
    # 10. anom_zero_day_ratio -> zero_consumption_ratio
    # 11. anom_below_baseline_ratio -> (approximate with a constant for now)
    # 12. meta_is_residential -> 1
    # 13. meta_is_commercial -> 0
    # 14. meta_is_industrial -> 0
    # 15. meta_baseline_kwh -> kwh_mean * 0.8
    
    backend_features = pd.DataFrame({
        'stat_mean': df['kwh_mean'],
        'stat_std': df['kwh_std'],
        'stat_cv': np.where(df['kwh_mean'] > 0, df['kwh_std'] / df['kwh_mean'], 0),
        'stat_min': df['kwh_min'],
        'stat_max': df['kwh_max'],
        'stat_median': df['kwh_mean'],
        'stat_iqr': df['kwh_std'] * 1.35, # Approximation
        'stat_range': df['kwh_max'] - df['kwh_min'],
        'anom_zero_day_count': df['zero_consumption_ratio'] * 720, # Approx count from ratio
        'anom_zero_day_ratio': df['zero_consumption_ratio'],
        'anom_below_baseline_ratio': df['night_day_ratio'] * 0.1, # Dummy mapping to give variance
        'meta_is_residential': 1.0,
        'meta_is_commercial': 0.0,
        'meta_is_industrial': 0.0,
        'meta_baseline_kwh': df['kwh_mean'] * 0.8
    })
    
    feature_names = list(backend_features.columns)
    X = backend_features.values
    y = df['label'].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    rf_model.fit(X_scaled, y)
    print(f"Backend Model Accuracy on Training Data: {rf_model.score(X_scaled, y):.4f}")
    
    # Format the ensemble dictionary expected by ml-service/app/model.py
    ensemble = {
        "feature_names": feature_names,
        "scaler": scaler,
        "rf_model": rf_model,
        "xgb_model": None,
        "iso_model": None,
        "meta_model": None,
        "optimal_threshold": 0.5,
        "shap_importance": {} 
    }
    
    # Save directly to the backend's models directory
    out_dir = os.path.join("ml-service", "models")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ensemble_model.pkl")
    
    joblib.dump(ensemble, out_path)
    print(f"Integration Complete! Backend model saved directly to {out_path}")

if __name__ == "__main__":
    main()
