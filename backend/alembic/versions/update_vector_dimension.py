"""Update vector dimension

Revision ID: update_vector_dimension
Revises: add_vector_embeddings
Create Date: 2024-04-14 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'update_vector_dimension'
down_revision: Union[str, None] = 'add_vector_embeddings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # First drop the existing embedding column
    op.execute('ALTER TABLE user_profiles DROP COLUMN IF EXISTS embedding;')
    
    # Then add the new embedding column with correct dimensions
    op.execute('ALTER TABLE user_profiles ADD COLUMN embedding float[];')

def downgrade() -> None:
    # First drop the embedding column
    op.execute('ALTER TABLE user_profiles DROP COLUMN IF EXISTS embedding;')
    
    # Then restore the original embedding column
    op.execute('ALTER TABLE user_profiles ADD COLUMN embedding float[];') 