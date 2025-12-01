"""Tests for model __repr__ methods."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photo import ProjectPhoto
from src.models.project import Project
from src.models.retailer import PricingSnapshot, Retailer
from src.models.shopping_list import ShoppingList, ShoppingListItem
from src.models.subscription import Subscription
from src.models.user import UserProfile
from src.repositories.project import ProjectRepository
from src.repositories.retailer import PricingSnapshotRepository, RetailerRepository
from src.repositories.shopping_list import (
    ShoppingListItemRepository,
    ShoppingListRepository,
)
from src.repositories.user import UserRepository


class TestModelRepresentations:
    """Tests for all model __repr__ methods."""

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
    async def retailer_repo(self, test_db: AsyncSession) -> RetailerRepository:
        """Create RetailerRepository instance."""
        return RetailerRepository(test_db)

    @pytest.fixture
    async def pricing_repo(
        self, test_db: AsyncSession
    ) -> PricingSnapshotRepository:
        """Create PricingSnapshotRepository instance."""
        return PricingSnapshotRepository(test_db)

    async def test_user_profile_repr(
        self, user_repo: UserRepository
    ) -> None:
        """Test UserProfile __repr__ method."""
        user = await user_repo.create({"skill_level": "intermediate"})
        repr_str = repr(user)
        assert "UserProfile" in repr_str
        assert str(user.id) in repr_str
        assert "intermediate" in repr_str

    async def test_project_repr(
        self, user_repo: UserRepository, project_repo: ProjectRepository
    ) -> None:
        """Test Project __repr__ method."""
        user = await user_repo.create({"skill_level": "beginner"})
        project = await project_repo.create({
            "user_id": user.id,
            "name": "Kitchen Reno",
            "project_type": "kitchen",
            "status": "draft",
        })
        repr_str = repr(project)
        assert "Project" in repr_str
        assert str(project.id) in repr_str
        assert "Kitchen Reno" in repr_str
        assert "draft" in repr_str

    async def test_shopping_list_repr(
        self,
        user_repo: UserRepository,
        project_repo: ProjectRepository,
        shopping_list_repo: ShoppingListRepository,
    ) -> None:
        """Test ShoppingList __repr__ method."""
        user = await user_repo.create({"skill_level": "beginner"})
        project = await project_repo.create({
            "user_id": user.id,
            "name": "Test",
            "project_type": "painting",
            "status": "draft",
        })
        shopping_list = await shopping_list_repo.create({
            "project_id": project.id,
            "total_estimated_cost": Decimal("1234.56"),
        })
        repr_str = repr(shopping_list)
        assert "ShoppingList" in repr_str
        assert str(shopping_list.id) in repr_str
        assert "1234.56" in repr_str

    async def test_shopping_list_item_repr(
        self,
        user_repo: UserRepository,
        project_repo: ProjectRepository,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
    ) -> None:
        """Test ShoppingListItem __repr__ method."""
        user = await user_repo.create({"skill_level": "beginner"})
        project = await project_repo.create({
            "user_id": user.id,
            "name": "Test",
            "project_type": "painting",
            "status": "draft",
        })
        shopping_list = await shopping_list_repo.create({
            "project_id": project.id,
            "total_estimated_cost": Decimal("0.00"),
        })
        item = await shopping_list_item_repo.create({
            "shopping_list_id": shopping_list.id,
            "material_name": "Premium Paint",
            "material_category": "paint",
            "calculated_quantity": Decimal("2.5"),
            "waste_factor_percent": Decimal("10.00"),
            "actual_purchase_quantity": Decimal("3.0"),
            "unit_of_measure": "gallons",
        })
        repr_str = repr(item)
        assert "ShoppingListItem" in repr_str
        assert str(item.id) in repr_str
        assert "Premium Paint" in repr_str

    async def test_project_photo_repr(
        self,
        user_repo: UserRepository,
        project_repo: ProjectRepository,
        test_db: AsyncSession,
    ) -> None:
        """Test ProjectPhoto __repr__ method."""
        user = await user_repo.create({"skill_level": "beginner"})
        project = await project_repo.create({
            "user_id": user.id,
            "name": "Test",
            "project_type": "painting",
            "status": "draft",
        })

        # Create photo directly using session
        from datetime import datetime, timezone
        photo = ProjectPhoto(
            project_id=project.id,
            storage_path="/path/to/photo.jpg",
            file_size_bytes=12345,
            mime_type="image/jpeg",
            uploaded_at=datetime.now(timezone.utc),
        )
        test_db.add(photo)
        await test_db.commit()
        await test_db.refresh(photo)

        repr_str = repr(photo)
        assert "ProjectPhoto" in repr_str
        assert str(photo.id) in repr_str
        assert "pending" in repr_str

    async def test_subscription_repr(
        self, user_repo: UserRepository, test_db: AsyncSession
    ) -> None:
        """Test Subscription __repr__ method."""
        user = await user_repo.create({"skill_level": "beginner"})

        # Create subscription directly using session
        subscription = Subscription(
            user_id=user.id,
            stripe_customer_id="cus_test123",
            tier="pro",
            status="active",
        )
        test_db.add(subscription)
        await test_db.commit()
        await test_db.refresh(subscription)

        repr_str = repr(subscription)
        assert "Subscription" in repr_str
        assert str(subscription.id) in repr_str
        assert "pro" in repr_str
        assert "active" in repr_str

    async def test_retailer_repr(
        self, retailer_repo: RetailerRepository
    ) -> None:
        """Test Retailer __repr__ method."""
        retailer = await retailer_repo.create({
            "name": "Home Depot",
            "api_type": "home_depot",
            "is_active": True,
        })
        repr_str = repr(retailer)
        assert "Retailer" in repr_str
        assert str(retailer.id) in repr_str
        assert "Home Depot" in repr_str

    async def test_pricing_snapshot_repr(
        self, retailer_repo: RetailerRepository, pricing_repo: PricingSnapshotRepository
    ) -> None:
        """Test PricingSnapshot __repr__ method."""
        retailer = await retailer_repo.create({
            "name": "Home Depot",
            "api_type": "home_depot",
            "is_active": True,
        })
        snapshot = await pricing_repo.create({
            "retailer_id": retailer.id,
            "material_name": "Paint",
            "material_category": "paint",
            "sku": "SKU123",
            "unit_price": Decimal("45.99"),
            "unit_of_measure": "gallons",
            "availability": "in_stock",
        })
        repr_str = repr(snapshot)
        assert "PricingSnapshot" in repr_str
        assert str(snapshot.id) in repr_str
        assert "Paint" in repr_str
        assert "SKU123" in repr_str
