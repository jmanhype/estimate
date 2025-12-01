"""Subscription repository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.subscription import Subscription
from src.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for Subscription operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        super().__init__(Subscription, db)

    async def get_by_user_id(self, user_id: UUID) -> Subscription | None:
        """
        Get subscription by user ID.

        Args:
            user_id: User UUID

        Returns:
            Subscription or None if not found
        """
        query = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_stripe_subscription_id(self, stripe_subscription_id: str) -> Subscription | None:
        """
        Get subscription by Stripe subscription ID.

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Subscription or None if not found
        """
        query = select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_stripe_customer_id(self, stripe_customer_id: str) -> Subscription | None:
        """
        Get subscription by Stripe customer ID.

        Args:
            stripe_customer_id: Stripe customer ID

        Returns:
            Subscription or None if not found
        """
        query = select(Subscription).where(Subscription.stripe_customer_id == stripe_customer_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_user(self, subscription_id: UUID) -> Subscription | None:
        """
        Get subscription with eagerly loaded user profile.

        Args:
            subscription_id: Subscription UUID

        Returns:
            Subscription with user or None
        """
        query = (
            select(Subscription)
            .where(Subscription.id == subscription_id)
            .options(selectinload(Subscription.user))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_tier(
        self,
        tier: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """
        Get subscriptions by tier.

        Args:
            tier: Subscription tier ('free', 'pro', 'business')
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of subscriptions
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"tier": tier},
        )

    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """
        Get subscriptions by status.

        Args:
            status: Subscription status ('active', 'canceled', 'past_due', 'trialing')
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of subscriptions
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"status": status},
        )

    async def get_active_subscriptions(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """
        Get all active subscriptions.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of active subscriptions
        """
        return await self.get_by_status("active", skip=skip, limit=limit)

    async def get_expiring_soon(
        self,
        before: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """
        Get subscriptions expiring before a certain date.

        Useful for sending renewal reminders.

        Args:
            before: DateTime threshold
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of subscriptions expiring soon
        """
        query = (
            select(Subscription)
            .where(
                Subscription.status == "active",
                Subscription.current_period_end <= before,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_canceling_at_period_end(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """
        Get subscriptions set to cancel at period end.

        Useful for win-back campaigns.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of subscriptions canceling at period end
        """
        query = (
            select(Subscription)
            .where(Subscription.cancel_at_period_end)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_tier(self, tier: str) -> int:
        """
        Count subscriptions by tier.

        Args:
            tier: Subscription tier

        Returns:
            Count of subscriptions with specified tier
        """
        return await self.count(filters={"tier": tier})

    async def count_by_status(self, status: str) -> int:
        """
        Count subscriptions by status.

        Args:
            status: Subscription status

        Returns:
            Count of subscriptions with specified status
        """
        return await self.count(filters={"status": status})
