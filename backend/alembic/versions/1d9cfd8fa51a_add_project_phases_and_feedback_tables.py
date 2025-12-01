"""add_project_phases_and_feedback_tables

Revision ID: 1d9cfd8fa51a
Revises: 883e7bc4375b
Create Date: 2025-12-01 10:27:47.487470

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1d9cfd8fa51a'
down_revision: str | Sequence[str] | None = '883e7bc4375b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create project_phases table
    op.create_table(
        'project_phases',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('phase_order', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('estimated_duration_days', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('actual_start_date', sa.Date(), nullable=True),
        sa.Column('actual_end_date', sa.Date(), nullable=True),
        sa.Column('materials_order_by_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed', 'blocked')",
            name='ck_project_phases_status'
        ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_phases_project_id'), 'project_phases', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_phases_status'), 'project_phases', ['status'], unique=False)

    # Create project_feedback table
    op.create_table(
        'project_feedback',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('material_type', sa.String(length=50), nullable=False),
        sa.Column('estimated_quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('actual_quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=False),
        sa.Column('accuracy_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('room_square_footage', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('ceiling_height', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('user_skill_level', sa.String(length=20), nullable=True),
        sa.Column('project_complexity', sa.String(length=20), nullable=True),
        sa.Column('surface_condition', sa.String(length=20), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('use_for_training', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "material_type IN ('paint', 'primer', 'flooring', 'tile', 'grout', "
            "'lumber', 'drywall', 'concrete', 'other')",
            name='ck_project_feedback_material_type'
        ),
        sa.CheckConstraint(
            "unit_of_measure IN ('gallon', 'quart', 'square_feet', 'square_meter', "
            "'piece', 'box', 'bag', 'roll', 'linear_feet', 'linear_meter')",
            name='ck_project_feedback_unit'
        ),
        sa.CheckConstraint(
            "user_skill_level IN ('beginner', 'intermediate', 'advanced', 'professional')",
            name='ck_project_feedback_skill_level'
        ),
        sa.CheckConstraint(
            "project_complexity IN ('simple', 'moderate', 'complex')",
            name='ck_project_feedback_complexity'
        ),
        sa.CheckConstraint(
            "surface_condition IN ('excellent', 'good', 'fair', 'poor')",
            name='ck_project_feedback_surface_condition'
        ),
        sa.CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name='ck_project_feedback_rating'
        ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_feedback_project_id'), 'project_feedback', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_feedback_user_id'), 'project_feedback', ['user_id'], unique=False)
    op.create_index(op.f('ix_project_feedback_material_type'), 'project_feedback', ['material_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop project_feedback table
    op.drop_index(op.f('ix_project_feedback_material_type'), table_name='project_feedback')
    op.drop_index(op.f('ix_project_feedback_user_id'), table_name='project_feedback')
    op.drop_index(op.f('ix_project_feedback_project_id'), table_name='project_feedback')
    op.drop_table('project_feedback')

    # Drop project_phases table
    op.drop_index(op.f('ix_project_phases_status'), table_name='project_phases')
    op.drop_index(op.f('ix_project_phases_project_id'), table_name='project_phases')
    op.drop_table('project_phases')
