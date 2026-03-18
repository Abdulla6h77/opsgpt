"""
anomaly_service.py
==================
Loads the trained Scikit-learn anomaly detection model and exposes a clean
`detect()` interface consumed by the FastAPI anomaly routes.

Model files expected at:
  ai/models/anomaly_model.pkl    — IsolationForest / LOF model
  ai/models/service_encoder.pkl  — LabelEncoder for the `service` column
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Any

import numpy as np

from ai.explain import explain_anomaly

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[3]
_MODEL_PATH = _REPO_ROOT / "ai" / "models" / "anomaly_model.pkl"
_ENCODER_PATH = _REPO_ROOT / "ai" / "models" / "service_encoder.pkl"

# ---------------------------------------------------------------------------
# Feature columns (must match training)
# ---------------------------------------------------------------------------
_NUMERIC_FEATURES = ["latency_ms", "status_code"]
_SERVICE_COL = "service"

# Severity thresholds based on anomaly score returned by the model.
# IsolationForest returns scores in roughly [-0.5, 0.5]; more negative = more anomalous.
_SEVERITY_THRESHOLDS = {
    "CRITICAL": -0.35,
    "HIGH": -0.20,
    "MEDIUM": -0.10,
}


def _load_pickle(path: Path, label: str) -> Any:
    if not path.exists():
        raise FileNotFoundError(
            f"{label} not found at {path}. "
            "Run ai/training/anomaly_training.ipynb to generate model files."
        )
    with open(path, "rb") as fh:
        obj = pickle.load(fh)  # noqa: S301 — internal trusted model file
    logger.info("Loaded %s from %s", label, path)
    return obj


# ---------------------------------------------------------------------------
# AnomalyService
# ---------------------------------------------------------------------------

class AnomalyService:
    """
    Wraps the trained Scikit-learn model and provides a `detect()` method
    that accepts a list of parsed log dicts and returns enriched anomaly dicts.

    Lazy-loads the model on first call so import time stays fast.
    """

    def __init__(self) -> None:
        self._model: Any | None = None
        self._encoder: Any | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._model is None:
            self._model = _load_pickle(_MODEL_PATH, "anomaly_model")
        if self._encoder is None:
            self._encoder = _load_pickle(_ENCODER_PATH, "service_encoder")

    def _encode_service(self, service: str) -> int:
        """Encode service name; unknown services get label -1."""
        try:
            return int(self._encoder.transform([service])[0])
        except Exception:
            return -1

    def _score_to_severity(self, score: float) -> str:
        if score <= _SEVERITY_THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        if score <= _SEVERITY_THRESHOLDS["HIGH"]:
            return "HIGH"
        if score <= _SEVERITY_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        return "LOW"

    def _build_feature_row(self, log: dict[str, Any]) -> list[float]:
        """Convert a single log dict into a feature vector."""
        latency = float(log.get("latency_ms") or 0.0)
        status = float(log.get("status_code") or 0.0)
        service_enc = float(self._encode_service(str(log.get(_SERVICE_COL, ""))))
        return [latency, status, service_enc]

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def detect(self, logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Run anomaly detection over a list of log dicts.

        Args:
            logs: List of parsed log dicts, each containing at minimum:
                  timestamp, service, status_code, latency_ms, message

        Returns:
            List of anomaly dicts (subset of input logs that are anomalous),
            each enriched with:
                is_anomaly    : True
                anomaly_score : float  (raw model score)
                severity      : str    (CRITICAL / HIGH / MEDIUM / LOW)
                reasons       : list[str]  (from explain_anomaly)
        """
        if not logs:
            return []

        try:
            self._ensure_loaded()
        except FileNotFoundError as exc:
            logger.error("Model files missing: %s. Returning empty anomaly list.", exc)
            return []

        # Build feature matrix
        feature_matrix = np.array([self._build_feature_row(log) for log in logs])

        # Predict: IsolationForest returns 1 (normal) or -1 (anomaly)
        try:
            predictions = self._model.predict(feature_matrix)
            scores = self._model.decision_function(feature_matrix)
        except Exception as exc:
            logger.exception("Model inference failed: %s", exc)
            return []

        anomalies: list[dict[str, Any]] = []
        for log, pred, score in zip(logs, predictions, scores):
            if pred != -1:
                continue  # normal — skip

            severity = self._score_to_severity(float(score))
            reasons = explain_anomaly(log)

            anomaly = {
                **log,
                "is_anomaly": True,
                "anomaly_score": round(float(score), 4),
                "severity": severity,
                "reasons": reasons,
            }
            anomalies.append(anomaly)

        logger.info(
            "Anomaly detection complete total=%d anomalies=%d",
            len(logs),
            len(anomalies),
        )
        return anomalies

    def detect_single(self, log: dict[str, Any]) -> dict[str, Any] | None:
        """
        Convenience wrapper for a single log entry.
        Returns the enriched anomaly dict or None if the log is normal.
        """
        results = self.detect([log])
        return results[0] if results else None


# ---------------------------------------------------------------------------
# Module-level singleton (import and reuse across requests)
# ---------------------------------------------------------------------------
anomaly_service = AnomalyService()