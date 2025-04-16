"""Add missing tables

Revision ID: add_missing_tables
Revises: 7085dfa9bba2
Create Date: 2024-04-16 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_missing_tables'
down_revision: Union[str, None] = '7085dfa9bba2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add messages table
    op.create_table('messages',
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('message_id')
    )
    op.create_index('ix_messages_recipient_id', 'messages', ['recipient_id'], unique=False)
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'], unique=False)
    op.create_index('ix_messages_timestamp', 'messages', ['timestamp'], unique=False)

    # Add saved_recommendations table
    op.create_table('saved_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('oasis_code', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('main_duties', sa.Text(), nullable=True),
        sa.Column('role_creativity', sa.Float(), nullable=True),
        sa.Column('role_leadership', sa.Float(), nullable=True),
        sa.Column('role_digital_literacy', sa.Float(), nullable=True),
        sa.Column('role_critical_thinking', sa.Float(), nullable=True),
        sa.Column('role_problem_solving', sa.Float(), nullable=True),
        sa.Column('saved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'oasis_code', name='uq_user_oasis_code')
    )
    op.create_index('ix_saved_recommendations_user_id', 'saved_recommendations', ['user_id'], unique=False)

    # Add suggested_peers table
    op.create_table('suggested_peers',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('suggested_id', sa.Integer(), nullable=False),
        sa.Column('similarity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['suggested_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'suggested_id')
    )
    op.create_index('ix_suggested_peers_suggested_id', 'suggested_peers', ['suggested_id'], unique=False)
    op.create_index('ix_suggested_peers_user_id', 'suggested_peers', ['user_id'], unique=False)

    # Add user_notes table
    op.create_table('user_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('saved_recommendation_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['saved_recommendation_id'], ['saved_recommendations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_notes_saved_recommendation_id', 'user_notes', ['saved_recommendation_id'], unique=False)
    op.create_index('ix_user_notes_user_id', 'user_notes', ['user_id'], unique=False)

    # Add user_skills table
    op.create_table('user_skills',
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
    op.create_index('ix_user_skills_id', 'user_skills', ['id'], unique=False)

    # Update users table with skill columns
    op.add_column('users', sa.Column('creativity', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('leadership', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('digital_literacy', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('critical_thinking', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('problem_solving', sa.Float(), nullable=True))

    # Update user_profiles table with additional fields
    op.add_column('user_profiles', sa.Column('name', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('user_profiles', sa.Column('sex', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('major', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('year', sa.Integer(), nullable=True))
    op.add_column('user_profiles', sa.Column('gpa', sa.Float(), nullable=True))
    op.add_column('user_profiles', sa.Column('hobbies', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('country', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('state_province', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('unique_quality', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('story', sa.Text(), nullable=True))


def downgrade() -> None:
    # Drop added columns from user_profiles
    op.drop_column('user_profiles', 'story')
    op.drop_column('user_profiles', 'unique_quality')
    op.drop_column('user_profiles', 'state_province')
    op.drop_column('user_profiles', 'country')
    op.drop_column('user_profiles', 'hobbies')
    op.drop_column('user_profiles', 'gpa')
    op.drop_column('user_profiles', 'year')
    op.drop_column('user_profiles', 'major')
    op.drop_column('user_profiles', 'sex')
    op.drop_column('user_profiles', 'age')
    op.drop_column('user_profiles', 'name')

    # Drop added columns from users
    op.drop_column('users', 'problem_solving')
    op.drop_column('users', 'critical_thinking')
    op.drop_column('users', 'digital_literacy')
    op.drop_column('users', 'leadership')
    op.drop_column('users', 'creativity')

    # Drop tables in reverse order of creation
    op.drop_table('user_skills')
    op.drop_table('user_notes')
    op.drop_table('suggested_peers')
    op.drop_table('saved_recommendations')
    op.drop_table('messages') 