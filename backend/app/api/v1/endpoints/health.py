"""
Health check and readiness API endpoints.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Query, status
from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.health import HealthResponse, DatabaseHealth

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Readiness Check",
    description="Returns the operational status, version, and optional database connectivity check for RiskShield AI.",
)
async def health_check(
    check_db: bool = Query(
        default=False,
        description="Include database connectivity probe in health check response",
    )
) -> HealthResponse:
    db_health: Optional[DatabaseHealth] = None
    if check_db:
        db_res = await check_database_connection()
        db_health = DatabaseHealth(
            status=db_res["status"],
            database=db_res.get("database"),
            error=db_res.get("error"),
        )

    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        database=db_health,
    )
