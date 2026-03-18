from fastapi import APIRouter, Depends, File, Request, UploadFile

from ..core.rate_limit import limiter
from ..core.security import verify_api_key
from ..schemas.logs import LogUploadResponse
from ..services.log_parser import parse_logs
from ..utils.helpers import validate_and_read_log_upload

router = APIRouter(prefix="/logs", tags=["Logs"], dependencies=[Depends(verify_api_key)])


@limiter.limit("100/minute")
@router.post(
    "/upload",
    response_model=LogUploadResponse,
    summary="Upload log file",
    description="Upload a .log/.txt file for parsing and preprocessing.",
    responses={
        200: {"description": "Log file parsed successfully."},
        400: {"description": "Invalid file format."},
    },
)
async def upload_logs(request: Request, file: UploadFile = File(...)):
    content = await validate_and_read_log_upload(file)
    logs = parse_logs(content.decode("utf-8"))

    return {
        "message": "Logs uploaded successfully",
        "total_logs": len(logs),
    }
