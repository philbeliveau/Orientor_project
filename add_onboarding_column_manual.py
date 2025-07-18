#!/usr/bin/env python3
"""
Manual migration script to add onboarding_completed column to users table
Run this if Alembic migration doesn't work
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_onboarding_column():
    """Add the onboarding_completed column to users table"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            
            try:
                # Check if column already exists
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'onboarding_completed'
                """))
                
                if result.fetchone():
                    logger.info("Column 'onboarding_completed' already exists")
                    return True
                
                # Add the column
                logger.info("Adding onboarding_completed column to users table...")
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE NOT NULL
                """))
                
                # Update existing users based on personality profiles
                logger.info("Updating existing users based on personality profiles...")
                
                # First, set all users to not completed
                connection.execute(text("UPDATE users SET onboarding_completed = FALSE"))
                
                # Then set to true for users who have personality profiles
                result = connection.execute(text("""
                    UPDATE users 
                    SET onboarding_completed = TRUE 
                    WHERE id IN (
                        SELECT DISTINCT user_id 
                        FROM personality_profiles 
                        WHERE user_id IS NOT NULL
                    )
                """))
                
                updated_count = result.rowcount
                logger.info(f"Updated {updated_count} users who have personality profiles")
                
                # Commit the transaction
                trans.commit()
                logger.info("✅ Successfully added onboarding_completed column")
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error during migration: {e}")
                return False
                
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = add_onboarding_column()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)