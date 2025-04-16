"""Add user_skills table

Revision ID: add_user_skills_table
Revises: 383abf336991
Create Date: 2024-04-16 11:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_user_skills_table'
down_revision: Union[str, None] = '383abf336991'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
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
    op.drop_index(op.f('ix_user_skills_id'), table_name='user_skills')
    op.drop_table('user_skills') 