"""Retailer pricing models."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import UUIDMixin


class RetailerPrice(Base, UUIDMixin):
    """
    Current pricing data from retailers.

    No user_id (public data). Updated by background scraper.
    Not historical - only stores current prices.
    """

    __tablename__ = "retailer_prices"

    material_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    material_category: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    retailer_name: Mapped[str] = mapped_column(
        String(50),
        CheckConstraint(
            "retailer_name IN ('home_depot', 'lowes', 'menards', 'ace_hardware')",
            name="ck_retailer_prices_retailer",
        ),
        nullable=False,
        index=True,
    )

    product_sku: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    product_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    unit_of_measure: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    availability_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "availability_status IN ('in_stock', 'out_of_stock', 'unknown')",
            name="ck_retailer_prices_availability",
        ),
        default="unknown",
        nullable=False,
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<RetailerPrice(material={self.material_name}, retailer={self.retailer_name}, price={self.unit_price})>"
