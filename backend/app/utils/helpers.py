from pathlib import PurePath

from fastapi import HTTPException, UploadFile

ALLOWED_UPLOAD_EXTENSIONS = {".log", ".txt"}
ALLOWED_UPLOAD_MIME_TYPES = {"text/plain", "application/octet-stream", ""}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


async def validate_and_read_log_upload(file: UploadFile) -> bytes:
    safe_name = PurePath(file.filename or "").name
    if safe_name != (file.filename or ""):
        raise HTTPException(status_code=400, detail="Invalid file name.")

    suffix = PurePath(safe_name).suffix.lower()
    if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .log and .txt files are allowed.")

    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_UPLOAD_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file content type.")

    payload = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit.")

    await file.seek(0)
    return payload
