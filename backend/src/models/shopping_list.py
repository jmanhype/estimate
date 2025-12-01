"""Shopping list models."""

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.project import Project


from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin, UUIDMixin


class ShoppingList(Base, UUIDMixin, TimestampMixin):
    """
    Shopping list for a project (1:1 relationship).

    Contains estimated materials and costs.
    """

    __tablename__ = "shopping_lists"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    total_estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="shopping_list",
    )

    items: Mapped[list["ShoppingListItem"]] = relationship(
        "ShoppingListItem",
        back_populates="shopping_list",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ShoppingList(id={self.id}, total_cost={self.total_estimated_cost})>"


class ShoppingListItem(Base, UUIDMixin, TimestampMixin):
    """
    Individual material item in shopping list.

    Stores calculated quantities, waste factors, and pricing.
    """

    __tablename__ = "shopping_list_items"

    shopping_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shopping_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    material_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    material_category: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "material_category IN ('paint', 'primer', 'flooring', 'tile', 'grout', 'thinset', "
            "'lumber', 'concrete', 'roofing', 'decking', 'fasteners', 'other')",
            name="ck_shopping_list_items_category",
        ),
        nullable=False,
        index=True,
    )

    calculated_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    waste_factor_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    actual_purchase_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    unit_of_measure: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "unit_of_measure IN ('gallons', 'square_feet', 'linear_feet', "
            "'boxes', 'bags', 'pieces', 'each')",
            name="ck_shopping_list_items_unit",
        ),
        nullable=False,
    )

    estimated_unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    estimated_total_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    actual_unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    actual_total_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    purchase_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "purchase_status IN ('not_purchased', 'purchased')",
            name="ck_shopping_list_items_purchase_status",
        ),
        default="not_purchased",
        nullable=False,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    shopping_list: Mapped["ShoppingList"] = relationship(
        "ShoppingList",
        back_populates="items",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ShoppingListItem(id={self.id}, material={self.material_name})>"
