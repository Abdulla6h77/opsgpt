from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LogBatchBase(BaseModel):
    filename: str


class LogBatchCreate(LogBatchBase):
    pass


class LogBatchResponse(LogBatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    uploaded_at: datetime

