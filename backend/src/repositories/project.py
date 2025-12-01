"""Project repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.project import Project
from src.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        super().__init__(Project, db)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """
        Get projects by user ID.

        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of projects
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id},
        )

    async def get_by_user_and_status(
        self,
        user_id: UUID,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """
        Get projects by user ID and status.

        Args:
            user_id: User UUID
            status: Project status
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of projects
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id, "status": status},
        )

    async def get_with_photos(self, project_id: UUID) -> Project | None:
        """
        Get project with eagerly loaded photos.

        Args:
            project_id: Project UUID

        Returns:
            Project with photos or None
        """
        query = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.photos))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_shopping_list(self, project_id: UUID) -> Project | None:
        """
        Get project with eagerly loaded shopping list.

        Args:
            project_id: Project UUID

        Returns:
            Project with shopping list or None
        """
        query = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.shopping_list))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_all_relations(self, project_id: UUID) -> Project | None:
        """
        Get project with all relations eagerly loaded.

        Args:
            project_id: Project UUID

        Returns:
            Project with photos and shopping list or None
        """
        query = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.photos),
                selectinload(Project.shopping_list),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: UUID) -> int:
        """
        Count projects by user ID.

        Args:
            user_id: User UUID

        Returns:
            Count of user's projects
        """
        return await self.count(filters={"user_id": user_id})

    async def count_by_status(self, status: str) -> int:
        """
        Count projects by status.

        Args:
            status: Project status

        Returns:
            Count of projects with specified status
        """
        return await self.count(filters={"status": status})
