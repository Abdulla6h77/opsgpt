import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.rate_limit import limiter
from ..core.security import verify_api_key
from ..models.anomaly import Anomaly
from ..models.incident import Incident
from ..models.log_batch import LogBatch
from ..schemas.anomaly import AnomalyListResponse, AnomalyResponse, DetectAnomalyResponse
from ..services.anomaly_client import detect_anomalies
from ..services.llm_agent import LLMAgent
from ..services.log_parser import parse_logs
from ..utils.helpers import validate_and_read_log_upload
from ai.explain import explain_anomaly
from ai.incident import generate_incident_report, generate_summary
from ai.remediation import suggest_fix
from ai.severity import calculate_severity

router = APIRouter(prefix="/anomalies", tags=["Anomalies"], dependencies=[Depends(verify_api_key)])
logger = logging.getLogger(__name__)


def _normalize_timestamp(value: object) -> datetime:
    # Handles strings, datetime, and pandas.Timestamp while forcing tz-aware UTC.
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    return datetime.now(timezone.utc)


@limiter.limit("100/minute")
@router.post(
    "/detect",
    response_model=DetectAnomalyResponse,
    summary="Detect anomalies from uploaded logs",
    description="Runs anomaly detection, enriches results, and persists log batches/incidents/anomalies.",
    responses={
        200: {"description": "Anomaly detection completed."},
        500: {"description": "An error occurred while processing anomalies."},
    },
)
async def detect(request: Request, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    raw = await validate_and_read_log_upload(file)
    logs = parse_logs(raw.decode("utf-8"))

    anomalies = detect_anomalies([log.model_dump() for log in logs])

    # Add explanation and severity for every detected anomaly before reporting.
    
    for log in anomalies:
        log["explanation"] = explain_anomaly(log)
        log["severity"] = calculate_severity(log)

        remediation = suggest_fix(log)
        log["root_cause"] = remediation["root_cause"]
        log["suggested_fix"] = remediation["suggested_fix"]

    report = generate_incident_report(anomalies)
    summary = generate_summary(report)
    ai_analysis = None
    if anomalies:
        # Optional enrichment layer. Failures never interrupt the pipeline.
    ai_analysis = LLMAgent().analyze_incident(anomalies, report)
    persisted_anomalies = 0

    try:
        # Track upload batch even if no anomalies are detected.
        batch = LogBatch(filename=file.filename or "unknown.log")
        logger.info("Inserting log batch filename='%s'", batch.filename)
        db.add(batch)

        if anomalies:
            rule_root_cause = anomalies[0].get("root_cause", "Unknown root cause")
            rule_remediation = anomalies[0].get("suggested_fix", "Manual investigation required")
            use_ai = bool(ai_analysis) and float(ai_analysis.get("confidence_score", 0.0)) > 0.0

            incident = Incident(
                service_name=report.get("most_affected_service", "unknown-service"),
                severity=report.get("highest_severity", "LOW"),
                summary=summary,
                root_cause=ai_analysis.get("ai_root_cause", rule_root_cause) if use_ai else rule_root_cause,
                remediation=ai_analysis.get("ai_remediation", rule_remediation) if use_ai else rule_remediation,
            )
            logger.info("Inserting incident service='%s' severity='%s'", incident.service_name, incident.severity)
            db.add(incident)
            await db.flush()

            for anomaly in anomalies:
                anomaly_ts = _normalize_timestamp(anomaly.get("timestamp"))

                row = Anomaly(
                    incident_id=incident.id,
                    anomaly_score=float(anomaly.get("anomaly", 1.0)),
                    raw_log=json.dumps(anomaly, default=str),
                    timestamp=anomaly_ts,
                )
                logger.info("Inserting anomaly for incident_id='%s'", incident.id)
                db.add(row)

            persisted_anomalies = len(anomalies)

        await db.commit()
        logger.info("DB commit successful file='%s' anomalies_persisted=%d", file.filename or "unknown.log", persisted_anomalies)

        await db.refresh(batch)
        if anomalies:
            await db.refresh(incident)

    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Database transaction failed in /anomalies/detect")
        raise HTTPException(status_code=500, detail="Database operation failed.") from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("Unexpected failure in /anomalies/detect")
        raise HTTPException(status_code=500, detail="Unexpected server error.") from exc

    return {
        "total_logs": len(logs),
        "anomalies_detected": len(anomalies),
        "incident_report": report,
        "incident_summary": summary,
        "anomalies": anomalies[:20],
    }


@limiter.limit("100/minute")
@router.get(
    "",
    response_model=AnomalyListResponse,
    summary="List anomalies",
    description="Returns paginated anomalies with optional severity/status/date filtering.",
    responses={200: {"description": "Paginated list of anomalies."}},
)
async def list_anomalies(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if severity:
        filters.append(Incident.severity == severity)
    if status:
        filters.append(Incident.status == status)
    if start_date:
        filters.append(Anomaly.timestamp >= start_date)
    if end_date:
        filters.append(Anomaly.timestamp <= end_date)

    total_stmt = select(func.count(Anomaly.id)).join(Incident, Anomaly.incident_id == Incident.id)
    data_stmt = (
        select(Anomaly)
        .join(Incident, Anomaly.incident_id == Incident.id)
        .order_by(Anomaly.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )

    if filters:
        total_stmt = total_stmt.where(*filters)
        data_stmt = data_stmt.where(*filters)

    try:
        total = (await db.execute(total_stmt)).scalar_one()
        anomalies = (await db.execute(data_stmt)).scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Database read failed in /anomalies")
        raise HTTPException(status_code=500, detail="Database operation failed.") from exc

    return AnomalyListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[AnomalyResponse.model_validate(item) for item in anomalies],
    )
