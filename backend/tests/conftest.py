"""
Pytest configuration and shared fixtures for backend tests.
"""

from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
import app.core.database as db_module
from app.models import (
    Transaction,
    Entity,
    TransactionEntity,
    AnalysisRun,
    Finding,
    FindingEntity,
    FindingTransaction,
    Assessment,
    Case,
    CaseNote,
    CaseAuditEvent,
)


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Configure settings for test environment
settings.ENVIRONMENT = "test"
settings.DATABASE_URL = TEST_DATABASE_URL
settings.RATE_LIMIT_ENABLED = False

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Point core database module engine to test engine
db_module._engine = test_engine

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
db_module._session_factory = TestingSessionLocal


@pytest.fixture(autouse=True)
async def setup_test_database():
    """
    Explicit test database table setup and teardown per test function.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an isolated async test session.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def app_settings():
    """Provides application settings instance."""
    return settings


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client fixture with overridden database dependency and default admin API key.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    # Provide default dev/test admin API key header for standard test flows
    default_headers = {"X-API-Key": "rs_admin_key_dev"}
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=default_headers,
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def unauthenticated_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client fixture without authentication headers for testing security enforcement.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
