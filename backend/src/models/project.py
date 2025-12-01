"""Project models."""

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    UserProfile
    ProjectPhoto
    ShoppingList


from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin, UUIDMixin


class Project(Base, UUIDMixin, TimestampMixin):
    """
    Renovation project.

    Represents a single renovation job with photos, estimates, and shopping list.
    """

    __tablename__ = "projects"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    project_type: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "project_type IN ('painting', 'flooring', 'tiling', 'drywall', "
            "'concrete', 'roofing', 'decking', 'fencing', 'kitchen', 'bathroom', 'other')",
            name="ck_projects_project_type",
        ),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "status IN ('draft', 'in_progress', 'completed')",
            name="ck_projects_status",
        ),
        default="draft",
        nullable=False,
        index=True,
    )

    budget_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    total_estimated_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    total_actual_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # Relationships
    user: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="projects",
    )

    photos: Mapped[list["ProjectPhoto"]] = relationship(
        "ProjectPhoto",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    shopping_list: Mapped["ShoppingList | None"] = relationship(
        "ShoppingList",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
