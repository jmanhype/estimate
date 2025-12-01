"""Base repository with generic CRUD operations."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base

# Type variable for model class
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with generic CRUD operations.

    Type Parameters:
        ModelType: SQLAlchemy model class

    Example:
        class UserRepository(BaseRepository[UserProfile]):
            def __init__(self, db: AsyncSession):
                super().__init__(UserProfile, db)
    """

    def __init__(self, model: type[ModelType], db: AsyncSession):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> ModelType | None:
        """
        Get a record by ID.

        Args:
            id: Record UUID

        Returns:
            Model instance or None if not found
        """
        return await self.db.get(self.model, id)

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelType]:
        """
        Get multiple records with pagination and optional filters.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            filters: Dictionary of field:value filters

        Returns:
            List of model instances
        """
        query = select(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Dictionary of field values

        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj  # type: ignore[no-any-return]

    async def update(
        self,
        *,
        id: UUID,
        obj_in: dict[str, Any],
    ) -> ModelType | None:
        """
        Update an existing record.

        Args:
            id: Record UUID
            obj_in: Dictionary of field values to update

        Returns:
            Updated model instance or None if not found
        """
        db_obj = await self.get(id)
        if db_obj is None:
            return None

        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record UUID

        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get(id)
        if db_obj is None:
            return False

        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """
        Count records with optional filters.

        Args:
            filters: Dictionary of field:value filters

        Returns:
            Count of matching records
        """
        query = select(func.count()).select_from(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def exists(self, id: UUID) -> bool:
        """
        Check if a record exists by ID.

        Args:
            id: Record UUID

        Returns:
            True if exists, False otherwise
        """
        result = await self.get(id)
        return result is not None

    def _build_query(self) -> Select[tuple[ModelType]]:
        """
        Build base query for the model.

        Returns:
            SQLAlchemy select statement

        Note:
            Override this method in subclasses to add default filtering,
            ordering, or joins.
        """
        return select(self.model)
