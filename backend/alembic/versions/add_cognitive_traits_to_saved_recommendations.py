"""Add cognitive traits to saved_recommendations table

Revision ID: add_cognitive_traits
Revises: add_space_feature_tables
Create Date: 2024-03-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_cognitive_traits'
down_revision: Union[str, None] = 'add_space_feature_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to saved_recommendations table
    op.add_column('saved_recommendations', sa.Column('analytical_thinking', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('attention_to_detail', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('collaboration', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('adaptability', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('independence', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('evaluation', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('decision_making', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('stress_tolerance', sa.Float(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('all_fields', postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    # Remove the columns in reverse order
    op.drop_column('saved_recommendations', 'all_fields')
    op.drop_column('saved_recommendations', 'stress_tolerance')
    op.drop_column('saved_recommendations', 'decision_making')
    op.drop_column('saved_recommendations', 'evaluation')
    op.drop_column('saved_recommendations', 'independence')
    op.drop_column('saved_recommendations', 'adaptability')
    op.drop_column('saved_recommendations', 'collaboration')
    op.drop_column('saved_recommendations', 'attention_to_detail')
    op.drop_column('saved_recommendations', 'analytical_thinking') 