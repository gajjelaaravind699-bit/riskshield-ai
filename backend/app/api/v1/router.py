"""
API v1 Router aggregation with security dependencies.
"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_auth, require_analyst, require_ingest
from app.api.v1.endpoints import (
    health_router,
    transactions_router,
    analysis_router,
    assessments_router,
    cases_router,
)

api_v1_router = APIRouter()

# 1. Public Health & Probes Router
api_v1_router.include_router(health_router)

# 2. Protected Business Domain Routers
api_v1_router.include_router(
    transactions_router,
    dependencies=[Depends(require_ingest)],
)
api_v1_router.include_router(
    analysis_router,
    dependencies=[Depends(require_analyst)],
)
api_v1_router.include_router(
    assessments_router,
    dependencies=[Depends(require_analyst)],
)
api_v1_router.include_router(
    cases_router,
    dependencies=[Depends(require_analyst)],
)

# Alias for compatibility
api_router = api_v1_router
