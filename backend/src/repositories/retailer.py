"""Retailer pricing repository."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.models.retailer import RetailerPrice
from src.repositories.base import BaseRepository


class RetailerPriceRepository(BaseRepository[RetailerPrice]):
    """Repository for RetailerPrice operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        super().__init__(RetailerPrice, db)

    async def get_by_material(
        self,
        material_name: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RetailerPrice]:
        """
        Get prices by material name.

        Args:
            material_name: Material name to search
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of retailer prices
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"material_name": material_name},
        )

    async def get_by_retailer(
        self,
        retailer_name: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RetailerPrice]:
        """
        Get prices by retailer name.

        Args:
            retailer_name: Retailer name
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of retailer prices
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"retailer_name": retailer_name},
        )

    async def get_by_category(
        self,
        material_category: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RetailerPrice]:
        """
        Get prices by category.

        Args:
            material_category: Material category
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of retailer prices
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"material_category": material_category},
        )

    async def search_by_material_and_retailer(
        self,
        material_name: str,
        retailer_name: str,
    ) -> list[RetailerPrice]:
        """
        Search prices by material and retailer.

        Args:
            material_name: Material name
            retailer_name: Retailer name

        Returns:
            List of matching retailer prices
        """
        return await self.get_multi(
            filters={
                "material_name": material_name,
                "retailer_name": retailer_name,
            }
        )

    async def get_cheapest_for_material(
        self,
        material_name: str,
        availability_only: bool = True,
    ) -> RetailerPrice | None:
        """
        Get cheapest price for a material across all retailers.

        Args:
            material_name: Material name
            availability_only: Only include in-stock items

        Returns:
            Cheapest retailer price or None
        """
        query = select(RetailerPrice).where(
            RetailerPrice.material_name == material_name
        )

        if availability_only:
            query = query.where(RetailerPrice.availability_status == "in_stock")

        query = query.order_by(RetailerPrice.unit_price.asc()).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_average_price_by_material(
        self,
        material_name: str,
        availability_only: bool = True,
    ) -> float | None:
        """
        Get average price for a material across retailers.

        Args:
            material_name: Material name
            availability_only: Only include in-stock items

        Returns:
            Average unit price or None
        """
        query = select(func.avg(RetailerPrice.unit_price)).where(
            RetailerPrice.material_name == material_name
        )

        if availability_only:
            query = query.where(RetailerPrice.availability_status == "in_stock")

        result = await self.db.execute(query)
        avg_price = result.scalar_one_or_none()
        return float(avg_price) if avg_price is not None else None

    async def get_stale_prices(self, days_old: int = 7) -> list[RetailerPrice]:
        """
        Get prices that haven't been updated recently.

        Args:
            days_old: Number of days to consider stale

        Returns:
            List of stale retailer prices
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        query = select(RetailerPrice).where(
            RetailerPrice.last_updated < cutoff_date
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def compare_retailers(
        self,
        material_name: str,
        availability_only: bool = True,
    ) -> list[RetailerPrice]:
        """
        Compare prices across retailers for a material.

        Args:
            material_name: Material name
            availability_only: Only include in-stock items

        Returns:
            List of prices sorted by unit price (cheapest first)
        """
        query = (
            select(RetailerPrice)
            .where(RetailerPrice.material_name == material_name)
            .order_by(RetailerPrice.unit_price.asc())
        )

        if availability_only:
            query = query.where(RetailerPrice.availability_status == "in_stock")

        result = await self.db.execute(query)
        return list(result.scalars().all())
