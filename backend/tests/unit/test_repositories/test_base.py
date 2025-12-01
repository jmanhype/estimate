"""Comprehensive tests for BaseRepository."""

from uuid import uuid4

import pytest

from src.models.user import UserProfile
from src.repositories.base import BaseRepository


class TestBaseRepositoryCreate:
    """Test BaseRepository create operations."""

    @pytest.mark.asyncio
    async def test_create_record(self, test_session) -> None:
        """Should create a new record."""
        repo = BaseRepository(UserProfile, test_session)

        user_data = {
            "skill_level": "beginner",
            "company_name": "Test Company",
        }

        user = await repo.create(user_data)

        assert user.id is not None
        assert user.skill_level == "beginner"
        assert user.company_name == "Test Company"

    @pytest.mark.asyncio
    async def test_create_with_specific_id(self, test_session) -> None:
        """Should create record with specified ID."""
        repo = BaseRepository(UserProfile, test_session)
        user_id = uuid4()

        user_data = {
            "id": user_id,
            "skill_level": "expert",
        }

        user = await repo.create(user_data)

        assert user.id == user_id
        assert user.skill_level == "expert"


class TestBaseRepositoryGet:
    """Test BaseRepository get operations."""

    @pytest.mark.asyncio
    async def test_get_existing_record(self, test_session) -> None:
        """Should retrieve existing record by ID."""
        repo = BaseRepository(UserProfile, test_session)

        # Create user
        user = await repo.create({"skill_level": "beginner"})
        user_id = user.id

        # Get user
        retrieved_user = await repo.get(user_id)

        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.skill_level == "beginner"

    @pytest.mark.asyncio
    async def test_get_nonexistent_record(self, test_session) -> None:
        """Should return None for non-existent ID."""
        repo = BaseRepository(UserProfile, test_session)
        fake_id = uuid4()

        result = await repo.get(fake_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_exists_for_existing_record(self, test_session) -> None:
        """Should return True for existing record."""
        repo = BaseRepository(UserProfile, test_session)

        user = await repo.create({"skill_level": "beginner"})

        exists = await repo.exists(user.id)

        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_for_nonexistent_record(self, test_session) -> None:
        """Should return False for non-existent record."""
        repo = BaseRepository(UserProfile, test_session)
        fake_id = uuid4()

        exists = await repo.exists(fake_id)

        assert exists is False


class TestBaseRepositoryGetMulti:
    """Test BaseRepository get_multi operations."""

    @pytest.mark.asyncio
    async def test_get_multi_without_filters(self, test_session) -> None:
        """Should retrieve multiple records without filters."""
        repo = BaseRepository(UserProfile, test_session)

        # Create multiple users
        for i in range(5):
            await repo.create({"skill_level": "beginner"})

        users = await repo.get_multi()

        assert len(users) == 5

    @pytest.mark.asyncio
    async def test_get_multi_with_pagination(self, test_session) -> None:
        """Should paginate results with skip and limit."""
        repo = BaseRepository(UserProfile, test_session)

        # Create 10 users
        for i in range(10):
            await repo.create({"skill_level": "beginner"})

        # Get first 5
        page1 = await repo.get_multi(skip=0, limit=5)
        assert len(page1) == 5

        # Get next 5
        page2 = await repo.get_multi(skip=5, limit=5)
        assert len(page2) == 5

        # Ensure different records
        page1_ids = {user.id for user in page1}
        page2_ids = {user.id for user in page2}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_get_multi_with_filters(self, test_session) -> None:
        """Should filter results by field values."""
        repo = BaseRepository(UserProfile, test_session)

        # Create users with different skill levels
        await repo.create({"skill_level": "beginner"})
        await repo.create({"skill_level": "beginner"})
        await repo.create({"skill_level": "expert"})

        # Filter by skill level
        beginners = await repo.get_multi(filters={"skill_level": "beginner"})

        assert len(beginners) == 2
        assert all(u.skill_level == "beginner" for u in beginners)

    @pytest.mark.asyncio
    async def test_get_multi_with_multiple_filters(self, test_session) -> None:
        """Should filter by multiple fields."""
        repo = BaseRepository(UserProfile, test_session)

        # Create users
        await repo.create({"skill_level": "beginner", "company_name": "Company A"})
        await repo.create({"skill_level": "beginner", "company_name": "Company B"})
        await repo.create({"skill_level": "expert", "company_name": "Company A"})

        # Filter by both fields
        results = await repo.get_multi(
            filters={"skill_level": "beginner", "company_name": "Company A"}
        )

        assert len(results) == 1
        assert results[0].skill_level == "beginner"
        assert results[0].company_name == "Company A"

    @pytest.mark.asyncio
    async def test_get_multi_empty_result(self, test_session) -> None:
        """Should return empty list when no matches found."""
        repo = BaseRepository(UserProfile, test_session)

        users = await repo.get_multi(filters={"skill_level": "nonexistent"})

        assert users == []


class TestBaseRepositoryUpdate:
    """Test BaseRepository update operations."""

    @pytest.mark.asyncio
    async def test_update_existing_record(self, test_session) -> None:
        """Should update existing record."""
        repo = BaseRepository(UserProfile, test_session)

        # Create user
        user = await repo.create({"skill_level": "beginner"})

        # Update user
        updated = await repo.update(
            id=user.id,
            obj_in={"skill_level": "expert", "company_name": "New Company"}
        )

        assert updated is not None
        assert updated.id == user.id
        assert updated.skill_level == "expert"
        assert updated.company_name == "New Company"

    @pytest.mark.asyncio
    async def test_update_partial_fields(self, test_session) -> None:
        """Should update only specified fields."""
        repo = BaseRepository(UserProfile, test_session)

        # Create user
        user = await repo.create({
            "skill_level": "beginner",
            "company_name": "Original Company"
        })

        # Update only skill_level
        updated = await repo.update(
            id=user.id,
            obj_in={"skill_level": "intermediate"}
        )

        assert updated.skill_level == "intermediate"
        assert updated.company_name == "Original Company"  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_nonexistent_record(self, test_session) -> None:
        """Should return None when updating non-existent record."""
        repo = BaseRepository(UserProfile, test_session)
        fake_id = uuid4()

        result = await repo.update(
            id=fake_id,
            obj_in={"skill_level": "expert"}
        )

        assert result is None


class TestBaseRepositoryDelete:
    """Test BaseRepository delete operations."""

    @pytest.mark.asyncio
    async def test_delete_existing_record(self, test_session) -> None:
        """Should delete existing record."""
        repo = BaseRepository(UserProfile, test_session)

        # Create user
        user = await repo.create({"skill_level": "beginner"})
        user_id = user.id

        # Delete user
        deleted = await repo.delete(user_id)

        assert deleted is True

        # Verify deleted
        result = await repo.get(user_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_record(self, test_session) -> None:
        """Should return False when deleting non-existent record."""
        repo = BaseRepository(UserProfile, test_session)
        fake_id = uuid4()

        deleted = await repo.delete(fake_id)

        assert deleted is False


class TestBaseRepositoryCount:
    """Test BaseRepository count operations."""

    @pytest.mark.asyncio
    async def test_count_all_records(self, test_session) -> None:
        """Should count all records without filters."""
        repo = BaseRepository(UserProfile, test_session)

        # Create users
        for i in range(7):
            await repo.create({"skill_level": "beginner"})

        count = await repo.count()

        assert count == 7

    @pytest.mark.asyncio
    async def test_count_with_filters(self, test_session) -> None:
        """Should count records matching filters."""
        repo = BaseRepository(UserProfile, test_session)

        # Create users
        await repo.create({"skill_level": "beginner"})
        await repo.create({"skill_level": "beginner"})
        await repo.create({"skill_level": "expert"})

        count = await repo.count(filters={"skill_level": "beginner"})

        assert count == 2

    @pytest.mark.asyncio
    async def test_count_empty_table(self, test_session) -> None:
        """Should return 0 for empty table."""
        repo = BaseRepository(UserProfile, test_session)

        count = await repo.count()

        assert count == 0
