"""Shopping list repository."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.shopping_list import ShoppingList, ShoppingListItem
from src.repositories.base import BaseRepository


class ShoppingListRepository(BaseRepository[ShoppingList]):
    """Repository for ShoppingList operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        super().__init__(ShoppingList, db)

    async def get_by_project(self, project_id: UUID) -> ShoppingList | None:
        """
        Get shopping list by project ID.

        Args:
            project_id: Project UUID

        Returns:
            Shopping list or None
        """
        query = select(ShoppingList).where(ShoppingList.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_items(self, shopping_list_id: UUID) -> ShoppingList | None:
        """
        Get shopping list with eagerly loaded items.

        Args:
            shopping_list_id: Shopping list UUID

        Returns:
            Shopping list with items or None
        """
        query = (
            select(ShoppingList)
            .where(ShoppingList.id == shopping_list_id)
            .options(selectinload(ShoppingList.items))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def recalculate_total(self, shopping_list_id: UUID) -> ShoppingList | None:
        """
        Recalculate total estimated cost from all items.

        Args:
            shopping_list_id: Shopping list UUID

        Returns:
            Updated shopping list or None
        """
        shopping_list = await self.get_with_items(shopping_list_id)
        if shopping_list is None:
            return None

        total = sum(
            item.estimated_total_cost or Decimal("0.00")
            for item in shopping_list.items
        )

        shopping_list.total_estimated_cost = total
        await self.db.commit()
        await self.db.refresh(shopping_list)
        return shopping_list


class ShoppingListItemRepository(BaseRepository[ShoppingListItem]):
    """Repository for ShoppingListItem operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        super().__init__(ShoppingListItem, db)

    async def get_by_shopping_list(
        self,
        shopping_list_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ShoppingListItem]:
        """
        Get items by shopping list ID.

        Args:
            shopping_list_id: Shopping list UUID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of shopping list items
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"shopping_list_id": shopping_list_id},
        )

    async def get_by_category(
        self,
        shopping_list_id: UUID,
        material_category: str,
    ) -> list[ShoppingListItem]:
        """
        Get items by category.

        Args:
            shopping_list_id: Shopping list UUID
            material_category: Material category

        Returns:
            List of shopping list items in category
        """
        return await self.get_multi(
            filters={
                "shopping_list_id": shopping_list_id,
                "material_category": material_category,
            }
        )

    async def get_by_purchase_status(
        self,
        shopping_list_id: UUID,
        purchase_status: str,
    ) -> list[ShoppingListItem]:
        """
        Get items by purchase status.

        Args:
            shopping_list_id: Shopping list UUID
            purchase_status: Purchase status

        Returns:
            List of shopping list items with status
        """
        return await self.get_multi(
            filters={
                "shopping_list_id": shopping_list_id,
                "purchase_status": purchase_status,
            }
        )

    async def mark_purchased(
        self,
        item_id: UUID,
        actual_unit_price: Decimal,
        actual_quantity: Decimal | None = None,
    ) -> ShoppingListItem | None:
        """
        Mark item as purchased with actual pricing.

        Args:
            item_id: Shopping list item UUID
            actual_unit_price: Actual unit price paid
            actual_quantity: Actual quantity purchased (defaults to planned quantity)

        Returns:
            Updated item or None
        """
        item = await self.get(item_id)
        if item is None:
            return None

        item.purchase_status = "purchased"
        item.actual_unit_price = actual_unit_price

        if actual_quantity is not None:
            item.actual_total_cost = actual_unit_price * actual_quantity
        else:
            item.actual_total_cost = actual_unit_price * item.actual_purchase_quantity

        await self.db.commit()
        await self.db.refresh(item)
        return item
