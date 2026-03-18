"""
anomaly_client.py
=================
Thin delegation shim -- all detection logic lives in AnomalyService.
Models are lazy-loaded on the first call, so import is always safe.
"""
from ai.inference.anomaly_service import anomaly_service


def detect_anomalies(logs: list) -> list:
    """Run anomaly detection via the shared AnomalyService singleton."""
    return anomaly_service.detect(logs)
