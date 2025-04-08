"""Update users table - remove username and add created_at and profile

Revision ID: update_users_table
Revises: 0aa1df5fd735
Create Date: 2024-04-08 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'update_users_table'
down_revision: Union[str, None] = '0aa1df5fd735'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add created_at column
    op.add_column('users',
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.func.now(), 
                  nullable=False)
    )
    
    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('favorite_movie', sa.String(255), nullable=True),
        sa.Column('favorite_book', sa.String(255), nullable=True),
        sa.Column('favorite_celebrities', sa.Text(), nullable=True),
        sa.Column('learning_style', sa.String(50), nullable=True),
        sa.Column('interests', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'], unique=True)
    
    # Drop username column and its index
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'username')

def downgrade() -> None:
    # Drop user_profiles table
    op.drop_index('ix_user_profiles_user_id', table_name='user_profiles')
    op.drop_table('user_profiles')
    
    # Add username column back
    op.add_column('users',
        sa.Column('username', sa.String(50), nullable=True)
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    
    # Drop created_at column
    op.drop_column('users', 'created_at') 