from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IncidentBase(BaseModel):
    service_name: str
    severity: str
    status: str = "OPEN"
    summary: str
    root_cause: str
    remediation: str


class IncidentCreate(IncidentBase):
    pass


class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class IncidentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    limit: int
    offset: int
    items: list[IncidentResponse]

