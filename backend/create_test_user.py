#!/usr/bin/env python3
"""
Create a test user for login testing
"""
import os
import sys
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing context (same as in your app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Create a test user with known credentials"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    # Test user credentials
    test_email = "test@navigo.com"
    test_password = "testpassword123"
    
    try:
        print(f"🔍 Creating test user: {test_email}")
        
        # Hash the password
        hashed_password = pwd_context.hash(test_password)
        print(f"✅ Password hashed successfully")
        
        # Connect to database
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if user already exists
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": test_email}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"⚠️  User {test_email} already exists with ID: {existing_user[0]}")
                
                # Update the password
                conn.execute(
                    text("UPDATE users SET hashed_password = :password WHERE email = :email"),
                    {"password": hashed_password, "email": test_email}
                )
                conn.commit()
                print(f"✅ Updated password for existing user")
                
            else:
                # Create new user
                result = conn.execute(
                    text("""
                        INSERT INTO users (email, hashed_password, created_at) 
                        VALUES (:email, :password, :created_at)
                        RETURNING id
                    """),
                    {
                        "email": test_email,
                        "password": hashed_password,
                        "created_at": datetime.utcnow()
                    }
                )
                user_id = result.fetchone()[0]
                conn.commit()
                print(f"✅ Created new user with ID: {user_id}")
        
        print(f"\n🎯 Test Credentials:")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Hashed: {hashed_password[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

def verify_test_user():
    """Verify the test user can be authenticated"""
    
    database_url = os.getenv("DATABASE_URL")
    test_email = "test@navigo.com"
    test_password = "testpassword123"
    
    try:
        print(f"\n🔍 Verifying authentication for: {test_email}")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Get user from database
            result = conn.execute(
                text("SELECT id, email, hashed_password FROM users WHERE email = :email"),
                {"email": test_email}
            )
            user = result.fetchone()
            
            if not user:
                print(f"❌ User {test_email} not found in database")
                return False
            
            user_id, email, hashed_password = user
            print(f"✅ User found: ID={user_id}, Email={email}")
            
            # Verify password
            if pwd_context.verify(test_password, hashed_password):
                print(f"✅ Password verification successful!")
                return True
            else:
                print(f"❌ Password verification failed!")
                return False
                
    except Exception as e:
        print(f"❌ Error verifying test user: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Test User Creation")
    print("=" * 50)
    
    if create_test_user():
        print("\n" + "=" * 50)
        if verify_test_user():
            print("\n✅ Test user created and verified successfully!")
            print("\nYou can now test login with:")
            print("  Email: test@navigo.com")
            print("  Password: testpassword123")
            return True
        else:
            print("\n❌ Test user created but verification failed")
            return False
    else:
        print("\n❌ Failed to create test user")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)