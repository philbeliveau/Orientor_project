#!/usr/bin/env python3
"""
Debug Railway database users
"""

import os
from sqlalchemy import create_engine, text

def check_railway_users():
    """Check what users exist in Railway database"""
    
    railway_url = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"
    
    try:
        engine = create_engine(railway_url)
        
        with engine.connect() as conn:
            print("🔍 Checking Railway database users...")
            
            # Check if users table exists
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema='public' AND table_name='users'
            """))
            tables = result.fetchall()
            print(f"📋 Users table exists: {len(tables) > 0}")
            
            if len(tables) > 0:
                # Get table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print(f"📊 Table columns: {[col[0] for col in columns]}")
                
                # Count users
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.fetchone()[0]
                print(f"👥 Total users: {count}")
                
                # Show sample users
                if count > 0:
                    result = conn.execute(text("SELECT email, encrypted_password FROM users LIMIT 5"))
                    users = result.fetchall()
                    print(f"📧 Sample users:")
                    for user in users:
                        email = user[0]
                        has_password = bool(user[1])
                        print(f"   - {email} (password: {'✅' if has_password else '❌'})")
                
                # Check specific user
                result = conn.execute(text("SELECT email, encrypted_password FROM users WHERE email IN ('beli5@example.com', 'beli@example.com')"))
                target_users = result.fetchall()
                print(f"🎯 Target users found: {len(target_users)}")
                for user in target_users:
                    print(f"   - {user[0]}: password hash = {user[1][:20] if user[1] else 'None'}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_railway_users()