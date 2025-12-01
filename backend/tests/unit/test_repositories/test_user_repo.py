"""Tests for UserRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserProfile
from src.repositories.user import UserRepository


class TestUserRepository:
    """Tests for UserRepository methods."""

    @pytest.fixture
    async def user_repo(self, test_db: AsyncSession) -> UserRepository:
        """Create UserRepository instance."""
        return UserRepository(test_db)

    @pytest.fixture
    async def sample_user(self, user_repo: UserRepository) -> UserProfile:
        """Create a sample user for testing."""
        return await user_repo.create({
            "skill_level": "intermediate",
            "company_name": "Test Company",
        })

    async def test_get_with_projects(
        self, user_repo: UserRepository, sample_user: UserProfile
    ) -> None:
        """Test getting user with eagerly loaded projects."""
        user = await user_repo.get_with_projects(sample_user.id)
        assert user is not None
        assert user.id == sample_user.id
        # Projects relationship should be loaded (empty list for new user)
        assert user.projects == []

    async def test_get_with_subscription(
        self, user_repo: UserRepository, sample_user: UserProfile
    ) -> None:
        """Test getting user with eagerly loaded subscription."""
        user = await user_repo.get_with_subscription(sample_user.id)
        assert user is not None
        assert user.id == sample_user.id
        # Subscription relationship should be loaded (None for new user)
        assert user.subscription is None

    async def test_get_by_skill_level(
        self, user_repo: UserRepository, sample_user: UserProfile
    ) -> None:
        """Test getting users by skill level."""
        users = await user_repo.get_by_skill_level("intermediate")
        assert len(users) > 0
        assert all(u.skill_level == "intermediate" for u in users)

    async def test_get_by_skill_level_with_pagination(
        self, user_repo: UserRepository
    ) -> None:
        """Test getting users by skill level with pagination."""
        # Create multiple users
        for _ in range(5):
            await user_repo.create({"skill_level": "beginner"})

        users = await user_repo.get_by_skill_level("beginner", skip=2, limit=2)
        assert len(users) == 2

    async def test_count_by_skill_level(
        self, user_repo: UserRepository
    ) -> None:
        """Test counting users by skill level."""
        # Create users with different skill levels
        await user_repo.create({"skill_level": "expert"})
        await user_repo.create({"skill_level": "expert"})
        await user_repo.create({"skill_level": "beginner"})

        count = await user_repo.count_by_skill_level("expert")
        assert count == 2

    async def test_get_by_skill_level_no_results(
        self, user_repo: UserRepository
    ) -> None:
        """Test getting users by skill level with no results."""
        users = await user_repo.get_by_skill_level("expert")
        assert users == []

    async def test_count_by_skill_level_zero(
        self, user_repo: UserRepository
    ) -> None:
        """Test counting users by skill level with zero results."""
        count = await user_repo.count_by_skill_level("expert")
        assert count == 0
