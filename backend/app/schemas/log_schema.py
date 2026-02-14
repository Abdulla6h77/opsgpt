from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LogEntry(BaseModel):
    timestamp: datetime
    level: str                 # INFO, WARN, ERROR
    service: str               # auth-service, api-gateway, db
    message: str
    latency_ms: Optional[int] = None
    status_code: Optional[int] = None