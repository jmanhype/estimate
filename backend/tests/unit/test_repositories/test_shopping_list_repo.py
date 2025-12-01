"""Tests for ShoppingListRepository and ShoppingListItemRepository."""

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
    """Tests for ShoppingListRepository methods."""

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
            "name": "Kitchen Renovation",
            "project_type": "kitchen",
            "status": "draft",
        })

    @pytest.fixture
    async def sample_shopping_list(
        self,
        shopping_list_repo: ShoppingListRepository,
        sample_project: Project,
    ) -> ShoppingList:
        """Create a sample shopping list for testing."""
        return await shopping_list_repo.create({
            "project_id": sample_project.id,
            "total_estimated_cost": Decimal("500.00"),
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
        assert shopping_list.id == sample_shopping_list.id
        assert shopping_list.project_id == sample_shopping_list.project_id

    async def test_get_by_project_not_found(
        self, shopping_list_repo: ShoppingListRepository
    ) -> None:
        """Test getting shopping list by project ID with no results."""
        from uuid import uuid4
        shopping_list = await shopping_list_repo.get_by_project(uuid4())
        assert shopping_list is None

    async def test_get_with_items(
        self,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test getting shopping list with eagerly loaded items."""
        # Create some items
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("10.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("11.000"),
            "unit_of_measure": "gallons",
            "estimated_unit_price": Decimal("35.00"),
            "estimated_total_cost": Decimal("385.00"),
        })
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Primer",
            "material_category": "primer",
            "calculated_quantity": Decimal("5.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("5.500"),
            "unit_of_measure": "gallons",
            "estimated_unit_price": Decimal("25.00"),
            "estimated_total_cost": Decimal("137.50"),
        })

        shopping_list = await shopping_list_repo.get_with_items(
            sample_shopping_list.id
        )
        assert shopping_list is not None
        assert shopping_list.id == sample_shopping_list.id
        # Items relationship should be loaded
        assert len(shopping_list.items) == 2
        assert shopping_list.items[0].material_name in ["Paint", "Primer"]

    async def test_get_with_items_empty(
        self,
        shopping_list_repo: ShoppingListRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test getting shopping list with no items."""
        shopping_list = await shopping_list_repo.get_with_items(
            sample_shopping_list.id
        )
        assert shopping_list is not None
        assert len(shopping_list.items) == 0

    async def test_recalculate_total(
        self,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test recalculating total estimated cost from items."""
        # Create items with known costs
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("10.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("11.000"),
            "unit_of_measure": "gallons",
            "estimated_unit_price": Decimal("35.00"),
            "estimated_total_cost": Decimal("385.00"),
        })
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Primer",
            "material_category": "primer",
            "calculated_quantity": Decimal("5.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("5.500"),
            "unit_of_measure": "gallons",
            "estimated_unit_price": Decimal("25.00"),
            "estimated_total_cost": Decimal("137.50"),
        })

        # Recalculate total
        shopping_list = await shopping_list_repo.recalculate_total(
            sample_shopping_list.id
        )
        assert shopping_list is not None
        # Total should be sum of item costs: 385.00 + 137.50 = 522.50
        assert shopping_list.total_estimated_cost == Decimal("522.50")

    async def test_recalculate_total_with_none_costs(
        self,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test recalculating total when some items have no cost."""
        # Create item with None cost
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Unknown Material",
            "material_category": "other",
            "calculated_quantity": Decimal("1.000"),
            "waste_factor_percent": Decimal("0.00"),
            "actual_purchase_quantity": Decimal("1.000"),
            "unit_of_measure": "each",
            "estimated_unit_price": None,
            "estimated_total_cost": None,
        })

        # Recalculate total
        shopping_list = await shopping_list_repo.recalculate_total(
            sample_shopping_list.id
        )
        assert shopping_list is not None
        # Total should be 0.00 since item has None cost
        assert shopping_list.total_estimated_cost == Decimal("0.00")

    async def test_recalculate_total_not_found(
        self, shopping_list_repo: ShoppingListRepository
    ) -> None:
        """Test recalculating total for non-existent shopping list."""
        from uuid import uuid4
        result = await shopping_list_repo.recalculate_total(uuid4())
        assert result is None


class TestShoppingListItemRepository:
    """Tests for ShoppingListItemRepository methods."""

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
            "name": "Kitchen Renovation",
            "project_type": "kitchen",
            "status": "draft",
        })

    @pytest.fixture
    async def sample_shopping_list(
        self,
        shopping_list_repo: ShoppingListRepository,
        sample_project: Project,
    ) -> ShoppingList:
        """Create a sample shopping list for testing."""
        return await shopping_list_repo.create({
            "project_id": sample_project.id,
            "total_estimated_cost": Decimal("500.00"),
        })

    async def test_get_by_shopping_list(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test getting items by shopping list ID."""
        # Create multiple items
        for i in range(3):
            await shopping_list_item_repo.create({
                "shopping_list_id": sample_shopping_list.id,
                "material_name": f"Material {i}",
                "material_category": "paint",
                "calculated_quantity": Decimal("1.000"),
                "waste_factor_percent": Decimal("10.00"),
                "actual_purchase_quantity": Decimal("1.100"),
                "unit_of_measure": "gallons",
            })

        items = await shopping_list_item_repo.get_by_shopping_list(
            sample_shopping_list.id
        )
        assert len(items) == 3
        assert all(item.shopping_list_id == sample_shopping_list.id for item in items)

    async def test_get_by_shopping_list_with_pagination(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test getting items by shopping list with pagination."""
        # Create multiple items
        for i in range(5):
            await shopping_list_item_repo.create({
                "shopping_list_id": sample_shopping_list.id,
                "material_name": f"Material {i}",
                "material_category": "paint",
                "calculated_quantity": Decimal("1.000"),
                "waste_factor_percent": Decimal("10.00"),
                "actual_purchase_quantity": Decimal("1.100"),
                "unit_of_measure": "gallons",
            })

        items = await shopping_list_item_repo.get_by_shopping_list(
            sample_shopping_list.id, skip=2, limit=2
        )
        assert len(items) == 2

    async def test_get_by_category(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test getting items by category."""
        # Create items with different categories
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("10.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("11.000"),
            "unit_of_measure": "gallons",
        })
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Primer",
            "material_category": "primer",
            "calculated_quantity": Decimal("5.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("5.500"),
            "unit_of_measure": "gallons",
        })
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "More Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("5.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("5.500"),
            "unit_of_measure": "gallons",
        })

        paint_items = await shopping_list_item_repo.get_by_category(
            sample_shopping_list.id, "paint"
        )
        assert len(paint_items) == 2
        assert all(item.material_category == "paint" for item in paint_items)

    async def test_get_by_purchase_status(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test getting items by purchase status."""
        # Create items with different statuses
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Purchased Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("10.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("11.000"),
            "unit_of_measure": "gallons",
            "purchase_status": "purchased",
        })
        await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Not Purchased Primer",
            "material_category": "primer",
            "calculated_quantity": Decimal("5.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("5.500"),
            "unit_of_measure": "gallons",
            "purchase_status": "not_purchased",
        })

        purchased_items = await shopping_list_item_repo.get_by_purchase_status(
            sample_shopping_list.id, "purchased"
        )
        assert len(purchased_items) == 1
        assert all(item.purchase_status == "purchased" for item in purchased_items)

    async def test_mark_purchased(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test marking item as purchased."""
        item = await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("10.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("11.000"),
            "unit_of_measure": "gallons",
        })

        updated_item = await shopping_list_item_repo.mark_purchased(
            item.id,
            actual_unit_price=Decimal("40.00"),
        )
        assert updated_item is not None
        assert updated_item.purchase_status == "purchased"
        assert updated_item.actual_unit_price == Decimal("40.00")
        # Should use actual_purchase_quantity since no quantity provided
        assert updated_item.actual_total_cost == Decimal("40.00") * Decimal("11.000")

    async def test_mark_purchased_with_quantity(
        self,
        shopping_list_item_repo: ShoppingListItemRepository,
        sample_shopping_list: ShoppingList,
    ) -> None:
        """Test marking item as purchased with custom quantity."""
        item = await shopping_list_item_repo.create({
            "shopping_list_id": sample_shopping_list.id,
            "material_name": "Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("10.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("11.000"),
            "unit_of_measure": "gallons",
        })

        updated_item = await shopping_list_item_repo.mark_purchased(
            item.id,
            actual_unit_price=Decimal("35.00"),
            actual_quantity=Decimal("12.000"),
        )
        assert updated_item is not None
        assert updated_item.purchase_status == "purchased"
        assert updated_item.actual_unit_price == Decimal("35.00")
        # Should use provided quantity
        assert updated_item.actual_total_cost == Decimal("35.00") * Decimal("12.000")

    async def test_mark_purchased_not_found(
        self, shopping_list_item_repo: ShoppingListItemRepository
    ) -> None:
        """Test marking non-existent item as purchased."""
        from uuid import uuid4
        result = await shopping_list_item_repo.mark_purchased(
            uuid4(),
            actual_unit_price=Decimal("40.00"),
        )
        assert result is None
