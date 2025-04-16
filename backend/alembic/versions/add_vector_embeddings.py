"""Add vector embeddings and suggested peers table

Revision ID: add_vector_embeddings
Revises: update_profile_fields
Create Date: 2024-04-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_vector_embeddings'
down_revision: Union[str, None] = 'update_profile_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add embedding column to user_profiles (using float array instead of vector)
    op.execute('ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS embedding float[];')
    
    # Create suggested_peers table
    op.create_table(
        'suggested_peers',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('suggested_id', sa.Integer(), nullable=False),
        sa.Column('similarity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['suggested_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'suggested_id')
    )
    
    # Create indices
    op.create_index('ix_suggested_peers_user_id', 'suggested_peers', ['user_id'], unique=False)
    op.create_index('ix_suggested_peers_suggested_id', 'suggested_peers', ['suggested_id'], unique=False)

def downgrade() -> None:
    # Drop suggested_peers table
    op.drop_table('suggested_peers')
    
    # Drop embedding column from user_profiles
    op.execute('ALTER TABLE user_profiles DROP COLUMN IF EXISTS embedding;') 