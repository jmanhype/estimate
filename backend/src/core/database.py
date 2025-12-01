"""Database configuration and session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings

# Create SQLAlchemy base class
Base = declarative_base()

# Sync engine for migrations (created lazily to avoid import errors)
_sync_engine: Any | None = None
_sync_session_factory: sessionmaker[Session] | None = None


def get_sync_engine() -> Any:
    """Get or create sync engine."""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(
            str(settings.database_url),
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_pre_ping=True,  # Verify connections before using
            echo=settings.db_echo,
        )
    return _sync_engine


def get_sync_session_factory() -> sessionmaker[Session]:
    """Get or create sync session factory."""
    global _sync_session_factory
    if _sync_session_factory is None:
        _sync_session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_sync_engine(),
        )
    return _sync_session_factory

# Async engine for FastAPI (created lazily to avoid import errors in migrations)
_async_engine: Any | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_async_engine() -> Any:
    """Get or create async engine."""
    global _async_engine
    if _async_engine is None:
        async_database_url = str(settings.database_url).replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        _async_engine = create_async_engine(
            async_database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=settings.db_echo,
        )
    return _async_engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _async_session_factory


def get_sync_db() -> AsyncGenerator[Session, None]:  # type: ignore[misc]
    """
    Get synchronous database session for migrations and scripts.

    Yields:
        Session: SQLAlchemy synchronous session

    Example:
        with get_sync_db() as db:
            user = db.query(UserProfile).first()
    """
    session_factory = get_sync_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get asynchronous database session for FastAPI dependencies.

    Yields:
        AsyncSession: SQLAlchemy asynchronous session

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(UserProfile))
            return result.scalars().all()
    """
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions in non-FastAPI code.

    Yields:
        AsyncSession: SQLAlchemy asynchronous session

    Example:
        async with get_db_context() as db:
            user = await db.get(UserProfile, user_id)
    """
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        yield session


def create_tables() -> None:
    """
    Create all database tables.

    Note: This is only used for testing. Production uses Alembic migrations.
    """
    Base.metadata.create_all(bind=get_sync_engine())


def drop_tables() -> None:
    """
    Drop all database tables.

    Note: This is only used for testing. Production uses Alembic migrations.
    """
    Base.metadata.drop_all(bind=get_sync_engine())
