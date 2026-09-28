import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import shap
import matplotlib.pyplot as plt
import os

def main():
    print("Loading the Enriched Smart Meter Dataset...")
    file_path = os.path.join("data", "smart_meter_data.csv")
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return
        
    df = pd.read_csv(file_path)
    
    # Feature Engineering
    print("Preprocessing data...")
    # Convert Timestamp to datetime and extract useful features
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
    
    # Encode target variable
    le = LabelEncoder()
    df['Anomaly_Label_Encoded'] = le.fit_transform(df['Anomaly_Label'])
    
    # Define features and target
    features = ['Electricity_Consumed', 'Temperature', 'Humidity', 
                'Wind_Speed', 'Avg_Past_Consumption', 'Hour', 'DayOfWeek']
    X = df[features]
    y = df['Anomaly_Label_Encoded']
    
    print(f"Features used: {features}")
    print(f"Class distribution:\n{df['Anomaly_Label'].value_counts()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train XGBoost Model
    print("\nTraining XGBoost model...")
    model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("\n--- Model Evaluation ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("Classification Report:")
    target_names = [str(cls) for cls in le.classes_]
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    # SHAP evaluation
    print("\nGenerating SHAP Summary Plot...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # Ensure paper_graphs directory exists
    os.makedirs('paper_graphs', exist_ok=True)
    
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, show=False)
    shap_plot_path = os.path.join("paper_graphs", "shap_summary_xgboost.png")
    plt.savefig(shap_plot_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"SHAP summary plot saved to {shap_plot_path}")
    
if __name__ == "__main__":
    main()
