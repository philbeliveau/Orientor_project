#!/usr/bin/env python3
"""
Test script to verify database connection and check users table
"""
import os
import sys
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection using different methods"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print(f"🔍 Testing connection to: {database_url}")
    
    # Test 1: Direct psycopg2 connection
    try:
        print("\n📝 Test 1: Direct psycopg2 connection")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT current_database(), current_user, version();")
        db_name, user, version = cursor.fetchone()
        print(f"✅ Database: {db_name}")
        print(f"✅ User: {user}")
        print(f"✅ Version: {version[:50]}...")
        
        cursor.close()
        conn.close()
        print("✅ Direct psycopg2 connection successful!")
        
    except Exception as e:
        print(f"❌ Direct psycopg2 connection failed: {e}")
        return False
    
    # Test 2: SQLAlchemy engine
    try:
        print("\n📝 Test 2: SQLAlchemy engine")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            if test_result[0] == 1:
                print("✅ SQLAlchemy connection successful!")
            else:
                print("❌ SQLAlchemy test query failed")
                return False
                
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False
    
    return True

def check_users_table():
    """Check users table structure and existing users"""
    
    database_url = os.getenv("DATABASE_URL")
    
    try:
        print("\n📝 Checking users table...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if users table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if table_exists:
                print("✅ Users table exists")
                
                # Get table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position;
                """))
                columns = result.fetchall()
                
                print("\n📋 Users table structure:")
                for col_name, data_type, nullable in columns:
                    print(f"  - {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
                
                # Check existing users (safely)
                result = conn.execute(text("SELECT COUNT(*) FROM users;"))
                user_count = result.fetchone()[0]
                print(f"\n👥 Total users in database: {user_count}")
                
                if user_count > 0:
                    # Get first few users (without passwords)
                    result = conn.execute(text("""
                        SELECT id, email, created_at 
                        FROM users 
                        ORDER BY created_at DESC 
                        LIMIT 5;
                    """))
                    users = result.fetchall()
                    
                    print("\n📋 Recent users:")
                    for user_id, email, created_at in users:
                        print(f"  - ID: {user_id}, Email: {email}, Created: {created_at}")
                        
                else:
                    print("⚠️  No users found in database")
                
            else:
                print("❌ Users table does not exist")
                
                # List all tables
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"\n📋 Available tables: {tables}")
                
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Database Connection Test")
    print("=" * 50)
    
    # Test database connection
    if test_database_connection():
        print("\n" + "=" * 50)
        check_users_table()
    else:
        print("\n❌ Database connection failed - skipping table checks")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Database tests completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)