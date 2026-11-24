"""
TrafficIntel AI - Machine Learning Training Pipeline
Trains a Random Forest Classifier to forecast traffic congestion categories (Low, Moderate, High)
incorporating spatiotemporal features, diurnal cycles, and meteorological inputs.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "ml", "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "backend", "app", "ml", "artifacts")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "traffic_dataset.csv")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "rf_traffic_model.joblib")
METADATA_PATH = os.path.join(ARTIFACTS_DIR, "model_metadata.json")

def generate_synthetic_telemetry(num_records: int = 10000) -> pd.DataFrame:
    print(f"Generating {num_records} telemetry rows...", flush=True)
    np.random.seed(42)

    corridor_names = [
        "Central Arterial Corridor",
        "Outer Ring Expressway",
        "Transit Hub Junction",
        "Tech Park Boulevard",
        "Arterial Bypass Link"
    ]
    corridor_lats = [12.9716, 12.9352, 12.9772, 12.8452, 12.9112]
    corridor_lons = [77.5946, 77.6245, 77.5708, 77.6602, 77.6155]
    corridor_ff = [55, 70, 45, 60, 50]

    idx = np.random.randint(0, len(corridor_names), size=num_records)
    road_names = [corridor_names[i] for i in idx]
    lats = np.array([corridor_lats[i] for i in idx])
    lons = np.array([corridor_lons[i] for i in idx])
    ff_speeds = np.array([corridor_ff[i] for i in idx])

    hours = np.random.uniform(0.0, 24.0, size=num_records)
    days = np.random.randint(0, 7, size=num_records)
    is_weekend = (days >= 5).astype(int)

    rain_mask = np.random.rand(num_records) < 0.12
    precipitation = np.where(rain_mask, np.round(np.random.exponential(scale=3.0, size=num_records), 1), 0.0)
    temp = np.round(20.0 + 8.0 * np.sin(np.pi * (hours - 6) / 12) + np.random.normal(0, 1.0, size=num_records), 1)

    is_m_rush = ((hours >= 8.0) & (hours <= 10.5) & (is_weekend == 0))
    is_e_rush = ((hours >= 17.0) & (hours <= 20.0) & (is_weekend == 0))
    is_rush = is_m_rush | is_e_rush

    scores = (
        is_rush.astype(float) * 1.8 +
        (precipitation > 1.0).astype(float) * 0.9 +
        (days == 4).astype(float) * 0.4 -
        is_weekend.astype(float) * 0.6 +
        np.random.normal(0, 0.4, size=num_records)
    )

    q1 = np.percentile(scores, 35)
    q2 = np.percentile(scores, 72)

    congestion_level = np.zeros(num_records, dtype=int)
    congestion_level[scores > q1] = 1
    congestion_level[scores > q2] = 2

    speed_factor = np.where(congestion_level == 0, np.random.uniform(0.8, 1.0, size=num_records),
                    np.where(congestion_level == 1, np.random.uniform(0.45, 0.75, size=num_records),
                             np.random.uniform(0.18, 0.40, size=num_records)))
    observed_speeds = np.round(ff_speeds * speed_factor, 1)

    df = pd.DataFrame({
        "road_name": road_names,
        "latitude": lats,
        "longitude": lons,
        "hour": np.round(hours, 2),
        "day_of_week": days,
        "is_weekend": is_weekend,
        "temperature_c": temp,
        "precipitation_mm": precipitation,
        "free_flow_speed": ff_speeds,
        "observed_speed": observed_speeds,
        "congestion_level": congestion_level
    })

    df.to_csv(CSV_PATH, index=False)
    print(f"Generated {len(df)} records in {CSV_PATH}", flush=True)
    return df

def feature_engineering(df: pd.DataFrame):
    df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    df["is_rush_hour"] = df["hour"].apply(lambda h: 1 if (8.0 <= h <= 10.5) or (17.0 <= h <= 20.0) else 0)
    df["rain_intensity"] = df["precipitation_mm"].apply(lambda p: 2 if p > 3.0 else (1 if p > 0.2 else 0))

    feature_cols = [
        "sin_hour", "cos_hour", "day_of_week", "is_weekend",
        "is_rush_hour", "temperature_c", "precipitation_mm", "rain_intensity"
    ]
    return df[feature_cols], df["congestion_level"], feature_cols

def train_and_evaluate():
    print("--- Starting ML Pipeline Training ---", flush=True)
    df = generate_synthetic_telemetry(10000)

    X, y, feature_names = feature_engineering(df)

    split_idx = int(len(df) * 0.80)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples", flush=True)

    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)
    dummy_acc = accuracy_score(y_test, dummy.predict(X_test))
    print(f"Baseline (Most Frequent) Accuracy: {dummy_acc * 100:.2f}%", flush=True)

    rf = RandomForestClassifier(
        n_estimators=50,
        max_depth=10,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=1
    )
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    report = classification_report(y_test, y_pred, target_names=["Low", "Moderate", "High"], output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()

    print(f"Random Forest Accuracy: {acc * 100:.2f}%", flush=True)
    print(f"Macro F1-Score: {f1_macro:.4f}", flush=True)

    importances = rf.feature_importances_
    feat_importances = [
        {"name": name, "importance": round(float(imp), 4)}
        for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    ]

    joblib.dump(rf, MODEL_PATH)
    print(f"Saved model artifact: {MODEL_PATH}", flush=True)

    metadata = {
        "version": "1.2.0",
        "algorithm": "RandomForestClassifier",
        "trained_at": datetime.now().isoformat(),
        "total_samples": len(df),
        "test_samples": len(X_test),
        "baseline_accuracy": round(float(dummy_acc), 4),
        "accuracy": round(float(acc), 4),
        "f1_macro": round(float(f1_macro), 4),
        "f1_weighted": round(float(f1_weighted), 4),
        "confusion_matrix": conf_matrix,
        "classification_report": report,
        "feature_importances": feat_importances,
        "feature_names": feature_names
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata: {METADATA_PATH}", flush=True)
    print("--- ML Pipeline Complete ---", flush=True)

if __name__ == "__main__":
    train_and_evaluate()
