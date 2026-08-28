"""
Database session management, connection reliability, and pooling utilities.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.core.config import settings

Base = declarative_base()

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        # SQLite dialect does not support pool_size / max_overflow
        is_sqlite = settings.async_database_uri.startswith("sqlite")
        engine_kwargs = {
            "echo": False,
            "future": True,
            "pool_pre_ping": settings.DB_POOL_PRE_PING,
        }
        if not is_sqlite:
            engine_kwargs.update({
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE,
            })

        _engine = create_async_engine(
            settings.async_database_uri,
            **engine_kwargs,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions in endpoints.
    Alembic remains the only schema migration mechanism — no tables are auto-created at runtime.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> dict:
    """
    Diagnostic helper to ping the database for readiness probes.
    Never exposes passwords, hostnames, or connection credentials.
    """
    try:
        engine = get_engine()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": settings.POSTGRES_DB if not settings.DATABASE_URL or "postgres" in settings.DATABASE_URL else "configured_db",
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": "Database connection unreachable",
        }
