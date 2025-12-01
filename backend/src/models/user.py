"""User-related models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.project import Project
    from src.models.subscription import Subscription


class UserProfile(Base, UUIDMixin, TimestampMixin):
    """
    User profile extending Supabase Auth.

    This table stores application-specific user data.
    The id references auth.users(id) in Supabase.
    """

    __tablename__ = "user_profiles"

    # Foreign key to Supabase auth.users (managed externally)
    # id is the PK from UUIDMixin and also serves as FK to auth.users

    skill_level: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "skill_level IN ('beginner', 'intermediate', 'expert')",
            name="ck_user_profiles_skill_level",
        ),
        nullable=False,
    )

    company_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    projects: Mapped[list[Project]] = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    subscription: Mapped[Subscription | None] = relationship(
        "Subscription",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<UserProfile(id={self.id}, skill_level={self.skill_level})>"
