"""Tests for database configuration and session management."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.core.database import (
    Base,
    create_tables,
    drop_tables,
    get_async_db,
    get_async_engine,
    get_async_session_factory,
    get_db_context,
    get_sync_db,
    get_sync_engine,
    get_sync_session_factory,
)


class TestDatabaseConfiguration:
    """Tests for database configuration functions."""

    def test_get_sync_engine(self) -> None:
        """Test getting sync engine."""
        engine = get_sync_engine()
        assert engine is not None
        # Calling again should return same instance
        engine2 = get_sync_engine()
        assert engine is engine2

    def test_get_sync_session_factory(self) -> None:
        """Test getting sync session factory."""
        factory = get_sync_session_factory()
        assert factory is not None
        # Calling again should return same instance
        factory2 = get_sync_session_factory()
        assert factory is factory2

    def test_get_async_engine(self) -> None:
        """Test getting async engine."""
        engine = get_async_engine()
        assert engine is not None
        # Calling again should return same instance
        engine2 = get_async_engine()
        assert engine is engine2

    def test_get_async_session_factory(self) -> None:
        """Test getting async session factory."""
        factory = get_async_session_factory()
        assert factory is not None
        # Calling again should return same instance
        factory2 = get_async_session_factory()
        assert factory is factory2

    def test_get_sync_db(self) -> None:
        """Test getting sync database session."""
        gen = get_sync_db()
        session = next(gen)
        assert isinstance(session, Session)
        # Clean up
        try:
            next(gen)
        except StopIteration:
            pass

    async def test_get_async_db(self) -> None:
        """Test getting async database session."""
        async_gen = get_async_db()
        session = await async_gen.__anext__()
        assert isinstance(session, AsyncSession)
        # Clean up
        try:
            await async_gen.__anext__()
        except StopAsyncIteration:
            pass

    async def test_get_db_context(self) -> None:
        """Test getting database context manager."""
        async with get_db_context() as session:
            assert isinstance(session, AsyncSession)

    def test_create_tables(self) -> None:
        """Test creating tables."""
        # This should not raise an error
        create_tables()

    def test_drop_tables(self) -> None:
        """Test dropping tables."""
        # This should not raise an error
        # Note: This is destructive, so we recreate afterward
        drop_tables()
        create_tables()


class TestBaseModel:
    """Tests for Base declarative class."""

    def test_base_exists(self) -> None:
        """Test that Base class exists and is properly configured."""
        assert Base is not None
        assert hasattr(Base, "metadata")
