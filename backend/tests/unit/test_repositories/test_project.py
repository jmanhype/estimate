"""Tests for ProjectRepository."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project
from src.models.user import UserProfile
from src.repositories.project import ProjectRepository
from src.repositories.user import UserRepository


class TestProjectRepository:
    """Tests for ProjectRepository CRUD operations."""

    @pytest.fixture
    async def user_repo(self, test_db: AsyncSession) -> UserRepository:
        """Create UserRepository instance."""
        return UserRepository(test_db)

    @pytest.fixture
    async def project_repo(self, test_db: AsyncSession) -> ProjectRepository:
        """Create ProjectRepository instance."""
        return ProjectRepository(test_db)

    @pytest.fixture
    async def sample_user(self, user_repo: UserRepository) -> UserProfile:
        """Create a sample user for testing."""
        return await user_repo.create({"skill_level": "intermediate"})

    @pytest.fixture
    async def sample_project(
        self, project_repo: ProjectRepository, sample_user: UserProfile
    ) -> Project:
        """Create a sample project for testing."""
        return await project_repo.create({
            "user_id": sample_user.id,
            "name": "Kitchen Renovation",
            "project_type": "kitchen",
            "status": "draft",
        })

    async def test_create_project(
        self, project_repo: ProjectRepository, sample_user: UserProfile
    ) -> None:
        """Test creating a project."""
        project = await project_repo.create({
            "user_id": sample_user.id,
            "name": "Bathroom Remodel",
            "project_type": "bathroom",
            "status": "draft",
        })
        assert project.name == "Bathroom Remodel"
        assert project.project_type == "bathroom"
        assert project.status == "draft"

    async def test_get_by_user(
        self, project_repo: ProjectRepository, sample_project: Project
    ) -> None:
        """Test getting projects by user ID."""
        projects = await project_repo.get_by_user(sample_project.user_id)
        assert len(projects) > 0
        assert all(p.user_id == sample_project.user_id for p in projects)

    async def test_get_by_status(
        self, project_repo: ProjectRepository, sample_project: Project
    ) -> None:
        """Test getting projects by status."""
        projects = await project_repo.get_by_status("draft")
        assert len(projects) > 0
        assert all(p.status == "draft" for p in projects)

    async def test_get_with_photos(
        self, project_repo: ProjectRepository, sample_project: Project
    ) -> None:
        """Test getting project with eagerly loaded photos."""
        project = await project_repo.get_with_photos(sample_project.id)
        assert project is not None
        assert project.id == sample_project.id
        # Photos relationship should be loaded (empty list for new project)
        assert project.photos == []

    async def test_get_with_shopping_list(
        self, project_repo: ProjectRepository, sample_project: Project
    ) -> None:
        """Test getting project with eagerly loaded shopping list."""
        project = await project_repo.get_with_shopping_list(sample_project.id)
        assert project is not None
        assert project.id == sample_project.id
        # Shopping list relationship should be loaded (None for new project)
        assert project.shopping_list is None

    async def test_update_costs(
        self, project_repo: ProjectRepository, sample_project: Project
    ) -> None:
        """Test updating project costs."""
        updated = await project_repo.update_costs(
            sample_project.id,
            estimated=Decimal("5000.00"),
            actual=Decimal("5200.00"),
        )
        assert updated is not None
        assert updated.total_estimated_cost == Decimal("5000.00")
        assert updated.total_actual_cost == Decimal("5200.00")

    async def test_update_costs_nonexistent_project(
        self, project_repo: ProjectRepository
    ) -> None:
        """Test updating costs for nonexistent project."""
        from uuid import uuid4
        result = await project_repo.update_costs(
            uuid4(),
            estimated=Decimal("1000.00"),
        )
        assert result is None

    async def test_get_by_user_no_results(
        self, project_repo: ProjectRepository
    ) -> None:
        """Test getting projects by user with no results."""
        from uuid import uuid4
        projects = await project_repo.get_by_user(uuid4())
        assert projects == []

    async def test_get_by_status_no_results(
        self, project_repo: ProjectRepository
    ) -> None:
        """Test getting projects by status with no results."""
        projects = await project_repo.get_by_status("completed")
        assert projects == []
