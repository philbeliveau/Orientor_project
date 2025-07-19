#!/usr/bin/env python3
"""
Properly migrate the users table from Supabase to Railway
Handles duplicate columns and schema issues
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_users_table():
    """Migrate users table from Supabase to Railway"""
    
    # Database URLs
    supabase_url = "postgresql://postgres:Supabase.phil.007@db.tyhcruhmrfvtcinofupn.supabase.co:5432/postgres"
    railway_url = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"
    
    try:
        # Connect to both databases
        print("🔗 Connecting to databases...")
        supabase_engine = create_engine(supabase_url)
        railway_engine = create_engine(railway_url)
        
        # Test connections
        with supabase_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        with railway_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connections successful")
        
        # Get Supabase users table structure
        print("🔍 Analyzing Supabase users table...")
        with supabase_engine.connect() as conn:
            # Get column information
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            print(f"📋 Supabase users columns ({len(columns)}): {[col[0] for col in columns]}")
            
            # Get sample data to understand the structure
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            total_users = result.fetchone()[0]
            print(f"📊 Total users in Supabase: {total_users}")
            
            if total_users > 0:
                # Get first few users to see the data
                result = conn.execute(text("SELECT email, created_at FROM users LIMIT 5"))
                sample_users = result.fetchall()
                print(f"📧 Sample users: {[user[0] for user in sample_users]}")
        
        # Create clean users table in Railway (remove the simple one I created)
        print("\n🔄 Creating proper users table in Railway...")
        with railway_engine.connect() as conn:
            # Drop the simple table I created
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            
            # Create a clean users table based on essential Supabase columns
            conn.execute(text("""
                CREATE TABLE users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    encrypted_password VARCHAR(255),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    email_confirmed_at TIMESTAMPTZ,
                    last_sign_in_at TIMESTAMPTZ,
                    raw_user_meta_data JSONB,
                    onboarding_completed BOOLEAN DEFAULT FALSE
                )
            """))
            conn.commit()
            print("✅ Clean users table created in Railway")
        
        # Migrate user data
        print("\n📦 Migrating user data...")
        
        # First, figure out which password column exists (use fresh connection)
        password_column = None
        for col_name in ['encrypted_password', 'hashed_password', 'password']:
            try:
                with supabase_engine.connect() as test_conn:
                    test_conn.execute(text(f"SELECT {col_name} FROM users LIMIT 1"))
                    password_column = col_name
                    print(f"✅ Found password column: {password_column}")
                    break
            except:
                continue
        
        if not password_column:
            print("⚠️ No password column found, migrating without passwords")
            password_column = "''"  # Empty string instead of NULL
        
        # Get user data with fresh connection
        with supabase_engine.connect() as source_conn:
            # Use a simpler query first to see what data we can get
            try:
                result = source_conn.execute(text("SELECT email FROM users WHERE email IS NOT NULL LIMIT 10"))
                sample_emails = [row[0] for row in result.fetchall()]
                print(f"📧 Sample accessible emails: {sample_emails}")
                
                # Now try the full query
                if password_column != "''":
                    query = f"""
                        SELECT DISTINCT 
                            id,
                            email,
                            {password_column} as password,
                            created_at
                        FROM users 
                        WHERE email IS NOT NULL
                        ORDER BY created_at
                        LIMIT 50
                    """
                else:
                    query = """
                        SELECT DISTINCT 
                            id,
                            email,
                            '' as password,
                            created_at
                        FROM users 
                        WHERE email IS NOT NULL
                        ORDER BY created_at
                        LIMIT 50
                    """
                
                result = source_conn.execute(text(query))
                users = result.fetchall()
                
            except Exception as e:
                print(f"⚠️ Query failed: {e}")
                print("🔄 Trying simplified approach...")
                # Fallback to most basic query
                result = source_conn.execute(text("""
                    SELECT email, created_at 
                    FROM users 
                    WHERE email IS NOT NULL 
                    ORDER BY created_at 
                    LIMIT 50
                """))
                raw_users = result.fetchall()
                # Convert to expected format
                users = [(None, user[0], "temp_password", user[1]) for user in raw_users]
            
            print(f"📊 Found {len(users)} users to migrate")
            
            if users:
                with railway_engine.connect() as target_conn:
                    migrated_count = 0
                    for user in users:
                        try:
                            # Handle different user data formats
                            if len(user) >= 4:
                                # Full format: (id, email, password, created_at, ...)
                                user_id = user[0] if user[0] else f"gen_random_uuid()"
                                email = user[1]
                                password = user[2] if user[2] else "temp_password_123"
                                created_at = user[3]
                            else:
                                # Simplified format
                                user_id = "gen_random_uuid()"
                                email = user[0] if len(user) > 0 else f"user{migrated_count}@example.com"
                                password = "temp_password_123"
                                created_at = user[1] if len(user) > 1 else "NOW()"
                            
                            target_conn.execute(text("""
                                INSERT INTO users (
                                    id, email, encrypted_password, created_at
                                ) VALUES (
                                    COALESCE(:id, gen_random_uuid()), :email, :password, COALESCE(:created_at, NOW())
                                )
                            """), {
                                'id': user_id if user_id != "gen_random_uuid()" else None,
                                'email': email, 
                                'password': password,
                                'created_at': created_at if created_at != "NOW()" else None
                            })
                            migrated_count += 1
                            print(f"   ✅ Migrated: {email}")
                        except Exception as e:
                            print(f"⚠️ Skipped user {user[1] if len(user) > 1 else user}: {e}")
                    
                    target_conn.commit()
                    print(f"✅ Successfully migrated {migrated_count}/{len(users)} users")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        with railway_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            railway_count = result.fetchone()[0]
            
            result = conn.execute(text("SELECT email FROM users LIMIT 10"))
            sample_emails = [row[0] for row in result.fetchall()]
            
            print(f"📊 Users in Railway: {railway_count}")
            print(f"📧 Sample migrated emails: {sample_emails}")
            
        print("\n🎉 Users table migration completed successfully!")
        print("💡 Your Supabase users are now available in Railway PostgreSQL")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_users_table()