#!/usr/bin/env python3
import os
import sys
import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Clear any Railway environment variables
for key in list(os.environ.keys()):
    if 'RAILWAY' in key:
        del os.environ[key]

# Set correct local database configuration
os.environ['DATABASE_URL'] = 'postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local'
os.environ['ENV'] = 'development'

# Now import after setting environment variables
sys.path.insert(0, '.')
from app.models import User, UserProfile
from app.schemas.user import UserCreate
from passlib.context import CryptContext
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create database engine directly
DATABASE_URL = 'postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test registration
def test_registration():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        db = SessionLocal()
        
        # Test user data
        user_data = UserCreate(
            email="test_debug@example.com",
            password="testpass123"
        )
        
        logger.info(f"Testing registration for: {user_data.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.info("User already exists, deleting first...")
            db.delete(existing_user)
            db.commit()
        
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        logger.info("Password hashed successfully")
        
        # Create user
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.flush()
        logger.info(f"User created with ID: {db_user.id}")
        
        # Create profile
        user_profile = UserProfile(
            user_id=db_user.id,
            favorite_movie="",
            favorite_book="",
            favorite_celebrities="",
            learning_style="",
            interests="",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user_profile)
        db.commit()
        logger.info(f"Profile created for user ID: {db_user.id}")
        
        logger.info("Registration test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_registration()
    sys.exit(0 if success else 1)