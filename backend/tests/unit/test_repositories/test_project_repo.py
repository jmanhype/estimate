"""Tests for ProjectRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project
from src.models.user import UserProfile
from src.repositories.project import ProjectRepository
from src.repositories.user import UserRepository


class TestProjectRepository:
    """Tests for ProjectRepository methods."""

    @pytest.fixture
    async def user_repo(self, test_session: AsyncSession) -> UserRepository:
        """Create UserRepository instance."""
        return UserRepository(test_session)

    @pytest.fixture
    async def project_repo(self, test_session: AsyncSession) -> ProjectRepository:
        """Create ProjectRepository instance."""
        return ProjectRepository(test_session)

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

    async def test_get_by_user(
        self, project_repo: ProjectRepository, sample_project: Project
    ) -> None:
        """Test getting projects by user ID."""
        projects = await project_repo.get_by_user(sample_project.user_id)
        assert len(projects) > 0
        assert all(p.user_id == sample_project.user_id for p in projects)

    async def test_get_by_user_with_pagination(
        self, project_repo: ProjectRepository, sample_user: UserProfile
    ) -> None:
        """Test getting projects by user with pagination."""
        # Create multiple projects
        for i in range(5):
            await project_repo.create({
                "user_id": sample_user.id,
                "name": f"Project {i}",
                "project_type": "painting",
                "status": "draft",
            })

        projects = await project_repo.get_by_user(sample_user.id, skip=2, limit=2)
        assert len(projects) == 2

    async def test_get_by_user_and_status(
        self, project_repo: ProjectRepository, sample_user: UserProfile
    ) -> None:
        """Test getting projects by user and status."""
        # Create projects with different statuses
        await project_repo.create({
            "user_id": sample_user.id,
            "name": "Draft Project",
            "project_type": "painting",
            "status": "draft",
        })
        await project_repo.create({
            "user_id": sample_user.id,
            "name": "In Progress Project",
            "project_type": "flooring",
            "status": "in_progress",
        })

        draft_projects = await project_repo.get_by_user_and_status(
            sample_user.id, "draft"
        )
        assert len(draft_projects) > 0
        assert all(p.status == "draft" for p in draft_projects)

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

    async def test_get_with_all_relations(
        self, project_repo: ProjectRepository, sample_project: Project
    ) -> None:
        """Test getting project with all eagerly loaded relations."""
        project = await project_repo.get_with_all_relations(sample_project.id)
        assert project is not None
        assert project.id == sample_project.id
        # All relationships should be loaded
        assert project.photos == []
        assert project.shopping_list is None

    async def test_count_by_user(
        self, project_repo: ProjectRepository, sample_user: UserProfile
    ) -> None:
        """Test counting projects by user."""
        # Create multiple projects
        for i in range(3):
            await project_repo.create({
                "user_id": sample_user.id,
                "name": f"Project {i}",
                "project_type": "painting",
                "status": "draft",
            })

        count = await project_repo.count_by_user(sample_user.id)
        assert count == 3

    async def test_count_by_status(
        self, project_repo: ProjectRepository, sample_user: UserProfile
    ) -> None:
        """Test counting projects by status."""
        # Create projects with different statuses
        await project_repo.create({
            "user_id": sample_user.id,
            "name": "Draft 1",
            "project_type": "painting",
            "status": "draft",
        })
        await project_repo.create({
            "user_id": sample_user.id,
            "name": "Draft 2",
            "project_type": "painting",
            "status": "draft",
        })
        await project_repo.create({
            "user_id": sample_user.id,
            "name": "In Progress",
            "project_type": "painting",
            "status": "in_progress",
        })

        draft_count = await project_repo.count_by_status("draft")
        assert draft_count == 2

    async def test_get_by_user_no_results(
        self, project_repo: ProjectRepository
    ) -> None:
        """Test getting projects by user with no results."""
        from uuid import uuid4
        projects = await project_repo.get_by_user(uuid4())
        assert projects == []

    async def test_count_by_user_zero(
        self, project_repo: ProjectRepository
    ) -> None:
        """Test counting projects by user with zero results."""
        from uuid import uuid4
        count = await project_repo.count_by_user(uuid4())
        assert count == 0
