import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.rate_limit import limiter
from ..core.security import verify_api_key
from ..models.incident import Incident
from ..schemas.incident import IncidentListResponse, IncidentResponse

router = APIRouter(prefix="/incidents", tags=["Incidents"], dependencies=[Depends(verify_api_key)])
logger = logging.getLogger(__name__)


@limiter.limit("100/minute")
@router.get(
    "",
    response_model=IncidentListResponse,
    summary="List incidents",
    description="Returns paginated incidents with optional severity, status, and date filters.",
    responses={200: {"description": "Paginated list of incidents."}},
)
async def list_incidents(
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
        filters.append(Incident.created_at >= start_date)
    if end_date:
        filters.append(Incident.created_at <= end_date)

    total_stmt = select(func.count(Incident.id))
    data_stmt = select(Incident).order_by(Incident.created_at.desc()).limit(limit).offset(offset)
    if filters:
        total_stmt = total_stmt.where(*filters)
        data_stmt = data_stmt.where(*filters)

    try:
        total = (await db.execute(total_stmt)).scalar_one()
        incidents = (await db.execute(data_stmt)).scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Database read failed in /incidents")
        raise HTTPException(status_code=500, detail="Database operation failed.") from exc

    return IncidentListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[IncidentResponse.model_validate(item) for item in incidents],
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
@limiter.limit("100/minute")
async def get_incident(
    request: Request,
    incident_id: int,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
