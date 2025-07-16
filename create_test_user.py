#!/usr/bin/env python3
"""
Create a test user that already has onboarding completed
"""
import os
import sys
import logging
from datetime import datetime
import uuid
import json

# Clear any Railway environment variables
for key in list(os.environ.keys()):
    if 'RAILWAY' in key:
        del os.environ[key]

# Set correct local database configuration
os.environ['DATABASE_URL'] = 'postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local'
os.environ['ENV'] = 'development'

# Now import after setting environment variables
sys.path.insert(0, './backend')
from app.models import User, UserProfile
from app.models.personality_profiles import PersonalityAssessment, PersonalityProfile
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine directly
DATABASE_URL = 'postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_user_with_onboarding_complete():
    """Create a test user that already has onboarding completed"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        db = SessionLocal()
        
        # Test user data
        email = "user_no_onboarding@example.com"
        password = "testpass123"
        
        logger.info(f"Creating user with completed onboarding: {email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logger.info("User already exists, deleting first...")
            db.delete(existing_user)
            db.commit()
        
        # Hash password
        hashed_password = pwd_context.hash(password)
        
        # Create user
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.flush()
        logger.info(f"User created with ID: {db_user.id}")
        
        # Create user profile
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
        db.flush()
        logger.info(f"User profile created for user ID: {db_user.id}")
        
        # Create a completed assessment
        assessment = PersonalityAssessment(
            user_id=db_user.id,
            assessment_type="onboarding",
            assessment_version="v1.0",
            session_id=uuid.uuid4(),
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_items=1,
            completed_items=1
        )
        
        db.add(assessment)
        db.flush()
        logger.info(f"Assessment created with ID: {assessment.id}")
        
        # Create a personality profile
        personality_profile = PersonalityProfile(
            user_id=db_user.id,
            assessment_id=assessment.id,
            profile_type="onboarding",
            scores={
                "hexaco": {
                    "honesty": 0.7,
                    "emotionality": 0.4,
                    "extraversion": 0.6,
                    "agreeableness": 0.8,
                    "conscientiousness": 0.9,
                    "openness": 0.7
                },
                "riasec": {
                    "realistic": 0.3,
                    "investigative": 0.8,
                    "artistic": 0.6,
                    "social": 0.7,
                    "enterprising": 0.5,
                    "conventional": 0.4
                },
                "topTraits": ["Conscientious", "Investigative", "Agreeable"]
            },
            narrative_description="This is a test user with a completed onboarding profile. They show high conscientiousness and agreeableness.",
            assessment_version="v1.0",
            computed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(personality_profile)
        db.commit()
        logger.info(f"Personality profile created for user ID: {db_user.id}")
        
        logger.info("✅ User with completed onboarding created successfully!")
        logger.info(f"📧 Email: {email}")
        logger.info(f"🔑 Password: {password}")
        logger.info(f"👤 User ID: {db_user.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_user_with_onboarding_complete()
    if success:
        print("\n🎉 Test user created successfully!")
        print("You can now login with:")
        print("  Email: user_no_onboarding@example.com")
        print("  Password: testpass123")
        print("This user should go directly to dashboard without onboarding.")
    else:
        print("❌ Failed to create test user")
    sys.exit(0 if success else 1)