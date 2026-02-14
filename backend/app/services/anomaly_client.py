import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MODEL_PATH = os.path.join(REPO_ROOT, "ai", "models", "anomaly_model.pkl")
ENCODER_PATH = os.path.join(REPO_ROOT, "ai", "models", "service_encoder.pkl")

model = joblib.load(MODEL_PATH)
encoder: LabelEncoder = joblib.load(ENCODER_PATH)


def detect_anomalies(logs: list):
    df = pd.DataFrame(logs)

    df["is_error"] = (df["level"] == "ERROR").astype(int)
    df["is_server_error"] = (df["status_code"] >= 500).astype(int)
    df["service_encoded"] = encoder.transform(df["service"])

    features = df[
        ["latency_ms", "is_error", "is_server_error", "service_encoded"]
    ].fillna(0)

    df["anomaly"] = model.predict(features)
    df["anomaly"] = df["anomaly"].map({1: 0, -1: 1})

    return df[df["anomaly"] == 1].to_dict(orient="records")
