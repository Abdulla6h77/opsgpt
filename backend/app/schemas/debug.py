from pydantic import BaseModel


class DebugInsertResponse(BaseModel):
    message: str
    incident_id: str

