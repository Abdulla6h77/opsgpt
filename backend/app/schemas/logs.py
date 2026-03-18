from pydantic import BaseModel


class LogUploadResponse(BaseModel):
    message: str
    total_logs: int

