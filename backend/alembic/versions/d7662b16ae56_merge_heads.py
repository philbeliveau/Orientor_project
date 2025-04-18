"""merge heads

Revision ID: d7662b16ae56
Revises: add_cognitive_traits, add_vector_embeddings_back
Create Date: 2025-04-18 10:00:41.461678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7662b16ae56'
down_revision: Union[str, None] = ('add_cognitive_traits', 'add_vector_embeddings_back')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
