import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import settings, validate_required_settings
from .core.rate_limit import limiter
from .core.logging import configure_logging
from .core.database import init_models
from .schemas.common import ErrorResponse
from .schemas.health import HealthResponse
from .routes import logs
from .routes import anomalies
from .routes import debug
from .routes import incidents


configure_logging()
logger = logging.getLogger(__name__)

openapi_tags = [
    {"name": "Health", "description": "Service health and readiness checks."},
    {"name": "Logs", "description": "Log upload and parsing endpoints."},
    {"name": "Anomalies", "description": "Anomaly detection and anomaly listing."},
    {"name": "Incidents", "description": "Incident listing and filtering endpoints."},
]


app = FastAPI(
    title="OpsGPT Backend",
    description="AI-powered Ops Co-Pilot backend with anomaly detection and incident intelligence.",
    version="0.2.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    # Security: origins loaded from settings (CORS_ORIGINS env var).
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    if response.status_code >= 500:
        logger.error("request_failed method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, elapsed_ms)
    elif response.status_code >= 400:
        logger.warning("request_warning method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, elapsed_ms)
    else:
        logger.info("request_ok method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, elapsed_ms)

    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Swagger UI uses inline scripts/styles, relax CSP only for docs endpoints.
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "frame-ancestors 'none'; base-uri 'self'"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    return response


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_: Request, exc: RateLimitExceeded):
    logger.warning("rate_limited detail=%s", exc.detail)
    payload = ErrorResponse(error="Too many requests")
    return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content=payload.model_dump(exclude_none=True))


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
    payload = ErrorResponse(error=detail)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(exclude_none=True))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logger.warning("Request validation failed")
    payload = ErrorResponse(error="Validation error")
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload.model_dump(exclude_none=True))


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError):
    if settings.is_production:
        logger.error("Database exception encountered")
    else:
        logger.exception("Database exception encountered")
    payload = ErrorResponse(error="Database operation failed")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump(exclude_none=True))


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    if settings.is_production:
        logger.error("Unhandled exception encountered")
    else:
        logger.exception("Unhandled exception encountered")
    payload = ErrorResponse(error="Internal server error")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump(exclude_none=True))


app.include_router(logs.router)
app.include_router(anomalies.router)
app.include_router(incidents.router)
if not settings.is_production:
    app.include_router(debug.router)


@app.on_event("startup")
async def on_startup() -> None:
    try:
        settings.ensure_runtime_secrets()
        validate_required_settings()
        await init_models()
        logger.info("Application startup completed successfully")
    except Exception:
        logger.exception("Database startup initialization failed")
        raise


@app.get(
    "/",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Legacy root health",
    description="Legacy health endpoint kept for backward compatibility.",
)
def root_health_check():
    return {"status": "ok"}


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Service liveness endpoint.",
    responses={200: {"description": "Service is healthy."}},
)
def health_check():
    return {"status": "ok"}
