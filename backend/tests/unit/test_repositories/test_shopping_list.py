"""Tests for ShoppingListRepository."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project
from src.models.shopping_list import ShoppingList, ShoppingListItem
from src.models.user import UserProfile
from src.repositories.project import ProjectRepository
from src.repositories.shopping_list import (
    ShoppingListItemRepository,
    ShoppingListRepository,
)
from src.repositories.user import UserRepository


class TestShoppingListRepository:
    """Tests for ShoppingListRepository CRUD operations."""

    @pytest.fixture
    async def user_repo(self, test_db: AsyncSession) -> UserRepository:
        """Create UserRepository instance."""
        return UserRepository(test_db)

    @pytest.fixture
    async def project_repo(self, test_db: AsyncSession) -> ProjectRepository:
        """Create ProjectRepository instance."""
        return ProjectRepository(test_db)

    @pytest.fixture
    async def shopping_list_repo(
        self, test_db: AsyncSession
    ) -> ShoppingListRepository:
        """Create ShoppingListRepository instance."""
        return ShoppingListRepository(test_db)

    @pytest.fixture
    async def shopping_list_item_repo(
        self, test_db: AsyncSession
    ) -> ShoppingListItemRepository:
        """Create ShoppingListItemRepository instance."""
        return ShoppingListItemRepository(test_db)

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
            "name": "Test Project",
            "project_type": "painting",
            "status": "draft",
        })

    @pytest.fixture
    async def sample_shopping_list(
        self, shopping_list_repo: ShoppingListRepository, sample_project: Project
    ) -> ShoppingList:
        """Create a sample shopping list for testing."""
        return await shopping_list_repo.create({
            "project_id": sample_project.id,
            "total_estimated_cost": Decimal("0.00"),
        })

    @pytest.fixture
    async def sample_item(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> ShoppingListItem:
        """Create a sample shopping list item for testing."""
        return await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("2.5"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("3.0"),
            "unit_of_measure": "gallons",
            "estimated_unit_price": Decimal("45.00"),
            "estimated_total_cost": Decimal("135.00"),
        })

    async def test_get_by_project(
        self,
        shopping_list_repo: ShoppingListRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test getting shopping list by project ID."""
        shopping_list = await shopping_list_repo.get_by_project(
            sample_shopping_list.project_id
        )
        assert shopping_list is not None
        assert shopping_list.project_id == sample_shopping_list.project_id

    async def test_get_with_items(
        self,
        shopping_list_repo: ShoppingListRepository,
        sample_shopping_list: ShoppingList,
        sample_item: ShoppingListItem,
    ) -> None:
        """Test getting shopping list with eagerly loaded items."""
        shopping_list = await shopping_list_repo.get_with_items(
            sample_shopping_list.id
        )
        assert shopping_list is not None
        assert len(shopping_list.items) == 1
        assert shopping_list.items[0].id == sample_item.id

    async def test_recalculate_total(
        self,
        shopping_list_repo: ShoppingListRepository,
        sample_shopping_list: ShoppingList,
        sample_item: ShoppingListItem,
    ) -> None:
        """Test recalculating total estimated cost."""
        shopping_list = await shopping_list_repo.recalculate_total(
            sample_shopping_list.id
        )
        assert shopping_list is not None
        assert shopping_list.total_estimated_cost == Decimal("135.00")

    async def test_recalculate_total_nonexistent(
        self, shopping_list_repo: ShoppingListRepository
    ) -> None:
        """Test recalculating total for nonexistent shopping list."""
        from uuid import uuid4
        result = await shopping_list_repo.recalculate_total(uuid4())
        assert result is None

    async def test_get_by_project_no_results(
        self, shopping_list_repo: ShoppingListRepository
    ) -> None:
        """Test getting shopping list by project with no results."""
        from uuid import uuid4
        result = await shopping_list_repo.get_by_project(uuid4())
        assert result is None


class TestShoppingListItemRepository:
    """Tests for ShoppingListItemRepository CRUD operations."""

    @pytest.fixture
    async def user_repo(self, test_db: AsyncSession) -> UserRepository:
        """Create UserRepository instance."""
        return UserRepository(test_db)

    @pytest.fixture
    async def project_repo(self, test_db: AsyncSession) -> ProjectRepository:
        """Create ProjectRepository instance."""
        return ProjectRepository(test_db)

    @pytest.fixture
    async def shopping_list_repo(
        self, test_db: AsyncSession
    ) -> ShoppingListRepository:
        """Create ShoppingListRepository instance."""
        return ShoppingListRepository(test_db)

    @pytest.fixture
    async def shopping_list_item_repo(
        self, test_db: AsyncSession
    ) -> ShoppingListItemRepository:
        """Create ShoppingListItemRepository instance."""
        return ShoppingListItemRepository(test_db)

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
            "name": "Test Project",
            "project_type": "painting",
            "status": "draft",
        })

    @pytest.fixture
    async def sample_shopping_list(
        self, shopping_list_repo: ShoppingListRepository, sample_project: Project
    ) -> ShoppingList:
        """Create a sample shopping list for testing."""
        return await shopping_list_repo.create({
            "project_id": sample_project.id,
            "total_estimated_cost": Decimal("0.00"),
        })

    @pytest.fixture
    async def sample_item(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> ShoppingListItem:
        """Create a sample shopping list item for testing."""
        return await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("2.5"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("3.0"),
            "unit_of_measure": "gallons",
            "estimated_unit_price": Decimal("45.00"),
            "estimated_total_cost": Decimal("135.00"),
        })

    async def test_get_by_shopping_list(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
        sample_item: ShoppingListItem,
    ) -> None:
        """Test getting items by shopping list ID."""
        items = await shopping_list_item_repo.get_by_shopping_list(
            sample_shopping_list.id
        )
        assert len(items) == 1
        assert items[0].id == sample_item.id

    async def test_get_by_category(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
        sample_item: ShoppingListItem,
    ) -> None:
        """Test getting items by category."""
        items = await shopping_list_item_repo.get_by_category(
            sample_shopping_list.id, "paint"
        )
        assert len(items) == 1
        assert items[0].material_category == "paint"

    async def test_get_by_purchase_status(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
        sample_item: ShoppingListItem,
    ) -> None:
        """Test getting items by purchase status."""
        items = await shopping_list_item_repo.get_by_purchase_status(
            sample_shopping_list.id, "not_purchased"
        )
        assert len(items) == 1
        assert items[0].purchase_status == "not_purchased"

    async def test_mark_purchased(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_item: ShoppingListItem,
    ) -> None:
        """Test marking item as purchased."""
        updated = await shopping_list_item_repo.mark_purchased(
            sample_item.id,
            actual_unit_price=Decimal("48.00"),
            actual_quantity=Decimal("3.0"),
        )
        assert updated is not None
        assert updated.purchase_status == "purchased"
        assert updated.actual_unit_price == Decimal("48.00")
        assert updated.actual_total_cost == Decimal("144.00")

    async def test_mark_purchased_default_quantity(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_item: ShoppingListItem,
    ) -> None:
        """Test marking item as purchased with default quantity."""
        updated = await shopping_list_item_repo.mark_purchased(
            sample_item.id, actual_unit_price=Decimal("50.00")
        )
        assert updated is not None
        assert updated.purchase_status == "purchased"
        assert updated.actual_total_cost == Decimal("150.00")

    async def test_mark_purchased_nonexistent(
        self, shopping_list_item_repo: ShoppingListItemRepository
    ) -> None:
        """Test marking nonexistent item as purchased."""
        from uuid import uuid4
        result = await shopping_list_item_repo.mark_purchased(
            uuid4(), actual_unit_price=Decimal("50.00")
        )
        assert result is None

    async def test_get_by_shopping_list_no_results(
        self, shopping_list_item_repo: ShoppingListItemRepository
    ) -> None:
        """Test getting items with no results."""
        from uuid import uuid4
        items = await shopping_list_item_repo.get_by_shopping_list(uuid4())
        assert items == []
