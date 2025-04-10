from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.user_profile import UserProfile
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Construct DATABASE_URL from individual components
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "orientor_db")

    if all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]):
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    else:
        logger.error("Database connection details are not properly configured")
        sys.exit(1)

# Ensure the URL uses the correct protocol
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Log connection details (without sensitive information)
safe_url = DATABASE_URL.split("@")[0].split("://")[0] + "://*****@" + DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "DATABASE_URL is set but masked for security"
logger.info(f"Using database URL: {safe_url}")

# Create engine and session
try:
    engine = create_engine(DATABASE_URL)
    # Test the connection
    with engine.connect() as conn:
        logger.info("Successfully connected to the database!")
except Exception as e:
    logger.error(f"Failed to connect to the database: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# User data from backup with current timestamps
current_time = datetime.now(pytz.UTC)
users_data = [
    {"id": 1, "email": "new_email@example.com", "hashed_password": "$2b$12$pRq9wkUrEXEgYgzzHTPjNOHND/ApgBWzuVuFeALVRW.cjx8tuAnoO"},
    {"id": 3, "email": "test_gocn0k84@example.com", "hashed_password": "$2b$12$585qBlLYlUSZnU1Wu6Xqme8oeFlqOalFeDTF.er0dI7PchgnLeiOq"},
    {"id": 2, "email": "testuser@example.com", "hashed_password": "$2b$12$qR9EipT0PftdEDT5rRgPBOtwaQzxPT68PSkWCw.cc2Uc9AQqC6TIC"},
    {"id": 6, "email": "user2@example.com", "hashed_password": "$2b$12$lzBJcVFcG3DXO9Ac8aJMZOJLum9ZlYxcRobpi2t7.iK4qcCqp.Exe"},
    {"id": 7, "email": "user3@example.com", "hashed_password": "$2b$12$XMz9x2gRS261Sibe8LGYa.wd9mtFPCsIwvx0ND8rOirdvuNBNwmVW"}
]

# Profile data from backup
profiles_data = [
    {"id": 1, "user_id": 2, "favorite_movie": "Call me by your name", "favorite_book": "Why buddhism is true", "favorite_celebrities": "Jason Statham", "learning_style": "Visual", "interests": "Philosophy, basketball, investing, geopolitics.\n\n"},
    {"id": 2, "user_id": 6, "favorite_movie": "", "favorite_book": "", "favorite_celebrities": "", "learning_style": "", "interests": ""},
    {"id": 3, "user_id": 7, "favorite_movie": "You", "favorite_book": "The AGI revolution", "favorite_celebrities": "Lebron james", "learning_style": "", "interests": "Ball"}
]

def clear_existing_data():
    db = SessionLocal()
    try:
        # Delete all profiles first (due to foreign key constraints)
        db.query(UserProfile).delete()
        logger.info("Cleared existing user profiles")
        
        # Then delete all users
        db.query(User).delete()
        logger.info("Cleared existing users")
        
        db.commit()
        logger.info("Successfully cleared all existing data")
    except Exception as e:
        logger.error(f"Error clearing existing data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def seed_database():
    db = SessionLocal()
    try:
        # Clear existing data first
        clear_existing_data()
        
        # Insert users
        for user_data in users_data:
            try:
                user = User(
                    id=user_data["id"],
                    email=user_data["email"],
                    hashed_password=user_data["hashed_password"],
                    created_at=current_time
                )
                db.add(user)
                db.flush()  # Flush after each user to catch potential errors early
                logger.info(f"User {user.email} inserted successfully!")
            except Exception as e:
                logger.error(f"Error inserting user {user_data['email']}: {str(e)}")
                db.rollback()
                raise
        db.commit()
        logger.info("All users inserted successfully!")

        # Insert profiles
        for profile_data in profiles_data:
            try:
                profile = UserProfile(
                    id=profile_data["id"],
                    user_id=profile_data["user_id"],
                    favorite_movie=profile_data["favorite_movie"],
                    favorite_book=profile_data["favorite_book"],
                    favorite_celebrities=profile_data["favorite_celebrities"],
                    learning_style=profile_data["learning_style"],
                    interests=profile_data["interests"],
                    created_at=current_time,
                    updated_at=current_time
                )
                db.add(profile)
                db.flush()  # Flush after each profile to catch potential errors early
                logger.info(f"Profile for user_id {profile.user_id} inserted successfully!")
            except Exception as e:
                logger.error(f"Error inserting profile for user_id {profile_data['user_id']}: {str(e)}")
                db.rollback()
                raise
        db.commit()
        logger.info("All profiles inserted successfully!")

        logger.info("Database seeded successfully!")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        logger.error("Failed to seed database")
        sys.exit(1)
    else:
        logger.info("Database seeding completed successfully")
        sys.exit(0) 