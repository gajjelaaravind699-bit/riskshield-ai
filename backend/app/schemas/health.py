"""
Health check and system readiness response schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    status: str = Field(..., description="Database connection status ('connected' or 'disconnected')")
    database: Optional[str] = Field(None, description="Database name if connected")
    error: Optional[str] = Field(None, description="Error message if disconnected")


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Overall application status")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Current running environment")
    timestamp: datetime = Field(..., description="Current server UTC timestamp")
    database: Optional[DatabaseHealth] = Field(None, description="Database readiness check details")
