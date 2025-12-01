"""Project photo models."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    Project

from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import UUIDMixin


class ProjectPhoto(Base, UUIDMixin):
    """
    Uploaded photo for computer vision analysis.

    Stores metadata and CV analysis results.
    """

    __tablename__ = "project_photos"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(50),
        CheckConstraint(
            "mime_type IN ('image/jpeg', 'image/png', 'image/heic')",
            name="ck_project_photos_mime_type",
        ),
        nullable=False,
    )

    scan_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "scan_status IN ('pending', 'clean', 'quarantined')",
            name="ck_project_photos_scan_status",
        ),
        default="pending",
        nullable=False,
        index=True,
    )

    cv_analysis_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "cv_analysis_status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_project_photos_cv_status",
        ),
        default="pending",
        nullable=False,
        index=True,
    )

    cv_analysis_result: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    cv_confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="photos",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ProjectPhoto(id={self.id}, cv_status={self.cv_analysis_status})>"
