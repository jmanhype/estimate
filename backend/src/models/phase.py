"""Project phase models for timeline planning."""

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.project import Project

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin, UUIDMixin


class ProjectPhase(Base, UUIDMixin, TimestampMixin):
    """
    Project timeline phase.

    Represents a distinct phase in the project timeline (e.g., "Preparation",
    "Painting", "Cleanup") with estimated duration and dependencies.
    """

    __tablename__ = "project_phases"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    phase_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed', 'blocked')",
            name="ck_project_phases_status",
        ),
        default="not_started",
        nullable=False,
        index=True,
    )

    estimated_duration_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    actual_start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    actual_end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # Materials should be ordered by this date
    materials_order_by_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="phases",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ProjectPhase(id={self.id}, name={self.name}, status={self.status}, order={self.phase_order})>"
