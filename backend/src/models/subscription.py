"""Subscription models."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin, UUIDMixin


class Subscription(Base, UUIDMixin, TimestampMixin):
    """
    User subscription synced from Stripe.

    Updated via Stripe webhooks (customer.subscription.* events).
    Denormalized for fast tier checks without API calls.
    """

    __tablename__ = "subscriptions"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    stripe_subscription_id: Mapped[str | None] = mapped_column(
        Text,
        unique=True,
        nullable=True,
    )

    stripe_customer_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    tier: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "tier IN ('free', 'pro', 'business')",
            name="ck_subscriptions_tier",
        ),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "status IN ('active', 'canceled', 'past_due', 'trialing')",
            name="ck_subscriptions_status",
        ),
        nullable=False,
    )

    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    user: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="subscription",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Subscription(id={self.id}, tier={self.tier}, status={self.status})>"
