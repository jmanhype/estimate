"""Project feedback models for AI learning."""

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.project import Project
    from src.models.user import UserProfile

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin, UUIDMixin


class ProjectFeedback(Base, UUIDMixin, TimestampMixin):
    """
    User feedback on project estimates.

    Captures actual vs estimated materials usage for AI learning and
    improving future estimates.
    """

    __tablename__ = "project_feedback"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    material_type: Mapped[str] = mapped_column(
        String(50),
        CheckConstraint(
            "material_type IN ('paint', 'primer', 'flooring', 'tile', 'grout', "
            "'lumber', 'drywall', 'concrete', 'other')",
            name="ck_project_feedback_material_type",
        ),
        nullable=False,
        index=True,
    )

    estimated_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    actual_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    unit_of_measure: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "unit_of_measure IN ('gallon', 'quart', 'square_feet', 'square_meter', "
            "'piece', 'box', 'bag', 'roll', 'linear_feet', 'linear_meter')",
            name="ck_project_feedback_unit",
        ),
        nullable=False,
    )

    # Accuracy percentage: (1 - abs(actual - estimated) / actual) * 100
    accuracy_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # Room characteristics for learning
    room_square_footage: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    ceiling_height: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )

    user_skill_level: Mapped[str | None] = mapped_column(
        String(20),
        CheckConstraint(
            "user_skill_level IN ('beginner', 'intermediate', 'advanced', 'professional')",
            name="ck_project_feedback_skill_level",
        ),
        nullable=True,
    )

    project_complexity: Mapped[str | None] = mapped_column(
        String(20),
        CheckConstraint(
            "project_complexity IN ('simple', 'moderate', 'complex')",
            name="ck_project_feedback_complexity",
        ),
        nullable=True,
    )

    surface_condition: Mapped[str | None] = mapped_column(
        String(20),
        CheckConstraint(
            "surface_condition IN ('excellent', 'good', 'fair', 'poor')",
            name="ck_project_feedback_surface_condition",
        ),
        nullable=True,
    )

    # User comments
    comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Rating of estimate accuracy (1-5)
    rating: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_project_feedback_rating"),
        nullable=True,
    )

    # Whether this feedback should be used for model training
    use_for_training: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="feedback",
    )

    user: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="feedback",
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ProjectFeedback(id={self.id}, material={self.material_type}, "
            f"accuracy={self.accuracy_percentage}%)>"
        )
