#!/usr/bin/env python3
"""
Login diagnostic script - tests authentication system
"""
import sys
sys.path.insert(0, '.')

from app.utils.database import get_db, initialize_database
from app.models import User
from passlib.context import CryptContext
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_hash():
    """Test password hashing and verification"""
    test_password = "testpass123"
    
    # Hash the password
    hashed = pwd_context.hash(test_password)
    logger.info(f"Hashed password: {hashed}")
    
    # Verify the password
    is_valid = pwd_context.verify(test_password, hashed)
    logger.info(f"Password verification: {is_valid}")
    
    return is_valid

def check_existing_users():
    """Check existing users and their passwords"""
    try:
        initialize_database()
        db = next(get_db())
        
        users = db.query(User).limit(5).all()
        logger.info(f"Found {len(users)} users in database")
        
        for user in users:
            logger.info(f"User: {user.email} (ID: {user.id})")
            
            # Try to verify with common passwords
            test_passwords = ["testpass123", "password", "123456", "testpass"]
            for test_pwd in test_passwords:
                if pwd_context.verify(test_pwd, user.hashed_password):
                    logger.info(f"✅ Password '{test_pwd}' works for {user.email}")
                    break
            else:
                logger.warning(f"❌ None of the test passwords work for {user.email}")
                
    except Exception as e:
        logger.error(f"Error checking users: {e}")
        
def create_test_user():
    """Create a test user with known credentials"""
    try:
        initialize_database()
        db = next(get_db())
        
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "testlogin@example.com").first()
        if existing_user:
            logger.info("Test user already exists, deleting...")
            db.delete(existing_user)
            db.commit()
        
        # Create test user
        hashed_password = pwd_context.hash("testpass123")
        test_user = User(
            email="testlogin@example.com",
            hashed_password=hashed_password
        )
        
        db.add(test_user)
        db.commit()
        logger.info(f"✅ Created test user: testlogin@example.com with password: testpass123")
        
    except Exception as e:
        logger.error(f"Error creating test user: {e}")

def main():
    """Run all diagnostic tests"""
    logger.info("🔍 Starting login diagnostic tests...")
    
    # Test 1: Password hashing
    logger.info("1. Testing password hashing...")
    test_password_hash()
    
    # Test 2: Check existing users
    logger.info("2. Checking existing users...")
    check_existing_users()
    
    # Test 3: Create test user
    logger.info("3. Creating test user...")
    create_test_user()
    
    logger.info("✅ Diagnostic tests completed!")
    logger.info("Try logging in with:")
    logger.info("  Email: testlogin@example.com")
    logger.info("  Password: testpass123")

if __name__ == "__main__":
    main()