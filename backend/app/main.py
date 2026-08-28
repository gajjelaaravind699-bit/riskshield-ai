"""
RiskShield AI — Main FastAPI Application Entrypoint.
Production-hardened with structured logging, security headers, rate limiting, and safe error handling.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.errors import register_exception_handlers
from app.core.middleware import (
    CorrelationIdMiddleware,
    SecurityHeadersMiddleware,
    RateLimiterMiddleware,
    RequestObservabilityMiddleware,
)
from app.api.v1.router import api_v1_router
from app.schemas.health import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes logging and runtime checks without executing automatic schema mutations.
    """
    configure_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "RiskShield AI — Abuse-Ring Sentinel Backend API.\n\n"
        "Enterprise decision-support platform for detecting coordinated payment abuse, "
        "identifying fraud rings, evaluating bounded risk scores, and managing human analyst investigations."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 1. Register Centralized Exception Handlers
register_exception_handlers(app)

# 2. Register Middlewares (Order of execution: outer to inner)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestObservabilityMiddleware)

if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)

if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimiterMiddleware)

if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# CORS Middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Process-Time"],
    )

# 3. Include Versioned API Routers
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
        "liveness_probe": f"{settings.API_V1_STR}/health/liveness",
        "readiness_probe": f"{settings.API_V1_STR}/health/readiness",
        "description": "Abuse-Ring Sentinel & Payment Fraud Decision-Support Engine",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Root Health Check Probe",
    tags=["Health & Probes"],
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
