import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import verify_api_key
from ..models.incident import Incident
from ..schemas.debug import DebugInsertResponse

router = APIRouter(prefix="/debug", tags=["Debug"], dependencies=[Depends(verify_api_key)])
logger = logging.getLogger(__name__)


@router.post(
    "/test-db",
    response_model=DebugInsertResponse,
    summary="Test database insert",
    description="Internal endpoint to verify write access to the incidents table.",
    include_in_schema=False,
)
async def test_db_insert(db: AsyncSession = Depends(get_db)):
    incident = Incident(
        service_name="debug-service",
        severity="LOW",
        summary="Debug DB insert verification",
        root_cause="Debug test",
        remediation="No action required",
    )

    try:
        logger.info("Debug insert start for /debug/test-db")
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        logger.info("Debug insert commit successful incident_id='%s'", incident.id)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Debug insert failed due to database error")
        raise HTTPException(status_code=500, detail="Database operation failed.") from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("Debug insert failed due to unexpected error")
        raise HTTPException(status_code=500, detail="Unexpected server error.") from exc

    return {"message": "DB insert successful", "incident_id": str(incident.id)}
