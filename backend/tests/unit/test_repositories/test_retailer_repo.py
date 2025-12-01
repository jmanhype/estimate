"""Tests for RetailerPriceRepository."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.retailer import RetailerPrice
from src.repositories.retailer import RetailerPriceRepository


class TestRetailerPriceRepository:
    """Tests for RetailerPriceRepository methods."""

    @pytest.fixture
    async def retailer_repo(self, test_db: AsyncSession) -> RetailerPriceRepository:
        """Create RetailerPriceRepository instance."""
        return RetailerPriceRepository(test_db)

    @pytest.fixture
    async def sample_prices(
        self, retailer_repo: RetailerPriceRepository
    ) -> list[RetailerPrice]:
        """Create sample retailer prices for testing."""
        now = datetime.now(timezone.utc)
        prices = []

        # Paint at different retailers with different prices
        prices.append(await retailer_repo.create({
            "material_name": "Interior Paint - White",
            "material_category": "paint",
            "retailer_name": "home_depot",
            "product_sku": "HD-PAINT-001",
            "unit_price": Decimal("35.99"),
            "unit_of_measure": "gallon",
            "availability_status": "in_stock",
            "last_updated": now,
        }))

        prices.append(await retailer_repo.create({
            "material_name": "Interior Paint - White",
            "material_category": "paint",
            "retailer_name": "lowes",
            "product_sku": "LOW-PAINT-001",
            "unit_price": Decimal("32.99"),
            "unit_of_measure": "gallon",
            "availability_status": "in_stock",
            "last_updated": now,
        }))

        prices.append(await retailer_repo.create({
            "material_name": "Interior Paint - White",
            "material_category": "paint",
            "retailer_name": "menards",
            "product_sku": "MEN-PAINT-001",
            "unit_price": Decimal("29.99"),
            "unit_of_measure": "gallon",
            "availability_status": "out_of_stock",
            "last_updated": now,
        }))

        # Different material (primer) at Home Depot
        prices.append(await retailer_repo.create({
            "material_name": "Primer - White",
            "material_category": "primer",
            "retailer_name": "home_depot",
            "product_sku": "HD-PRIMER-001",
            "unit_price": Decimal("25.99"),
            "unit_of_measure": "gallon",
            "availability_status": "in_stock",
            "last_updated": now,
        }))

        # Stale price (old update)
        prices.append(await retailer_repo.create({
            "material_name": "Flooring - Oak",
            "material_category": "flooring",
            "retailer_name": "lowes",
            "product_sku": "LOW-FLOOR-001",
            "unit_price": Decimal("4.99"),
            "unit_of_measure": "square_feet",
            "availability_status": "in_stock",
            "last_updated": now - timedelta(days=10),
        }))

        return prices

    async def test_get_by_material(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting prices by material name."""
        prices = await retailer_repo.get_by_material("Interior Paint - White")
        assert len(prices) == 3
        assert all(p.material_name == "Interior Paint - White" for p in prices)

    async def test_get_by_material_with_pagination(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting prices by material with pagination."""
        prices = await retailer_repo.get_by_material(
            "Interior Paint - White", skip=1, limit=2
        )
        assert len(prices) == 2

    async def test_get_by_retailer(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting prices by retailer name."""
        prices = await retailer_repo.get_by_retailer("home_depot")
        assert len(prices) == 2
        assert all(p.retailer_name == "home_depot" for p in prices)

    async def test_get_by_retailer_with_pagination(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting prices by retailer with pagination."""
        prices = await retailer_repo.get_by_retailer("home_depot", skip=1, limit=1)
        assert len(prices) == 1

    async def test_get_by_category(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting prices by category."""
        prices = await retailer_repo.get_by_category("paint")
        assert len(prices) == 3
        assert all(p.material_category == "paint" for p in prices)

    async def test_get_by_category_with_pagination(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting prices by category with pagination."""
        prices = await retailer_repo.get_by_category("paint", skip=1, limit=2)
        assert len(prices) == 2

    async def test_search_by_material_and_retailer(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test searching prices by material and retailer."""
        prices = await retailer_repo.search_by_material_and_retailer(
            "Interior Paint - White", "home_depot"
        )
        assert len(prices) == 1
        assert prices[0].material_name == "Interior Paint - White"
        assert prices[0].retailer_name == "home_depot"

    async def test_get_cheapest_for_material(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting cheapest price for a material."""
        # With availability_only=True (default), should get Lowes ($32.99)
        # Menards is cheaper ($29.99) but out of stock
        cheapest = await retailer_repo.get_cheapest_for_material(
            "Interior Paint - White"
        )
        assert cheapest is not None
        assert cheapest.retailer_name == "lowes"
        assert cheapest.unit_price == Decimal("32.99")

    async def test_get_cheapest_for_material_all_stock(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting cheapest price including out of stock."""
        # With availability_only=False, should get Menards ($29.99)
        cheapest = await retailer_repo.get_cheapest_for_material(
            "Interior Paint - White", availability_only=False
        )
        assert cheapest is not None
        assert cheapest.retailer_name == "menards"
        assert cheapest.unit_price == Decimal("29.99")

    async def test_get_cheapest_for_material_not_found(
        self, retailer_repo: RetailerPriceRepository
    ) -> None:
        """Test getting cheapest price for non-existent material."""
        cheapest = await retailer_repo.get_cheapest_for_material("Nonexistent Material")
        assert cheapest is None

    async def test_get_average_price_by_material(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting average price for a material."""
        # With availability_only=True, should average Home Depot ($35.99) and Lowes ($32.99)
        # = 34.49
        avg_price = await retailer_repo.get_average_price_by_material(
            "Interior Paint - White"
        )
        assert avg_price is not None
        assert abs(avg_price - 34.49) < 0.01

    async def test_get_average_price_by_material_all_stock(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting average price including out of stock."""
        # With availability_only=False, should average all three:
        # (35.99 + 32.99 + 29.99) / 3 = 32.99
        avg_price = await retailer_repo.get_average_price_by_material(
            "Interior Paint - White", availability_only=False
        )
        assert avg_price is not None
        assert abs(avg_price - 32.99) < 0.01

    async def test_get_average_price_by_material_not_found(
        self, retailer_repo: RetailerPriceRepository
    ) -> None:
        """Test getting average price for non-existent material."""
        avg_price = await retailer_repo.get_average_price_by_material(
            "Nonexistent Material"
        )
        assert avg_price is None

    async def test_get_stale_prices(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting stale prices."""
        # With default 7 days, should find the flooring price (10 days old)
        stale_prices = await retailer_repo.get_stale_prices()
        assert len(stale_prices) == 1
        assert stale_prices[0].material_name == "Flooring - Oak"

    async def test_get_stale_prices_custom_days(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test getting stale prices with custom days threshold."""
        # With 15 days, should find no stale prices
        stale_prices = await retailer_repo.get_stale_prices(days_old=15)
        assert len(stale_prices) == 0

    async def test_compare_retailers(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test comparing prices across retailers."""
        # With availability_only=True, should get Home Depot and Lowes, sorted by price
        comparison = await retailer_repo.compare_retailers("Interior Paint - White")
        assert len(comparison) == 2
        # Should be sorted by price (cheapest first)
        assert comparison[0].retailer_name == "lowes"
        assert comparison[0].unit_price == Decimal("32.99")
        assert comparison[1].retailer_name == "home_depot"
        assert comparison[1].unit_price == Decimal("35.99")

    async def test_compare_retailers_all_stock(
        self,
        retailer_repo: RetailerPriceRepository,
        sample_prices: list[RetailerPrice],
    ) -> None:
        """Test comparing prices including out of stock."""
        # With availability_only=False, should get all three, sorted by price
        comparison = await retailer_repo.compare_retailers(
            "Interior Paint - White", availability_only=False
        )
        assert len(comparison) == 3
        # Should be sorted by price (cheapest first)
        assert comparison[0].retailer_name == "menards"
        assert comparison[0].unit_price == Decimal("29.99")
        assert comparison[1].retailer_name == "lowes"
        assert comparison[1].unit_price == Decimal("32.99")
        assert comparison[2].retailer_name == "home_depot"
        assert comparison[2].unit_price == Decimal("35.99")

    async def test_compare_retailers_not_found(
        self, retailer_repo: RetailerPriceRepository
    ) -> None:
        """Test comparing retailers for non-existent material."""
        comparison = await retailer_repo.compare_retailers("Nonexistent Material")
        assert comparison == []
