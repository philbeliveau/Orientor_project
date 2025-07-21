#!/usr/bin/env python3
"""
Fix the personality_assessments table to have proper auto-increment sequence
"""
import os
import sys
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_personality_assessments_sequence():
    """Fix the personality_assessments table to have proper auto-increment sequence"""
    
    # Get database URL
    DATABASE_URL = (
        os.getenv("DATABASE_URL") or 
        os.getenv("DATABASE_PRIVATE_URL") or 
        os.getenv("POSTGRES_URL") or
        os.getenv("RAILWAY_DATABASE_URL")
    )
    
    if not DATABASE_URL:
        logger.error("❌ No database URL found in environment variables")
        return False
    
    try:
        logger.info("🔧 Connecting to database...")
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            logger.info("🔍 Checking current table structure...")
            
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'personality_assessments'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.error("❌ personality_assessments table does not exist")
                return False
            
            logger.info("✅ Table exists, checking sequence...")
            
            # Check if sequence exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM pg_class 
                    WHERE relname = 'personality_assessments_id_seq' 
                    AND relkind = 'S'
                );
            """))
            sequence_exists = result.scalar()
            
            if sequence_exists:
                logger.info("✅ Sequence already exists, checking if it's properly linked...")
                
                # Check if column default is set
                result = conn.execute(text("""
                    SELECT column_default 
                    FROM information_schema.columns 
                    WHERE table_name = 'personality_assessments' 
                    AND column_name = 'id';
                """))
                default_value = result.scalar()
                
                if default_value and "personality_assessments_id_seq" in str(default_value):
                    logger.info("✅ Sequence is properly linked to id column")
                    
                    # Get current max ID to sync sequence
                    result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM personality_assessments;"))
                    max_id = result.scalar()
                    
                    if max_id > 0:
                        logger.info(f"🔄 Syncing sequence to start from {max_id + 1}")
                        conn.execute(text(f"SELECT setval('personality_assessments_id_seq', {max_id});"))
                        conn.commit()
                    
                    return True
                else:
                    logger.warning("⚠️ Sequence exists but not linked to column, fixing...")
            else:
                logger.info("🆕 Creating sequence...")
                
                # Get current max ID
                result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM personality_assessments;"))
                max_id = result.scalar()
                start_value = max_id + 1
                
                logger.info(f"📊 Current max ID: {max_id}, starting sequence at: {start_value}")
                
                # Create sequence
                conn.execute(text(f"""
                    CREATE SEQUENCE IF NOT EXISTS personality_assessments_id_seq 
                    START WITH {start_value} 
                    INCREMENT BY 1;
                """))
                
                logger.info("✅ Sequence created")
            
            # Set the default value for the id column
            logger.info("🔗 Linking sequence to id column...")
            conn.execute(text("""
                ALTER TABLE personality_assessments 
                ALTER COLUMN id SET DEFAULT nextval('personality_assessments_id_seq');
            """))
            
            # Make sure the sequence is owned by the column
            conn.execute(text("""
                ALTER SEQUENCE personality_assessments_id_seq 
                OWNED BY personality_assessments.id;
            """))
            
            # Commit all changes
            conn.commit()
            
            logger.info("✅ Successfully fixed personality_assessments sequence!")
            
            # Test the fix
            logger.info("🧪 Testing sequence functionality...")
            test_result = conn.execute(text("SELECT nextval('personality_assessments_id_seq');"))
            next_val = test_result.scalar()
            logger.info(f"✅ Next sequence value: {next_val}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error fixing sequence: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting personality_assessments sequence fix...")
    
    success = fix_personality_assessments_sequence()
    
    if success:
        logger.info("🎉 Database fix completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Database fix failed!")
        sys.exit(1)