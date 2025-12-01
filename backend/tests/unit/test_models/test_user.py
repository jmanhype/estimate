"""Comprehensive tests for UserProfile model."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models.user import UserProfile


class TestUserProfileModel:
    """Test UserProfile model structure and validation."""

    @pytest.mark.asyncio
    async def test_create_user_profile_with_required_fields(
        self, test_session
    ) -> None:
        """UserProfile should be created with only required fields."""
        user_id = uuid4()
        user = UserProfile(
            id=user_id,
            skill_level="beginner",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        assert user.id == user_id
        assert user.skill_level == "beginner"
        assert user.company_name is None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_create_user_profile_with_all_fields(
        self, test_session
    ) -> None:
        """UserProfile should be created with all fields including optional ones."""
        user_id = uuid4()
        user = UserProfile(
            id=user_id,
            skill_level="expert",
            company_name="Test Construction Co.",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        assert user.id == user_id
        assert user.skill_level == "expert"
        assert user.company_name == "Test Construction Co."

    @pytest.mark.asyncio
    async def test_user_profile_auto_generated_uuid(
        self, test_session
    ) -> None:
        """UserProfile should auto-generate UUID if not provided."""
        user = UserProfile(
            skill_level="intermediate",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        assert isinstance(user.id, UUID)
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_user_profile_auto_timestamps(
        self, test_session
    ) -> None:
        """UserProfile should auto-generate timestamps."""
        before_create = datetime.now(UTC)

        user = UserProfile(
            skill_level="beginner",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        after_create = datetime.now(UTC)

        assert before_create <= user.created_at <= after_create
        assert before_create <= user.updated_at <= after_create
        # Timestamps should be very close on creation (within 1 second)
        assert abs((user.created_at - user.updated_at).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_user_profile_updated_at_changes_on_update(
        self, test_session
    ) -> None:
        """UserProfile.updated_at should change when record is updated."""
        user = UserProfile(
            skill_level="beginner",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        original_updated_at = user.updated_at

        # Update user
        user.skill_level = "intermediate"
        await test_session.commit()
        await test_session.refresh(user)

        assert user.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_user_profile_unique_id_constraint(
        self, test_session
    ) -> None:
        """UserProfile should enforce unique ID constraint."""
        user_id = uuid4()

        user1 = UserProfile(
            id=user_id,
            skill_level="beginner",
        )
        test_session.add(user1)
        await test_session.commit()

        # Try to create another user with same ID
        user2 = UserProfile(
            id=user_id,
            skill_level="expert",
        )
        test_session.add(user2)

        with pytest.raises(IntegrityError):
            await test_session.commit()

    @pytest.mark.asyncio
    async def test_user_profile_skill_level_values(
        self, test_session
    ) -> None:
        """UserProfile should accept all valid skill levels."""
        valid_skill_levels = ["beginner", "intermediate", "expert"]

        for skill_level in valid_skill_levels:
            user = UserProfile(
                skill_level=skill_level,
            )
            test_session.add(user)
            await test_session.commit()
            await test_session.refresh(user)

            assert user.skill_level == skill_level
            await test_session.delete(user)
            await test_session.commit()

    @pytest.mark.asyncio
    async def test_user_profile_repr(self, test_session) -> None:
        """UserProfile __repr__ should return useful string representation."""
        user_id = uuid4()
        user = UserProfile(
            id=user_id,
            skill_level="beginner",
        )

        repr_str = repr(user)

        assert "UserProfile" in repr_str
        assert str(user_id) in repr_str
        assert "beginner" in repr_str


class TestUserProfileRelationships:
    """Test UserProfile relationships with other models."""

    @pytest.mark.asyncio
    async def test_user_profile_has_projects_relationship(
        self, test_session
    ) -> None:
        """UserProfile should have projects relationship."""
        user = UserProfile(
            skill_level="beginner",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user, ["projects"])

        # Should have projects attribute (empty list initially)
        assert hasattr(user, "projects")
        assert isinstance(user.projects, list)
        assert len(user.projects) == 0

    @pytest.mark.asyncio
    async def test_user_profile_has_subscription_relationship(
        self, test_session
    ) -> None:
        """UserProfile should have subscription relationship."""
        user = UserProfile(
            skill_level="beginner",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user, ["subscription"])

        # Should have subscription attribute (None initially)
        assert hasattr(user, "subscription")
        assert user.subscription is None


class TestUserProfileQueries:
    """Test UserProfile database queries."""

    @pytest.mark.asyncio
    async def test_query_user_by_id(self, test_session) -> None:
        """Should be able to query user by ID."""
        user = UserProfile(
            skill_level="intermediate",
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        # Query by ID
        result = await test_session.get(UserProfile, user.id)

        assert result is not None
        assert result.id == user.id
        assert result.skill_level == "intermediate"

    @pytest.mark.asyncio
    async def test_query_users_by_skill_level(self, test_session) -> None:
        """Should be able to query users by skill level."""
        # Create multiple users
        users = [
            UserProfile(skill_level="beginner"),
            UserProfile(skill_level="beginner"),
            UserProfile(skill_level="expert"),
        ]

        for user in users:
            test_session.add(user)
        await test_session.commit()

        # Query beginners
        query = select(UserProfile).where(UserProfile.skill_level == "beginner")
        result = await test_session.execute(query)
        beginners = list(result.scalars().all())

        assert len(beginners) == 2
        assert all(u.skill_level == "beginner" for u in beginners)

    @pytest.mark.asyncio
    async def test_query_users_with_company(self, test_session) -> None:
        """Should be able to query users with company name."""
        users = [
            UserProfile(skill_level="beginner", company_name="Company A"),
            UserProfile(skill_level="expert", company_name="Company B"),
            UserProfile(skill_level="intermediate"),  # No company
        ]

        for user in users:
            test_session.add(user)
        await test_session.commit()

        # Query users with company
        query = select(UserProfile).where(UserProfile.company_name.isnot(None))
        result = await test_session.execute(query)
        with_company = list(result.scalars().all())

        assert len(with_company) == 2
        assert all(u.company_name is not None for u in with_company)

    @pytest.mark.asyncio
    async def test_delete_user_profile(self, test_session) -> None:
        """Should be able to delete a user profile."""
        user = UserProfile(
            skill_level="beginner",
        )

        test_session.add(user)
        await test_session.commit()
        user_id = user.id

        # Delete user
        await test_session.delete(user)
        await test_session.commit()

        # Verify deleted
        result = await test_session.get(UserProfile, user_id)
        assert result is None
