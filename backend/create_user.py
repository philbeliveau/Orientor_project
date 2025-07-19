#!/usr/bin/env python3
"""
Create a simple users table and add your user
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_users_table():
    """Create a simple users table in Railway PostgreSQL"""
    
    # Use the actual Railway URL (not Supabase)
    railway_url = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"
    if not railway_url:
        print("❌ No database URL found!")
        print("Need RAILWAY_DATABASE_URL or DATABASE_URL")
        sys.exit(1)
    
    print(f"🔗 Connecting to Railway PostgreSQL...")
    # Hide password in logs
    import re
    safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', railway_url)
    print(f"   URL: {safe_url}")
    
    try:
        engine = create_engine(railway_url)
        
        with engine.connect() as conn:
            # Check if users table exists
            print("🔍 Checking existing tables...")
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Existing tables: {tables}")
            
            if 'users' not in tables:
                # Create new users table
                print("🔄 Creating users table...")
                conn.execute(text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """))
            else:
                print("✅ Users table already exists")
                # Check structure
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                """))
                columns = result.fetchall()
                print(f"📋 Users table columns: {[col[0] for col in columns]}")
            
            # Add your user (handle if already exists)
            print("👤 Adding your user...")
            try:
                conn.execute(text("""
                    INSERT INTO users (email, password, name) 
                    VALUES (:email, :password, :name)
                """), {
                    "email": "beli5@example.com",
                    "password": "navigo_123", 
                    "name": "Beli"
                })
                print("✅ Added beli5@example.com")
            except Exception as e:
                if "duplicate" in str(e).lower():
                    print("ℹ️ User beli5@example.com already exists")
                else:
                    print(f"⚠️ Error adding user: {e}")
            
            # Add test user
            try:
                conn.execute(text("""
                    INSERT INTO users (email, password, name) 
                    VALUES (:email, :password, :name)
                """), {
                    "email": "test@example.com",
                    "password": "password123",
                    "name": "Test User"
                })
                print("✅ Added test@example.com")
            except Exception as e:
                if "duplicate" in str(e).lower():
                    print("ℹ️ User test@example.com already exists")
                else:
                    print(f"⚠️ Error adding test user: {e}")
            
            conn.commit()
            
            # Verify
            result = conn.execute(text("SELECT email, name FROM users"))
            users = result.fetchall()
            
            print("✅ Users table created successfully!")
            print("👥 Users in database:")
            for user in users:
                print(f"   - {user[0]} ({user[1]})")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_users_table()