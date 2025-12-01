"""Comprehensive tests for Project model."""

from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models.project import Project
from src.models.user import UserProfile


class TestProjectModel:
    """Test Project model structure and validation."""

    @pytest.mark.asyncio
    async def test_create_project_with_required_fields(
        self, test_session
    ) -> None:
        """Project should be created with required fields only."""
        # Create user first
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        project = Project(
            user_id=user.id,
            name="Kitchen Renovation",
            project_type="kitchen",
        )

        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        assert project.user_id == user.id
        assert project.name == "Kitchen Renovation"
        assert project.project_type == "kitchen"
        assert project.status == "draft"  # Default
        assert project.budget_amount is None
        assert project.total_estimated_cost is None
        assert project.total_actual_cost is None

    @pytest.mark.asyncio
    async def test_create_project_with_all_fields(
        self, test_session
    ) -> None:
        """Project should be created with all fields."""
        user = UserProfile(skill_level="expert")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        project = Project(
            user_id=user.id,
            name="Full Home Remodel",
            project_type="other",
            status="in_progress",
            budget_amount=Decimal("50000.00"),
            total_estimated_cost=Decimal("45000.00"),
            total_actual_cost=Decimal("47500.00"),
        )

        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        assert project.budget_amount == Decimal("50000.00")
        assert project.total_estimated_cost == Decimal("45000.00")
        assert project.total_actual_cost == Decimal("47500.00")
        assert project.status == "in_progress"

    @pytest.mark.asyncio
    async def test_project_valid_project_types(
        self, test_session
    ) -> None:
        """Project should accept all valid project types."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        valid_types = [
            "painting", "flooring", "tiling", "drywall",
            "concrete", "roofing", "decking", "fencing",
            "kitchen", "bathroom", "other"
        ]

        for project_type in valid_types:
            project = Project(
                user_id=user.id,
                name=f"Test {project_type}",
                project_type=project_type,
            )
            test_session.add(project)
            await test_session.commit()
            await test_session.refresh(project)

            assert project.project_type == project_type

            await test_session.delete(project)
            await test_session.commit()

    @pytest.mark.asyncio
    async def test_project_valid_statuses(
        self, test_session
    ) -> None:
        """Project should accept all valid statuses."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        valid_statuses = ["draft", "in_progress", "completed"]

        for status in valid_statuses:
            project = Project(
                user_id=user.id,
                name=f"Test {status}",
                project_type="painting",
                status=status,
            )
            test_session.add(project)
            await test_session.commit()
            await test_session.refresh(project)

            assert project.status == status

            await test_session.delete(project)
            await test_session.commit()

    @pytest.mark.asyncio
    async def test_project_foreign_key_constraint(
        self, test_session
    ) -> None:
        """Project should enforce foreign key constraint to user."""
        fake_user_id = uuid4()

        project = Project(
            user_id=fake_user_id,
            name="Invalid Project",
            project_type="painting",
        )

        test_session.add(project)

        with pytest.raises(IntegrityError):
            await test_session.commit()

    @pytest.mark.asyncio
    async def test_project_cascade_delete_with_user(
        self, test_session
    ) -> None:
        """Projects should be deleted when user is deleted (cascade)."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        project = Project(
            user_id=user.id,
            name="Test Project",
            project_type="painting",
        )
        test_session.add(project)
        await test_session.commit()
        project_id = project.id

        # Delete user (should cascade to projects)
        await test_session.delete(user)
        await test_session.commit()

        # Verify project was deleted
        result = await test_session.get(Project, project_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_project_repr(self, test_session) -> None:
        """Project __repr__ should return useful string representation."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        project = Project(
            user_id=user.id,
            name="Kitchen Remodel",
            project_type="kitchen",
        )
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        repr_str = repr(project)

        assert "Project" in repr_str
        assert "Kitchen Remodel" in repr_str


class TestProjectRelationships:
    """Test Project relationships with other models."""

    @pytest.mark.asyncio
    async def test_project_has_user_relationship(
        self, test_session
    ) -> None:
        """Project should have user relationship."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        project = Project(
            user_id=user.id,
            name="Test Project",
            project_type="painting",
        )
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        # Should have user relationship
        assert hasattr(project, "user")

    @pytest.mark.asyncio
    async def test_project_has_photos_relationship(
        self, test_session
    ) -> None:
        """Project should have photos relationship."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        project = Project(
            user_id=user.id,
            name="Test Project",
            project_type="painting",
        )
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        # Should have photos attribute (empty list initially)
        assert hasattr(project, "photos")
        assert isinstance(project.photos, list)
        assert len(project.photos) == 0

    @pytest.mark.asyncio
    async def test_project_has_shopping_list_relationship(
        self, test_session
    ) -> None:
        """Project should have shopping_list relationship."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        project = Project(
            user_id=user.id,
            name="Test Project",
            project_type="painting",
        )
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        # Should have shopping_list attribute (None initially)
        assert hasattr(project, "shopping_list")
        assert project.shopping_list is None


class TestProjectQueries:
    """Test Project database queries."""

    @pytest.mark.asyncio
    async def test_query_projects_by_user(self, test_session) -> None:
        """Should be able to query projects by user."""
        user1 = UserProfile(skill_level="beginner")
        user2 = UserProfile(skill_level="expert")
        test_session.add_all([user1, user2])
        await test_session.commit()
        await test_session.refresh(user1)
        await test_session.refresh(user2)

        # Create projects for both users
        projects = [
            Project(user_id=user1.id, name="Project 1", project_type="painting"),
            Project(user_id=user1.id, name="Project 2", project_type="flooring"),
            Project(user_id=user2.id, name="Project 3", project_type="tiling"),
        ]

        for project in projects:
            test_session.add(project)
        await test_session.commit()

        # Query user1's projects
        query = select(Project).where(Project.user_id == user1.id)
        result = await test_session.execute(query)
        user1_projects = list(result.scalars().all())

        assert len(user1_projects) == 2
        assert all(p.user_id == user1.id for p in user1_projects)

    @pytest.mark.asyncio
    async def test_query_projects_by_status(self, test_session) -> None:
        """Should be able to query projects by status."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        projects = [
            Project(user_id=user.id, name="P1", project_type="painting", status="draft"),
            Project(user_id=user.id, name="P2", project_type="flooring", status="draft"),
            Project(user_id=user.id, name="P3", project_type="tiling", status="in_progress"),
        ]

        for project in projects:
            test_session.add(project)
        await test_session.commit()

        # Query draft projects
        query = select(Project).where(Project.status == "draft")
        result = await test_session.execute(query)
        draft_projects = list(result.scalars().all())

        assert len(draft_projects) == 2
        assert all(p.status == "draft" for p in draft_projects)

    @pytest.mark.asyncio
    async def test_query_projects_by_type(self, test_session) -> None:
        """Should be able to query projects by type."""
        user = UserProfile(skill_level="beginner")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        projects = [
            Project(user_id=user.id, name="P1", project_type="painting"),
            Project(user_id=user.id, name="P2", project_type="painting"),
            Project(user_id=user.id, name="P3", project_type="kitchen"),
        ]

        for project in projects:
            test_session.add(project)
        await test_session.commit()

        # Query painting projects
        query = select(Project).where(Project.project_type == "painting")
        result = await test_session.execute(query)
        painting_projects = list(result.scalars().all())

        assert len(painting_projects) == 2
        assert all(p.project_type == "painting" for p in painting_projects)
