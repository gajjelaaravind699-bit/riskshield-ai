"""
Pytest configuration and shared fixtures for backend tests.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings


@pytest.fixture
def app_settings():
    """Provides application settings instance."""
    return settings


@pytest.fixture
async def async_client():
    """
    Async HTTP client fixture for testing FastAPI endpoints.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
