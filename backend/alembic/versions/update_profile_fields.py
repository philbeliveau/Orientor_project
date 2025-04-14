"""Update profile fields

Revision ID: update_profile_fields
Revises: add_student_profile_fields
Create Date: 2024-04-10 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'update_profile_fields'
down_revision: Union[str, None] = 'add_student_profile_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add columns if they don't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                         WHERE table_name = 'user_profiles' AND column_name = 'favorite_movie') THEN
                ALTER TABLE user_profiles ADD COLUMN favorite_movie VARCHAR(255);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                         WHERE table_name = 'user_profiles' AND column_name = 'favorite_book') THEN
                ALTER TABLE user_profiles ADD COLUMN favorite_book VARCHAR(255);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                         WHERE table_name = 'user_profiles' AND column_name = 'favorite_celebrities') THEN
                ALTER TABLE user_profiles ADD COLUMN favorite_celebrities TEXT;
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                         WHERE table_name = 'user_profiles' AND column_name = 'learning_style') THEN
                ALTER TABLE user_profiles ADD COLUMN learning_style VARCHAR(50);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                         WHERE table_name = 'user_profiles' AND column_name = 'interests') THEN
                ALTER TABLE user_profiles ADD COLUMN interests TEXT;
            END IF;
        END
        $$;
    """)

def downgrade() -> None:
    # Remove the columns if they exist
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'user_profiles' AND column_name = 'favorite_movie') THEN
                ALTER TABLE user_profiles DROP COLUMN favorite_movie;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'user_profiles' AND column_name = 'favorite_book') THEN
                ALTER TABLE user_profiles DROP COLUMN favorite_book;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'user_profiles' AND column_name = 'favorite_celebrities') THEN
                ALTER TABLE user_profiles DROP COLUMN favorite_celebrities;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'user_profiles' AND column_name = 'learning_style') THEN
                ALTER TABLE user_profiles DROP COLUMN learning_style;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'user_profiles' AND column_name = 'interests') THEN
                ALTER TABLE user_profiles DROP COLUMN interests;
            END IF;
        END
        $$;
    """) 