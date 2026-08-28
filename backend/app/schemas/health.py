"""
Health check and system readiness response schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    status: str = Field(..., description="Database connection status ('connected' or 'disconnected')")
    database: Optional[str] = Field(None, description="Database identifier if connected")
    error: Optional[str] = Field(None, description="Sanitized status message if disconnected")


class LivenessResponse(BaseModel):
    status: str = Field("alive", description="Process liveness indicator")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Current server UTC timestamp")


class ReadinessResponse(BaseModel):
    status: str = Field(..., description="Readiness status ('ready' or 'not_ready')")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Current running environment")
    timestamp: datetime = Field(..., description="Current server UTC timestamp")
    database: DatabaseHealth = Field(..., description="Database connectivity status")


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Overall application status")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Current running environment")
    timestamp: datetime = Field(..., description="Current server UTC timestamp")
    database: Optional[DatabaseHealth] = Field(None, description="Database readiness check details")
