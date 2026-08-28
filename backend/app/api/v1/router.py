"""
API v1 Router aggregation.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    health_router,
    transactions_router,
    analysis_router,
    assessments_router,
    cases_router,
)

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(assessments_router)
api_v1_router.include_router(cases_router)

# Alias for compatibility
api_router = api_v1_router
