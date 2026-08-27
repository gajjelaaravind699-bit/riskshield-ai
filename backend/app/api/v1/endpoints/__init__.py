"""
API v1 endpoints package initialization.
"""

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.transactions import router as transactions_router
from app.api.v1.endpoints.analysis import router as analysis_router

__all__ = [
    "health_router",
    "transactions_router",
    "analysis_router",
]
