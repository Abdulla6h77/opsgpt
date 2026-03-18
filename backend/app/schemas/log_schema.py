from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class LogEntry(BaseModel):
    timestamp: datetime
    level: LogLevel
    service: str
    message: str
    latency_ms: Optional[int] = Field(default=None, ge=0)
    status_code: Optional[int] = None
    severity: Optional[Severity] = None
