"""Tests for UserRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserProfile
from src.repositories.user import UserRepository


class TestUserRepository:
    """Tests for UserRepository CRUD operations."""

    @pytest.fixture
    async def user_repo(self, test_db: AsyncSession) -> UserRepository:
        """Create UserRepository instance."""
        return UserRepository(test_db)

    @pytest.fixture
    async def sample_user(self, user_repo: UserRepository) -> UserProfile:
        """Create a sample user for testing."""
        user = await user_repo.create({
            "skill_level": "intermediate",
            "company_name": "Test Company",
        })
        return user

    async def test_get_by_id(
        self, user_repo: UserRepository, sample_user: UserProfile
    ) -> None:
        """Test getting user by ID."""
        user = await user_repo.get(sample_user.id)
        assert user is not None
        assert user.id == sample_user.id
        assert user.skill_level == "intermediate"

    async def test_get_by_skill_level(
        self, user_repo: UserRepository, sample_user: UserProfile
    ) -> None:
        """Test getting users by skill level."""
        users = await user_repo.get_by_skill_level("intermediate")
        assert len(users) > 0
        assert all(u.skill_level == "intermediate" for u in users)

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

    async def test_has_active_subscription_without_subscription(
        self, user_repo: UserRepository, sample_user: UserProfile
    ) -> None:
        """Test checking for active subscription when user has none."""
        has_sub = await user_repo.has_active_subscription(sample_user.id)
        assert has_sub is False

    async def test_get_nonexistent_user(self, user_repo: UserRepository) -> None:
        """Test getting a user that doesn't exist."""
        from uuid import uuid4
        user = await user_repo.get(uuid4())
        assert user is None

    async def test_get_by_skill_level_no_results(
        self, user_repo: UserRepository
    ) -> None:
        """Test getting users by skill level with no results."""
        users = await user_repo.get_by_skill_level("expert")
        assert users == []

    async def test_create_user_minimal_fields(
        self, user_repo: UserRepository
    ) -> None:
        """Test creating user with only required fields."""
        user = await user_repo.create({"skill_level": "beginner"})
        assert user.skill_level == "beginner"
        assert user.company_name is None

    async def test_create_user_all_fields(
        self, user_repo: UserRepository
    ) -> None:
        """Test creating user with all fields."""
        user = await user_repo.create({
            "skill_level": "expert",
            "company_name": "Expert Renovations LLC",
        })
        assert user.skill_level == "expert"
        assert user.company_name == "Expert Renovations LLC"
