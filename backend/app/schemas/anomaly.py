from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnomalyBase(BaseModel):
    incident_id: UUID
    anomaly_score: float
    raw_log: str
    timestamp: datetime


class AnomalyCreate(AnomalyBase):
    pass


class AnomalyResponse(AnomalyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class AnomalyListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    limit: int
    offset: int
    items: list[AnomalyResponse]


class DetectAnomalyResponse(BaseModel):
    total_logs: int
    anomalies_detected: int
    incident_report: dict[str, Any]
    incident_summary: str
    anomalies: list[dict[str, Any]]

