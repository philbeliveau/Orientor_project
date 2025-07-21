#!/usr/bin/env python3
"""
Check and fix all auto-increment sequences for personality profile tables
"""
import os
import sys
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_fix_sequence(conn, table_name, id_column='id'):
    """Check and fix sequence for a specific table"""
    logger.info(f"🔍 Checking {table_name}...")
    
    # Check if table exists
    result = conn.execute(text(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = '{table_name}'
        );
    """))
    table_exists = result.scalar()
    
    if not table_exists:
        logger.warning(f"⚠️ {table_name} table does not exist")
        return True  # Not an error if table doesn't exist
    
    sequence_name = f"{table_name}_{id_column}_seq"
    
    # Check if sequence exists
    result = conn.execute(text(f"""
        SELECT EXISTS (
            SELECT FROM pg_class 
            WHERE relname = '{sequence_name}' 
            AND relkind = 'S'
        );
    """))
    sequence_exists = result.scalar()
    
    if not sequence_exists:
        logger.info(f"🆕 Creating sequence for {table_name}...")
        
        # Get current max ID
        result = conn.execute(text(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table_name};"))
        max_id = result.scalar()
        start_value = max_id + 1
        
        logger.info(f"📊 {table_name} max ID: {max_id}, starting sequence at: {start_value}")
        
        # Create sequence
        conn.execute(text(f"""
            CREATE SEQUENCE IF NOT EXISTS {sequence_name} 
            START WITH {start_value} 
            INCREMENT BY 1;
        """))
        
        # Set the default value for the id column
        conn.execute(text(f"""
            ALTER TABLE {table_name} 
            ALTER COLUMN {id_column} SET DEFAULT nextval('{sequence_name}');
        """))
        
        # Make sure the sequence is owned by the column
        conn.execute(text(f"""
            ALTER SEQUENCE {sequence_name} 
            OWNED BY {table_name}.{id_column};
        """))
        
        logger.info(f"✅ Created sequence for {table_name}")
    else:
        # Check if column default is set
        result = conn.execute(text(f"""
            SELECT column_default 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_name = '{id_column}';
        """))
        default_value = result.scalar()
        
        if default_value and sequence_name in str(default_value):
            logger.info(f"✅ {table_name} sequence already properly configured")
        else:
            logger.info(f"🔗 Linking sequence to {table_name}.{id_column}...")
            conn.execute(text(f"""
                ALTER TABLE {table_name} 
                ALTER COLUMN {id_column} SET DEFAULT nextval('{sequence_name}');
            """))
    
    return True

def check_all_sequences():
    """Check and fix all sequences for personality profile tables"""
    
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
            # Tables to check
            tables_to_check = [
                'personality_assessments',
                'personality_responses',
                'personality_profiles'
            ]
            
            for table_name in tables_to_check:
                success = check_and_fix_sequence(conn, table_name)
                if not success:
                    return False
            
            # Commit all changes
            conn.commit()
            
            logger.info("✅ All sequences checked and fixed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking sequences: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting sequence check for all personality tables...")
    
    success = check_all_sequences()
    
    if success:
        logger.info("🎉 All database sequences are properly configured!")
        sys.exit(0)
    else:
        logger.error("💥 Database sequence check failed!")
        sys.exit(1)