"""Add onboarding_completed column to users table

Revision ID: add_onboarding_completed
Revises: 
Create Date: 2025-07-18 15:28:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_onboarding_completed'
down_revision = None  # Update this to your latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Add the onboarding_completed column to the users table
    op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, default=False))
    
    # For existing users, we'll check if they have a personality profile
    # and set onboarding_completed accordingly
    connection = op.get_bind()
    
    # First set all users to not completed
    connection.execute(sa.text("UPDATE users SET onboarding_completed = false"))
    
    # Then set to true for users who have personality profiles
    connection.execute(sa.text("""
        UPDATE users 
        SET onboarding_completed = true 
        WHERE id IN (
            SELECT DISTINCT user_id 
            FROM personality_profiles 
            WHERE user_id IS NOT NULL
        )
    """))


def downgrade():
    # Remove the onboarding_completed column
    op.drop_column('users', 'onboarding_completed')