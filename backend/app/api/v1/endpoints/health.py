"""
Health, Liveness, and Readiness API endpoints.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Query, Response, status
from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.health import (
    HealthResponse,
    DatabaseHealth,
    LivenessResponse,
    ReadinessResponse,
)

router = APIRouter()


@router.get(
    "/health/liveness",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Returns HTTP 200 indicating the FastAPI application process is alive.",
    tags=["Health & Probes"],
)
async def liveness_probe() -> LivenessResponse:
    return LivenessResponse(
        status="alive",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/health/readiness",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Returns HTTP 200 if the database is reachable, or HTTP 503 if the database is disconnected.",
    tags=["Health & Probes"],
)
async def readiness_probe(response: Response) -> ReadinessResponse:
    db_res = await check_database_connection()
    is_connected = db_res.get("status") == "connected"

    if not is_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    db_health = DatabaseHealth(
        status=db_res["status"],
        database=db_res.get("database"),
        error=db_res.get("error"),
    )

    return ReadinessResponse(
        status="ready" if is_connected else "not_ready",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        database=db_health,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="General Health Check",
    description="Returns the operational status, version, and optional database connectivity check for RiskShield AI.",
    tags=["Health & Probes"],
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
