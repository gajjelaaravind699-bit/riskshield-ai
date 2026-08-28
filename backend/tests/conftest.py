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

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


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
    Async HTTP client fixture with overridden database dependency.
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
