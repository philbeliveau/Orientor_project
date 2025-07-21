#!/usr/bin/env python3
"""
Migrate user_profiles data from Supabase to Railway PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_user_profiles():
    """Migrate user_profiles table from Supabase to Railway"""
    
    # Source (Supabase) connection
    supabase_url = "postgresql://postgres:Supabase.phil.007@db.tyhcruhmrfvtcinofupn.supabase.co:5432/postgres"
    
    # Target (Railway) connection
    railway_url = os.getenv('DATABASE_URL')
    if not railway_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return False
        
    # Fix Railway URL for SSL
    if railway_url.startswith('postgres://'):
        railway_url = railway_url.replace('postgres://', 'postgresql://', 1)
    if '?sslmode=' not in railway_url:
        railway_url += '?sslmode=require'
    
    try:
        logger.info("🔗 Connecting to Supabase...")
        supabase_engine = create_engine(supabase_url)
        
        logger.info("🔗 Connecting to Railway...")
        railway_engine = create_engine(railway_url)
        
        # First, create the user_profiles table if it doesn't exist
        with railway_engine.connect() as railway_conn:
            # Check if table exists
            result = railway_conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_profiles'
                );
            """))
            
            if not result.fetchone()[0]:
                logger.info("📋 Creating user_profiles table on Railway...")
                railway_conn.execute(text("""
                    CREATE TABLE user_profiles (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
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
                railway_conn.commit()
                logger.info("✅ user_profiles table created")
            else:
                logger.info("✅ user_profiles table already exists")
        
        # Fetch data from Supabase
        with supabase_engine.connect() as supabase_conn:
            logger.info("📊 Fetching user_profiles data from Supabase...")
            
            result = supabase_conn.execute(text("""
                SELECT 
                    user_id, name, age, sex, major, year, gpa, hobbies,
                    country, state_province, unique_quality, story,
                    favorite_movie, favorite_book, favorite_celebrities,
                    learning_style, interests, job_title, industry,
                    years_experience, education_level, career_goals,
                    skills, personal_analysis, created_at, updated_at
                FROM user_profiles
                ORDER BY id
            """))
            
            profiles = result.fetchall()
            logger.info(f"📊 Found {len(profiles)} user profiles to migrate")
            
            if not profiles:
                logger.info("ℹ️ No user profiles to migrate")
                return True
        
        # Insert data into Railway
        with railway_engine.connect() as railway_conn:
            logger.info("📤 Migrating user profiles to Railway...")
            
            migrated_count = 0
            skipped_count = 0
            
            for profile in profiles:
                try:
                    # Check if profile already exists
                    existing = railway_conn.execute(text("""
                        SELECT id FROM user_profiles WHERE user_id = :user_id
                    """), {"user_id": profile.user_id}).fetchone()
                    
                    if existing:
                        logger.debug(f"⚠️ Profile for user_id {profile.user_id} already exists, skipping")
                        skipped_count += 1
                        continue
                    
                    # Insert the profile
                    railway_conn.execute(text("""
                        INSERT INTO user_profiles (
                            user_id, name, age, sex, major, year, gpa, hobbies,
                            country, state_province, unique_quality, story,
                            favorite_movie, favorite_book, favorite_celebrities,
                            learning_style, interests, job_title, industry,
                            years_experience, education_level, career_goals,
                            skills, personal_analysis, created_at, updated_at
                        ) VALUES (
                            :user_id, :name, :age, :sex, :major, :year, :gpa, :hobbies,
                            :country, :state_province, :unique_quality, :story,
                            :favorite_movie, :favorite_book, :favorite_celebrities,
                            :learning_style, :interests, :job_title, :industry,
                            :years_experience, :education_level, :career_goals,
                            :skills, :personal_analysis, :created_at, :updated_at
                        )
                    """), {
                        "user_id": profile.user_id,
                        "name": profile.name,
                        "age": profile.age,
                        "sex": profile.sex,
                        "major": profile.major,
                        "year": profile.year,
                        "gpa": profile.gpa,
                        "hobbies": profile.hobbies,
                        "country": profile.country,
                        "state_province": profile.state_province,
                        "unique_quality": profile.unique_quality,
                        "story": profile.story,
                        "favorite_movie": profile.favorite_movie,
                        "favorite_book": profile.favorite_book,
                        "favorite_celebrities": profile.favorite_celebrities,
                        "learning_style": profile.learning_style,
                        "interests": profile.interests,
                        "job_title": profile.job_title,
                        "industry": profile.industry,
                        "years_experience": profile.years_experience,
                        "education_level": profile.education_level,
                        "career_goals": profile.career_goals,
                        "skills": profile.skills,
                        "personal_analysis": profile.personal_analysis,
                        "created_at": profile.created_at,
                        "updated_at": profile.updated_at
                    })
                    
                    migrated_count += 1
                    logger.debug(f"✅ Migrated profile for user_id {profile.user_id}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to migrate profile for user_id {profile.user_id}: {e}")
                    continue
            
            railway_conn.commit()
            
            logger.info(f"✅ Migration complete:")
            logger.info(f"   📊 Migrated: {migrated_count} profiles")
            logger.info(f"   ⚠️ Skipped: {skipped_count} profiles (already exist)")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def migrate_user_skills():
    """Also migrate user_skills table if it exists"""
    
    # Source (Supabase) connection
    supabase_url = "postgresql://postgres:Supabase.phil.007@db.tyhcruhmrfvtcinofupn.supabase.co:5432/postgres"
    
    # Target (Railway) connection
    railway_url = os.getenv('DATABASE_URL')
    if not railway_url:
        return False
        
    # Fix Railway URL for SSL
    if railway_url.startswith('postgres://'):
        railway_url = railway_url.replace('postgres://', 'postgresql://', 1)
    if '?sslmode=' not in railway_url:
        railway_url += '?sslmode=require'
    
    try:
        supabase_engine = create_engine(supabase_url)
        railway_engine = create_engine(railway_url)
        
        # Check if user_skills exists in Supabase
        with supabase_engine.connect() as supabase_conn:
            result = supabase_conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_skills'
                );
            """))
            
            if not result.fetchone()[0]:
                logger.info("ℹ️ user_skills table doesn't exist in Supabase, skipping")
                return True
        
        # Create user_skills table in Railway if needed
        with railway_engine.connect() as railway_conn:
            result = railway_conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_skills'
                );
            """))
            
            if not result.fetchone()[0]:
                logger.info("📋 Creating user_skills table on Railway...")
                railway_conn.execute(text("""
                    CREATE TABLE user_skills (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
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
                railway_conn.commit()
                logger.info("✅ user_skills table created")
        
        # Fetch and migrate user_skills data
        with supabase_engine.connect() as supabase_conn:
            logger.info("📊 Fetching user_skills data from Supabase...")
            
            result = supabase_conn.execute(text("""
                SELECT 
                    user_id, creativity, leadership, digital_literacy,
                    critical_thinking, problem_solving, analytical_thinking,
                    attention_to_detail, collaboration, adaptability,
                    independence, evaluation, decision_making, stress_tolerance,
                    created_at, updated_at
                FROM user_skills
                ORDER BY id
            """))
            
            skills = result.fetchall()
            logger.info(f"📊 Found {len(skills)} user skills to migrate")
            
            if not skills:
                logger.info("ℹ️ No user skills to migrate")
                return True
        
        # Insert skills into Railway
        with railway_engine.connect() as railway_conn:
            migrated_count = 0
            
            for skill in skills:
                try:
                    # Check if skills already exist
                    existing = railway_conn.execute(text("""
                        SELECT id FROM user_skills WHERE user_id = :user_id
                    """), {"user_id": skill.user_id}).fetchone()
                    
                    if existing:
                        continue
                    
                    # Insert the skills
                    railway_conn.execute(text("""
                        INSERT INTO user_skills (
                            user_id, creativity, leadership, digital_literacy,
                            critical_thinking, problem_solving, analytical_thinking,
                            attention_to_detail, collaboration, adaptability,
                            independence, evaluation, decision_making, stress_tolerance,
                            created_at, updated_at
                        ) VALUES (
                            :user_id, :creativity, :leadership, :digital_literacy,
                            :critical_thinking, :problem_solving, :analytical_thinking,
                            :attention_to_detail, :collaboration, :adaptability,
                            :independence, :evaluation, :decision_making, :stress_tolerance,
                            :created_at, :updated_at
                        )
                    """), {
                        "user_id": skill.user_id,
                        "creativity": skill.creativity,
                        "leadership": skill.leadership,
                        "digital_literacy": skill.digital_literacy,
                        "critical_thinking": skill.critical_thinking,
                        "problem_solving": skill.problem_solving,
                        "analytical_thinking": skill.analytical_thinking,
                        "attention_to_detail": skill.attention_to_detail,
                        "collaboration": skill.collaboration,
                        "adaptability": skill.adaptability,
                        "independence": skill.independence,
                        "evaluation": skill.evaluation,
                        "decision_making": skill.decision_making,
                        "stress_tolerance": skill.stress_tolerance,
                        "created_at": skill.created_at,
                        "updated_at": skill.updated_at
                    })
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to migrate skills for user_id {skill.user_id}: {e}")
                    continue
            
            railway_conn.commit()
            logger.info(f"✅ Migrated {migrated_count} user skills records")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ User skills migration failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting user profiles migration from Supabase to Railway...")
    
    success1 = migrate_user_profiles()
    success2 = migrate_user_skills()
    
    if success1 and success2:
        print("✅ Migration completed successfully")
        sys.exit(0)
    else:
        print("❌ Migration failed")
        sys.exit(1)