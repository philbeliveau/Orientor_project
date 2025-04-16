"""merge heads

Revision ID: 7085dfa9bba2
Revises: 6dcdf8a4ad47, add_space_feature_tables, add_user_skills_table
Create Date: 2025-04-16 15:24:33.127735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7085dfa9bba2'
down_revision: Union[str, None] = ('6dcdf8a4ad47', 'add_space_feature_tables', 'add_user_skills_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
