"""User profile repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import UserProfile
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserProfile]):
    """Repository for UserProfile operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        super().__init__(UserProfile, db)

    async def get_with_projects(self, user_id: UUID) -> UserProfile | None:
        """
        Get user with eagerly loaded projects.

        Args:
            user_id: User UUID

        Returns:
            User profile with projects or None
        """
        query = (
            select(UserProfile)
            .where(UserProfile.id == user_id)
            .options(selectinload(UserProfile.projects))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_subscription(self, user_id: UUID) -> UserProfile | None:
        """
        Get user with eagerly loaded subscription.

        Args:
            user_id: User UUID

        Returns:
            User profile with subscription or None
        """
        query = (
            select(UserProfile)
            .where(UserProfile.id == user_id)
            .options(selectinload(UserProfile.subscription))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_skill_level(
        self,
        skill_level: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[UserProfile]:
        """
        Get users by skill level.

        Args:
            skill_level: Skill level ('beginner', 'intermediate', 'expert')
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of user profiles
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"skill_level": skill_level},
        )

    async def count_by_skill_level(self, skill_level: str) -> int:
        """
        Count users by skill level.

        Args:
            skill_level: Skill level to count

        Returns:
            Count of users with specified skill level
        """
        return await self.count(filters={"skill_level": skill_level})
