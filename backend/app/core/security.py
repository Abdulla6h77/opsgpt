import hmac
import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
logger = logging.getLogger(__name__)


def is_valid_api_key(value: str | None) -> bool:
    # Never pass if the server-side key is unconfigured.
    if not settings.security_api_key.strip():
        return False
    candidate = value or ""
    return hmac.compare_digest(candidate, settings.security_api_key)


def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    if not settings.security_api_key.strip():
        logger.error("auth_failed reason=missing_server_api_key")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if not is_valid_api_key(api_key):
        logger.warning("auth_failed reason=invalid_api_key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
