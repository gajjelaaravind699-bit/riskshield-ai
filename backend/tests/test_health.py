"""
Unit and integration tests for RiskShield AI Health and Root endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Test root endpoint returns service metadata."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "RiskShield AI"
    assert "version" in data
    assert data["docs_url"] == "/docs"
    assert data["health_check"] == "/api/v1/health"


@pytest.mark.asyncio
async def test_api_v1_health_endpoint(async_client: AsyncClient):
    """Test /api/v1/health endpoint returns 200 OK and valid schema."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "RiskShield AI"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    assert data["database"] is None


@pytest.mark.asyncio
async def test_root_health_endpoint_alias(async_client: AsyncClient):
    """Test top-level /health endpoint returns 200 OK."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "RiskShield AI"


@pytest.mark.asyncio
async def test_openapi_schema(async_client: AsyncClient):
    """Test OpenAPI JSON specification is available and valid."""
    response = await async_client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]
