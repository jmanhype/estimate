"""Tests for model __repr__ methods."""

from datetime import UTC
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.project import ProjectRepository
from src.repositories.retailer import RetailerPriceRepository
from src.repositories.shopping_list import (
    ShoppingListItemRepository,
    ShoppingListRepository,
)
from src.repositories.user import UserRepository


class TestModelRepr:
    """Tests for model __repr__ methods."""

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
    async def retailer_repo(self, test_db: AsyncSession) -> RetailerPriceRepository:
        """Create RetailerPriceRepository instance."""
        return RetailerPriceRepository(test_db)

    async def test_user_profile_repr(
        self, user_repo: UserRepository
    ) -> None:
        """Test UserProfile __repr__ method."""
        user = await user_repo.create({
            "skill_level": "intermediate",
            "company_name": "Test Company",
        })
        repr_str = repr(user)
        assert repr_str.startswith("<UserProfile(id=")
        assert str(user.id) in repr_str
        assert "skill_level=intermediate" in repr_str

    async def test_project_repr(
        self, user_repo: UserRepository, project_repo: ProjectRepository
    ) -> None:
        """Test Project __repr__ method."""
        user = await user_repo.create({"skill_level": "intermediate"})
        project = await project_repo.create({
            "user_id": user.id,
            "name": "Kitchen Renovation",
            "project_type": "kitchen",
            "status": "draft",
        })
        repr_str = repr(project)
        assert repr_str.startswith("<Project(id=")
        assert str(project.id) in repr_str
        assert "name=Kitchen Renovation" in repr_str

    async def test_shopping_list_repr(
        self,
        user_repo: UserRepository,
        project_repo: ProjectRepository,
        shopping_list_repo: ShoppingListRepository,
    ) -> None:
        """Test ShoppingList __repr__ method."""
        user = await user_repo.create({"skill_level": "intermediate"})
        project = await project_repo.create({
            "user_id": user.id,
            "name": "Test Project",
            "project_type": "painting",
            "status": "draft",
        })
        shopping_list = await shopping_list_repo.create({
            "project_id": project.id,
            "total_estimated_cost": Decimal("500.00"),
        })
        repr_str = repr(shopping_list)
        assert repr_str.startswith("<ShoppingList(id=")
        assert str(shopping_list.id) in repr_str
        assert "total_cost=500.00" in repr_str

    async def test_shopping_list_item_repr(
        self,
        user_repo: UserRepository,
        project_repo: ProjectRepository,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
    ) -> None:
        """Test ShoppingListItem __repr__ method."""
        user = await user_repo.create({"skill_level": "intermediate"})
        project = await project_repo.create({
            "user_id": user.id,
            "name": "Test Project",
            "project_type": "painting",
            "status": "draft",
        })
        shopping_list = await shopping_list_repo.create({
            "project_id": project.id,
            "total_estimated_cost": Decimal("500.00"),
        })
        item = await shopping_list_item_repo.create({
            "shopping_list_id": shopping_list.id,
            "material_name": "Paint - White",
            "material_category": "paint",
            "calculated_quantity": Decimal("10.000"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("11.000"),
            "unit_of_measure": "gallons",
        })
        repr_str = repr(item)
        assert repr_str.startswith("<ShoppingListItem(id=")
        assert str(item.id) in repr_str
        assert "material=Paint - White" in repr_str

    async def test_retailer_price_repr(
        self, retailer_repo: RetailerPriceRepository
    ) -> None:
        """Test RetailerPrice __repr__ method."""
        from datetime import datetime

        price = await retailer_repo.create({
            "material_name": "Paint - White",
            "material_category": "paint",
            "retailer_name": "home_depot",
            "unit_price": Decimal("35.99"),
            "unit_of_measure": "gallon",
            "availability_status": "in_stock",
            "last_updated": datetime.now(UTC),
        })
        repr_str = repr(price)
        assert repr_str.startswith("<RetailerPrice(material=")
        assert "Paint - White" in repr_str
        assert "retailer=home_depot" in repr_str
        assert "price=35.99" in repr_str
