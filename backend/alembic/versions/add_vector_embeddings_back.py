"""Add vector embeddings back

Revision ID: add_vector_embeddings_back
Revises: add_missing_tables
Create Date: 2024-04-16 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_vector_embeddings_back'
down_revision: Union[str, None] = 'add_missing_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add embedding column to user_profiles
    op.add_column('user_profiles', sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True))


def downgrade() -> None:
    # Drop the embedding column
    op.drop_column('user_profiles', 'embedding') 