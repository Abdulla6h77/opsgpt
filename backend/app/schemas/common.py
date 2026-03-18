from typing import Any

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error: str
    details: str | list[dict[str, Any]] | None = None

