"""Add student profile fields

Revision ID: add_student_profile_fields
Revises: update_users_table
Create Date: 2024-04-10 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_student_profile_fields'
down_revision: Union[str, None] = 'update_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add new columns to user_profiles table
    op.add_column('user_profiles', sa.Column('name', sa.String(255), nullable=True))
    op.add_column('user_profiles', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('user_profiles', sa.Column('sex', sa.String(50), nullable=True))
    op.add_column('user_profiles', sa.Column('major', sa.String(255), nullable=True))
    op.add_column('user_profiles', sa.Column('year', sa.Integer(), nullable=True))
    op.add_column('user_profiles', sa.Column('gpa', sa.Float(), nullable=True))
    op.add_column('user_profiles', sa.Column('hobbies', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('country', sa.String(255), nullable=True))
    op.add_column('user_profiles', sa.Column('state_province', sa.String(255), nullable=True))
    op.add_column('user_profiles', sa.Column('unique_quality', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('story', sa.Text(), nullable=True))

def downgrade() -> None:
    # Remove the new columns
    op.drop_column('user_profiles', 'name')
    op.drop_column('user_profiles', 'age')
    op.drop_column('user_profiles', 'sex')
    op.drop_column('user_profiles', 'major')
    op.drop_column('user_profiles', 'year')
    op.drop_column('user_profiles', 'gpa')
    op.drop_column('user_profiles', 'hobbies')
    op.drop_column('user_profiles', 'country')
    op.drop_column('user_profiles', 'state_province')
    op.drop_column('user_profiles', 'unique_quality')
    op.drop_column('user_profiles', 'story') 