from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.log_parser import parse_logs

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/upload")
async def upload_logs(file: UploadFile = File(...)):
    if not file.filename.endswith(".log"):
        raise HTTPException(status_code=400, detail="Only .log files allowed")

    content = await file.read()
    logs = parse_logs(content.decode("utf-8"))

    return {
        "message": "Logs uploaded successfully",
        "total_logs": len(logs)
    }
