"""Add Space feature tables

Revision ID: add_space_feature_tables
Revises: update_profile_fields
Create Date: 2023-04-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_space_feature_tables'
down_revision: Union[str, None] = 'update_profile_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create saved_recommendations table
    op.create_table(
        'saved_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('oasis_code', sa.String(length=20), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('saved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'oasis_code', name='uq_user_recommendation')
    )
    op.create_index(op.f('ix_saved_recommendations_id'), 'saved_recommendations', ['id'], unique=False)
    
    # Create user_notes table
    op.create_table(
        'user_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recommendation_id'], ['saved_recommendations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_notes_id'), 'user_notes', ['id'], unique=False)
    
    # Create user_skills table
    op.create_table(
        'user_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('creativity', sa.Float(), nullable=True),
        sa.Column('leadership', sa.Float(), nullable=True),
        sa.Column('digital_literacy', sa.Float(), nullable=True),
        sa.Column('critical_thinking', sa.Float(), nullable=True),
        sa.Column('problem_solving', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_skills_id'), 'user_skills', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_user_skills_id'), table_name='user_skills')
    op.drop_table('user_skills')
    
    op.drop_index(op.f('ix_user_notes_id'), table_name='user_notes')
    op.drop_table('user_notes')
    
    op.drop_index(op.f('ix_saved_recommendations_id'), table_name='saved_recommendations')
    op.drop_table('saved_recommendations') 