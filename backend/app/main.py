"""
RiskShield AI — Main FastAPI Application Entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_v1_router
from app.schemas.health import HealthResponse
from datetime import datetime, timezone

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "RiskShield AI — Abuse-Ring Sentinel Backend API.\n\n"
        "Decision-support system for detecting coordinated payment abuse, "
        "identifying fraud clusters, and generating auditable risk evaluations."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include Versioned API Routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get(
    "/",
    summary="Root Welcome & Service Metadata",
    tags=["Root"],
)
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_STR}/health",
        "description": "Abuse-Ring Sentinel & Payment Fraud Decision-Support Engine",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Root Health Check Probe",
    tags=["Health"],
)
async def root_health_check():
    """
    Standard top-level health probe for container orchestrators and load balancers.
    """
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
    )
