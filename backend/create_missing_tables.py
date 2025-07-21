#!/usr/bin/env python3
"""
Create missing database tables for Railway deployment
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def create_user_profiles_table():
    """Create the user_profiles table if it doesn't exist"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
        
    try:
        # Fix for Railway/Heroku SSL issue
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        if '?sslmode=' not in database_url:
            database_url += '?sslmode=require'
            
        print("🔧 Connecting to database...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if user_profiles table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_profiles'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if table_exists:
                print("✅ user_profiles table already exists")
                return True
            
            print("🔧 Creating user_profiles table...")
            
            # Create user_profiles table
            conn.execute(text("""
                CREATE TABLE user_profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR,
                    age INTEGER,
                    sex VARCHAR(50),
                    major VARCHAR,
                    year INTEGER,
                    gpa FLOAT,
                    hobbies TEXT,
                    country VARCHAR(255),
                    state_province VARCHAR(255),
                    unique_quality TEXT,
                    story TEXT,
                    favorite_movie VARCHAR(255),
                    favorite_book VARCHAR(255),
                    favorite_celebrities TEXT,
                    learning_style VARCHAR(50),
                    interests TEXT,
                    job_title VARCHAR,
                    industry VARCHAR,
                    years_experience INTEGER,
                    education_level VARCHAR,
                    career_goals VARCHAR,
                    skills VARCHAR[],
                    personal_analysis TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    UNIQUE(user_id)
                );
            """))
            
            # Create index for user_id
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
            """))
            
            # Create updated_at trigger
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """))
            
            conn.execute(text("""
                CREATE TRIGGER update_user_profiles_updated_at 
                BEFORE UPDATE ON user_profiles 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """))
            
            conn.commit()
            print("✅ user_profiles table created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error creating user_profiles table: {e}")
        return False

def create_other_missing_tables():
    """Create other potentially missing tables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return False
        
    try:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        if '?sslmode=' not in database_url:
            database_url += '?sslmode=require'
            
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check and create user_skills table if needed
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_skills'
                );
            """))
            
            if not result.fetchone()[0]:
                print("🔧 Creating user_skills table...")
                conn.execute(text("""
                    CREATE TABLE user_skills (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        creativity INTEGER DEFAULT 0,
                        leadership INTEGER DEFAULT 0,
                        digital_literacy INTEGER DEFAULT 0,
                        critical_thinking INTEGER DEFAULT 0,
                        problem_solving INTEGER DEFAULT 0,
                        analytical_thinking INTEGER DEFAULT 0,
                        attention_to_detail INTEGER DEFAULT 0,
                        collaboration INTEGER DEFAULT 0,
                        adaptability INTEGER DEFAULT 0,
                        independence INTEGER DEFAULT 0,
                        evaluation INTEGER DEFAULT 0,
                        decision_making INTEGER DEFAULT 0,
                        stress_tolerance INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                        UNIQUE(user_id)
                    );
                """))
                print("✅ user_skills table created")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"❌ Error creating additional tables: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Creating missing database tables...")
    
    success1 = create_user_profiles_table()
    success2 = create_other_missing_tables()
    
    if success1 and success2:
        print("✅ All missing tables created successfully")
        sys.exit(0)
    else:
        print("❌ Failed to create some tables")
        sys.exit(1)