"""Tests for RetailerRepository."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.retailer import PricingSnapshot, Retailer
from src.repositories.retailer import PricingSnapshotRepository, RetailerRepository


class TestRetailerRepository:
    """Tests for RetailerRepository CRUD operations."""

    @pytest.fixture
    async def retailer_repo(self, test_db: AsyncSession) -> RetailerRepository:
        """Create RetailerRepository instance."""
        return RetailerRepository(test_db)

    @pytest.fixture
    async def sample_retailer(
        self, retailer_repo: RetailerRepository
    ) -> Retailer:
        """Create a sample retailer for testing."""
        return await retailer_repo.create({
            "name": "Home Depot",
            "api_type": "home_depot",
            "is_active": True,
        })

    async def test_get_active_retailers(
        self, retailer_repo: RetailerRepository, sample_retailer: Retailer
    ) -> None:
        """Test getting active retailers."""
        retailers = await retailer_repo.get_active()
        assert len(retailers) > 0
        assert all(r.is_active is True for r in retailers)

    async def test_get_by_api_type(
        self, retailer_repo: RetailerRepository, sample_retailer: Retailer
    ) -> None:
        """Test getting retailer by API type."""
        retailer = await retailer_repo.get_by_api_type("home_depot")
        assert retailer is not None
        assert retailer.api_type == "home_depot"

    async def test_get_by_api_type_no_results(
        self, retailer_repo: RetailerRepository
    ) -> None:
        """Test getting retailer by API type with no results."""
        retailer = await retailer_repo.get_by_api_type("lowes")
        assert retailer is None

    async def test_get_active_no_results(
        self, test_db: AsyncSession
    ) -> None:
        """Test getting active retailers with no results."""
        retailer_repo = RetailerRepository(test_db)
        retailers = await retailer_repo.get_active()
        assert retailers == []


class TestPricingSnapshotRepository:
    """Tests for PricingSnapshotRepository CRUD operations."""

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

    @pytest.fixture
    async def sample_retailer(
        self, retailer_repo: RetailerRepository
    ) -> Retailer:
        """Create a sample retailer for testing."""
        return await retailer_repo.create({
            "name": "Home Depot",
            "api_type": "home_depot",
            "is_active": True,
        })

    @pytest.fixture
    async def sample_snapshot(
        self, pricing_repo: PricingSnapshotRepository, sample_retailer: Retailer
    ) -> PricingSnapshot:
        """Create a sample pricing snapshot for testing."""
        return await pricing_repo.create({
            "retailer_id": sample_retailer.id,
            "material_name": "Interior Paint",
            "material_category": "paint",
            "sku": "PPG-INT-001",
            "unit_price": Decimal("45.99"),
            "unit_of_measure": "gallons",
            "availability": "in_stock",
            "product_url": "https://example.com/paint",
        })

    async def test_get_by_retailer_and_material(
        self,
        pricing_repo: PricingSnapshotRepository,
        sample_retailer: Retailer,
        sample_snapshot: PricingSnapshot,
    ) -> None:
        """Test getting pricing snapshots by retailer and material."""
        snapshots = await pricing_repo.get_by_retailer_and_material(
            sample_retailer.id, "Interior Paint"
        )
        assert len(snapshots) > 0
        assert all(s.material_name == "Interior Paint" for s in snapshots)

    async def test_get_latest_by_retailer_and_sku(
        self,
        pricing_repo: PricingSnapshotRepository,
        sample_retailer: Retailer,
        sample_snapshot: PricingSnapshot,
    ) -> None:
        """Test getting latest pricing snapshot by retailer and SKU."""
        snapshot = await pricing_repo.get_latest_by_retailer_and_sku(
            sample_retailer.id, "PPG-INT-001"
        )
        assert snapshot is not None
        assert snapshot.sku == "PPG-INT-001"

    async def test_get_by_category(
        self,
        pricing_repo: PricingSnapshotRepository,
        sample_snapshot: PricingSnapshot,
    ) -> None:
        """Test getting pricing snapshots by category."""
        snapshots = await pricing_repo.get_by_category("paint", limit=10)
        assert len(snapshots) > 0
        assert all(s.material_category == "paint" for s in snapshots)

    async def test_get_available_materials(
        self,
        pricing_repo: PricingSnapshotRepository,
        sample_retailer: Retailer,
        sample_snapshot: PricingSnapshot,
    ) -> None:
        """Test getting available materials by retailer."""
        snapshots = await pricing_repo.get_available_materials(sample_retailer.id)
        assert len(snapshots) > 0
        assert all(s.availability == "in_stock" for s in snapshots)

    async def test_search_materials(
        self,
        pricing_repo: PricingSnapshotRepository,
        sample_snapshot: PricingSnapshot,
    ) -> None:
        """Test searching materials by name."""
        snapshots = await pricing_repo.search_materials("Paint")
        assert len(snapshots) > 0
        assert any("Paint" in s.material_name for s in snapshots)

    async def test_get_price_comparison(
        self,
        pricing_repo: PricingSnapshotRepository,
        sample_snapshot: PricingSnapshot,
    ) -> None:
        """Test getting price comparison for a material."""
        snapshots = await pricing_repo.get_price_comparison("Interior Paint")
        assert len(snapshots) > 0
        assert all(s.material_name == "Interior Paint" for s in snapshots)

    async def test_get_by_retailer_and_material_no_results(
        self, pricing_repo: PricingSnapshotRepository
    ) -> None:
        """Test getting snapshots with no results."""
        from uuid import uuid4
        snapshots = await pricing_repo.get_by_retailer_and_material(
            uuid4(), "Nonexistent"
        )
        assert snapshots == []

    async def test_get_latest_by_retailer_and_sku_no_results(
        self, pricing_repo: PricingSnapshotRepository
    ) -> None:
        """Test getting latest snapshot with no results."""
        from uuid import uuid4
        snapshot = await pricing_repo.get_latest_by_retailer_and_sku(
            uuid4(), "FAKE-SKU"
        )
        assert snapshot is None

    async def test_search_materials_no_results(
        self, pricing_repo: PricingSnapshotRepository
    ) -> None:
        """Test searching materials with no results."""
        snapshots = await pricing_repo.search_materials("ZZZ_NONEXISTENT_ZZZ")
        assert snapshots == []
