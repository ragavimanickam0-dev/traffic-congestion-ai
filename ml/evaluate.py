"""
TrafficIntel AI - Model Evaluation & Benchmarking Script
Loads the trained Random Forest model and compares test performance against baselines.
"""

import os
import sys
import json
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from ml.train import feature_engineering, CSV_PATH, MODEL_PATH, METADATA_PATH

def evaluate_model():
    print("=================================================================", flush=True)
    print(" TrafficIntel AI - Machine Learning Model Evaluation Report", flush=True)
    print("=================================================================\n", flush=True)

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model artifact not found at {MODEL_PATH}. Run 'python ml/train.py' first.", flush=True)
        return

    if not os.path.exists(CSV_PATH):
        print(f"Error: Dataset not found at {CSV_PATH}.", flush=True)
        return

    df = pd.read_csv(CSV_PATH)
    model = joblib.load(MODEL_PATH)
    
    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)

    X, y, feature_names = feature_engineering(df)

    split_idx = int(len(df) * 0.80)
    X_test = X.iloc[split_idx:]
    y_test = y.iloc[split_idx:]

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_m = f1_score(y_test, y_pred, average="macro")
    f1_w = f1_score(y_test, y_pred, average="weighted")
    cm = confusion_matrix(y_test, y_pred)

    print(f"Model Algorithm      : {metadata.get('algorithm', 'RandomForestClassifier')}", flush=True)
    print(f"Model Version        : {metadata.get('version', '1.2.0')}", flush=True)
    print(f"Evaluation Test Set  : {len(X_test)} samples (Chronological Split)", flush=True)
    print(f"Baseline Accuracy    : {metadata.get('baseline_accuracy', 0.36) * 100:.2f}%", flush=True)
    print(f"Trained Accuracy     : {acc * 100:.2f}%", flush=True)
    print(f"Macro F1-Score       : {f1_m:.4f}", flush=True)
    print(f"Weighted F1-Score    : {f1_w:.4f}\n", flush=True)

    print("Classification Report by Category:", flush=True)
    print("-----------------------------------------------------------------", flush=True)
    print(classification_report(y_test, y_pred, target_names=["Low", "Moderate", "High"]), flush=True)

    print("Confusion Matrix:", flush=True)
    print("-----------------------------------------------------------------", flush=True)
    print(f"                 Predicted Low  Predicted Mod  Predicted High", flush=True)
    print(f"Actual Low       {cm[0][0]:13d}  {cm[0][1]:13d}  {cm[0][2]:14d}", flush=True)
    print(f"Actual Moderate  {cm[1][0]:13d}  {cm[1][1]:13d}  {cm[1][2]:14d}", flush=True)
    print(f"Actual High      {cm[2][0]:13d}  {cm[2][1]:13d}  {cm[2][2]:14d}\n", flush=True)

    print("Top Feature Importances:", flush=True)
    print("-----------------------------------------------------------------", flush=True)
    for feat in metadata.get("feature_importances", []):
        bar = "=" * int(feat["importance"] * 30)
        print(f"{feat['name']:25s} | {feat['importance']:.4f} | {bar}", flush=True)

    print("\n=================================================================", flush=True)
    print(" Evaluation Completed Successfully", flush=True)
    print("=================================================================", flush=True)

if __name__ == "__main__":
    evaluate_model()
