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

# Sync engine for migrations
sync_engine = create_engine(
    str(settings.database_url),
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.db_echo,
)

# Sync session factory
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# Async engine for FastAPI
async_database_url = str(settings.database_url).replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    async_database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=settings.db_echo,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


def get_sync_db() -> Session:
    """
    Get synchronous database session for migrations and scripts.

    Yields:
        Session: SQLAlchemy synchronous session

    Example:
        with get_sync_db() as db:
            user = db.query(UserProfile).first()
    """
    db = SyncSessionLocal()
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
    async with AsyncSessionLocal() as session:
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
    async with AsyncSessionLocal() as session:
        yield session


def create_tables() -> None:
    """
    Create all database tables.

    Note: This is only used for testing. Production uses Alembic migrations.
    """
    Base.metadata.create_all(bind=sync_engine)


def drop_tables() -> None:
    """
    Drop all database tables.

    Note: This is only used for testing. Production uses Alembic migrations.
    """
    Base.metadata.drop_all(bind=sync_engine)
