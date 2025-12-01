"""Tests for SubscriptionRepository."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.subscription import Subscription
from src.models.user import UserProfile
from src.repositories.subscription import SubscriptionRepository
from src.repositories.user import UserRepository


class TestSubscriptionRepository:
    """Tests for SubscriptionRepository methods."""

    @pytest.fixture
    async def user_repo(self, test_session: AsyncSession) -> UserRepository:
        """Create UserRepository instance."""
        return UserRepository(test_session)

    @pytest.fixture
    async def subscription_repo(self, test_session: AsyncSession) -> SubscriptionRepository:
        """Create SubscriptionRepository instance."""
        return SubscriptionRepository(test_session)

    @pytest.fixture
    async def sample_user(self, user_repo: UserRepository) -> UserProfile:
        """Create a sample user for testing."""
        return await user_repo.create({
            "skill_level": "intermediate",
        })

    @pytest.fixture
    async def sample_subscription(
        self,
        subscription_repo: SubscriptionRepository,
        sample_user: UserProfile,
    ) -> Subscription:
        """Create a sample subscription for testing."""
        now = datetime.now(tz=timezone.utc)
        return await subscription_repo.create({
            "user_id": sample_user.id,
            "stripe_subscription_id": "sub_test123",
            "stripe_customer_id": "cus_test123",
            "tier": "pro",
            "status": "active",
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
            "cancel_at_period_end": False,
        })

    async def test_get_by_user_id(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
        sample_user: UserProfile,
    ) -> None:
        """Test getting subscription by user ID."""
        subscription = await subscription_repo.get_by_user_id(sample_user.id)
        assert subscription is not None
        assert subscription.id == sample_subscription.id
        assert subscription.user_id == sample_user.id

    async def test_get_by_user_id_not_found(
        self,
        subscription_repo: SubscriptionRepository,
    ) -> None:
        """Test getting subscription by non-existent user ID."""
        subscription = await subscription_repo.get_by_user_id(uuid4())
        assert subscription is None

    async def test_get_by_stripe_subscription_id(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
    ) -> None:
        """Test getting subscription by Stripe subscription ID."""
        subscription = await subscription_repo.get_by_stripe_subscription_id("sub_test123")
        assert subscription is not None
        assert subscription.id == sample_subscription.id
        assert subscription.stripe_subscription_id == "sub_test123"

    async def test_get_by_stripe_subscription_id_not_found(
        self,
        subscription_repo: SubscriptionRepository,
    ) -> None:
        """Test getting subscription by non-existent Stripe subscription ID."""
        subscription = await subscription_repo.get_by_stripe_subscription_id("sub_nonexistent")
        assert subscription is None

    async def test_get_by_stripe_customer_id(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
    ) -> None:
        """Test getting subscription by Stripe customer ID."""
        subscription = await subscription_repo.get_by_stripe_customer_id("cus_test123")
        assert subscription is not None
        assert subscription.id == sample_subscription.id
        assert subscription.stripe_customer_id == "cus_test123"

    async def test_get_by_stripe_customer_id_not_found(
        self,
        subscription_repo: SubscriptionRepository,
    ) -> None:
        """Test getting subscription by non-existent Stripe customer ID."""
        subscription = await subscription_repo.get_by_stripe_customer_id("cus_nonexistent")
        assert subscription is None

    async def test_get_with_user(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
        sample_user: UserProfile,
    ) -> None:
        """Test getting subscription with eagerly loaded user."""
        subscription = await subscription_repo.get_with_user(sample_subscription.id)
        assert subscription is not None
        assert subscription.id == sample_subscription.id
        # User relationship should be loaded
        assert subscription.user is not None
        assert subscription.user.id == sample_user.id

    async def test_get_by_tier(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
        user_repo: UserRepository,
    ) -> None:
        """Test getting subscriptions by tier."""
        # Create additional users and subscriptions
        user2 = await user_repo.create({"skill_level": "beginner"})
        now = datetime.now(tz=timezone.utc)
        await subscription_repo.create({
            "user_id": user2.id,
            "stripe_customer_id": "cus_test456",
            "tier": "free",
            "status": "active",
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
        })

        subscriptions = await subscription_repo.get_by_tier("pro")
        assert len(subscriptions) >= 1
        assert all(s.tier == "pro" for s in subscriptions)

    async def test_get_by_tier_with_pagination(
        self,
        subscription_repo: SubscriptionRepository,
        user_repo: UserRepository,
    ) -> None:
        """Test getting subscriptions by tier with pagination."""
        # Create multiple users and subscriptions
        now = datetime.now(tz=timezone.utc)
        for i in range(5):
            user = await user_repo.create({"skill_level": "beginner"})
            await subscription_repo.create({
                "user_id": user.id,
                "stripe_customer_id": f"cus_free{i}",
                "tier": "free",
                "status": "active",
                "current_period_start": now,
                "current_period_end": now + timedelta(days=30),
            })

        subscriptions = await subscription_repo.get_by_tier("free", skip=2, limit=2)
        assert len(subscriptions) == 2

    async def test_get_by_status(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
    ) -> None:
        """Test getting subscriptions by status."""
        subscriptions = await subscription_repo.get_by_status("active")
        assert len(subscriptions) >= 1
        assert all(s.status == "active" for s in subscriptions)

    async def test_get_active_subscriptions(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
        user_repo: UserRepository,
    ) -> None:
        """Test getting all active subscriptions."""
        # Create a canceled subscription
        user2 = await user_repo.create({"skill_level": "expert"})
        now = datetime.now(tz=timezone.utc)
        await subscription_repo.create({
            "user_id": user2.id,
            "stripe_customer_id": "cus_test789",
            "tier": "pro",
            "status": "canceled",
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
        })

        active_subs = await subscription_repo.get_active_subscriptions()
        assert len(active_subs) >= 1
        assert all(s.status == "active" for s in active_subs)

    async def test_get_expiring_soon(
        self,
        subscription_repo: SubscriptionRepository,
        user_repo: UserRepository,
    ) -> None:
        """Test getting subscriptions expiring soon."""
        now = datetime.now(tz=timezone.utc)
        expiring_date = now + timedelta(days=5)

        # Create subscription expiring in 5 days
        user1 = await user_repo.create({"skill_level": "beginner"})
        await subscription_repo.create({
            "user_id": user1.id,
            "stripe_customer_id": "cus_expiring1",
            "tier": "pro",
            "status": "active",
            "current_period_start": now - timedelta(days=25),
            "current_period_end": expiring_date,
        })

        # Create subscription expiring in 60 days (should not be included)
        user2 = await user_repo.create({"skill_level": "intermediate"})
        await subscription_repo.create({
            "user_id": user2.id,
            "stripe_customer_id": "cus_not_expiring",
            "tier": "pro",
            "status": "active",
            "current_period_start": now,
            "current_period_end": now + timedelta(days=60),
        })

        # Get subscriptions expiring within 7 days
        threshold = now + timedelta(days=7)
        expiring_subs = await subscription_repo.get_expiring_soon(threshold)

        assert len(expiring_subs) >= 1
        assert all(s.current_period_end <= threshold for s in expiring_subs)
        assert all(s.status == "active" for s in expiring_subs)

    async def test_get_canceling_at_period_end(
        self,
        subscription_repo: SubscriptionRepository,
        user_repo: UserRepository,
    ) -> None:
        """Test getting subscriptions set to cancel at period end."""
        now = datetime.now(tz=timezone.utc)

        # Create subscription canceling at period end
        user1 = await user_repo.create({"skill_level": "beginner"})
        await subscription_repo.create({
            "user_id": user1.id,
            "stripe_customer_id": "cus_canceling1",
            "tier": "pro",
            "status": "active",
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
            "cancel_at_period_end": True,
        })

        # Create normal subscription (should not be included)
        user2 = await user_repo.create({"skill_level": "intermediate"})
        await subscription_repo.create({
            "user_id": user2.id,
            "stripe_customer_id": "cus_normal",
            "tier": "pro",
            "status": "active",
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
            "cancel_at_period_end": False,
        })

        canceling_subs = await subscription_repo.get_canceling_at_period_end()
        assert len(canceling_subs) >= 1
        assert all(s.cancel_at_period_end is True for s in canceling_subs)

    async def test_count_by_tier(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
        user_repo: UserRepository,
    ) -> None:
        """Test counting subscriptions by tier."""
        # Create additional subscriptions
        now = datetime.now(tz=timezone.utc)
        for i in range(2):
            user = await user_repo.create({"skill_level": "beginner"})
            await subscription_repo.create({
                "user_id": user.id,
                "stripe_customer_id": f"cus_count_test{i}",
                "tier": "business",
                "status": "active",
                "current_period_start": now,
                "current_period_end": now + timedelta(days=30),
            })

        count = await subscription_repo.count_by_tier("business")
        assert count == 2

    async def test_count_by_status(
        self,
        subscription_repo: SubscriptionRepository,
        sample_subscription: Subscription,
    ) -> None:
        """Test counting subscriptions by status."""
        count = await subscription_repo.count_by_status("active")
        assert count >= 1

    async def test_count_by_tier_zero(
        self,
        subscription_repo: SubscriptionRepository,
    ) -> None:
        """Test counting subscriptions by tier with zero results."""
        count = await subscription_repo.count_by_tier("nonexistent")
        assert count == 0

    async def test_get_by_tier_no_results(
        self,
        subscription_repo: SubscriptionRepository,
    ) -> None:
        """Test getting subscriptions by tier with no results."""
        subscriptions = await subscription_repo.get_by_tier("nonexistent")
        assert subscriptions == []
