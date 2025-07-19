#!/usr/bin/env python3
"""
Migrate data from Supabase to Railway PostgreSQL
Usage: python migrate_to_railway.py
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection_urls():
    """Get source (Supabase) and target (Railway) database URLs"""
    
    # Debug: Show what environment variables are available
    logger.info("🔍 Checking environment variables...")
    env_vars = [
        "DATABASE_URL", "SUPABASE_DATABASE_URL", "DATABASE_URL_SUPABASE",
        "RAILWAY_DATABASE_URL", "DATABASE_PRIVATE_URL", "POSTGRES_URL"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Hide password for logging
            import re
            safe_value = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', value)
            logger.info(f"  {var}: {safe_value}")
        else:
            logger.info(f"  {var}: Not set")
    
    # Supabase URL (source) - use DATABASE_URL if it points to Supabase
    database_url = os.getenv("DATABASE_URL")
    supabase_url = None
    
    if database_url and "supabase.co" in database_url:
        supabase_url = database_url
        logger.info("✅ Found Supabase URL in DATABASE_URL")
    else:
        supabase_url = (
            os.getenv("SUPABASE_DATABASE_URL") or 
            os.getenv("DATABASE_URL_SUPABASE") or
            os.getenv("SUPABASE_URL")
        )
    
    # Railway URL (target) - separate from Supabase URL
    railway_url = (
        os.getenv("RAILWAY_DATABASE_URL") or
        os.getenv("DATABASE_PRIVATE_URL") or 
        os.getenv("POSTGRES_URL")
    )
    
    # Don't use DATABASE_URL for Railway if it's Supabase
    if not railway_url and database_url and "supabase.co" not in database_url:
        railway_url = database_url
    
    # If no specific URLs found, prompt user
    if not supabase_url:
        logger.error("❌ No Supabase URL found!")
        logger.info("Please set one of: SUPABASE_DATABASE_URL, DATABASE_URL_SUPABASE, or SUPABASE_URL")
    
    if not railway_url:
        logger.error("❌ No Railway URL found!")
        logger.info("Please set one of: RAILWAY_DATABASE_URL, DATABASE_URL, DATABASE_PRIVATE_URL, or POSTGRES_URL")
    
    return supabase_url, railway_url

def connect_to_databases():
    """Create connections to both databases"""
    supabase_url, railway_url = get_connection_urls()
    
    if not supabase_url:
        logger.error("❌ Supabase DATABASE_URL not found!")
        logger.info("Set SUPABASE_DATABASE_URL environment variable")
        return None, None
    
    if not railway_url:
        logger.error("❌ Railway DATABASE_URL not found!")
        logger.info("Make sure Railway PostgreSQL is provisioned")
        return None, None
    
    try:
        # Connect to Supabase (source)
        logger.info("🔗 Connecting to Supabase...")
        supabase_engine = create_engine(supabase_url)
        with supabase_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Supabase connection successful")
        
        # Connect to Railway (target)
        logger.info("🔗 Connecting to Railway PostgreSQL...")
        railway_engine = create_engine(railway_url)
        with railway_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Railway PostgreSQL connection successful")
        
        return supabase_engine, railway_engine
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None, None

def get_table_schema(engine, table_name):
    """Get table schema from source database"""
    try:
        with engine.connect() as conn:
            # Get table structure
            result = conn.execute(text(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """), {"table_name": table_name})
            
            columns = result.fetchall()
            return columns
    except Exception as e:
        logger.error(f"❌ Failed to get table schema: {e}")
        return None

def create_table_sql(columns, table_name):
    """Generate CREATE TABLE SQL from column information"""
    if not columns:
        return None
    
    sql_parts = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
    
    for col in columns:
        col_name, data_type, is_nullable, default = col
        
        # Convert PostgreSQL data types
        pg_type = data_type.upper()
        if 'CHARACTER VARYING' in pg_type:
            pg_type = 'VARCHAR(255)'
        elif 'TIMESTAMP' in pg_type:
            pg_type = 'TIMESTAMP'
        elif 'INTEGER' in pg_type:
            pg_type = 'INTEGER'
        
        # Nullable constraint
        nullable = "" if is_nullable == "YES" else " NOT NULL"
        
        # Default value
        default_val = f" DEFAULT {default}" if default else ""
        
        sql_parts.append(f"    {col_name} {pg_type}{nullable}{default_val},")
    
    # Remove last comma and close
    sql_parts[-1] = sql_parts[-1].rstrip(',')
    sql_parts.append(");")
    
    return "\n".join(sql_parts)

def migrate_table_data(source_engine, target_engine, table_name):
    """Migrate data from source to target table"""
    try:
        logger.info(f"📊 Migrating data for table: {table_name}")
        
        # Get data from source
        with source_engine.connect() as source_conn:
            result = source_conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()
        
        if not rows:
            logger.info(f"ℹ️ No data found in {table_name}")
            return True
        
        logger.info(f"📦 Found {len(rows)} rows to migrate")
        
        # Insert data into target
        with target_engine.connect() as target_conn:
            # Clear existing data (optional)
            target_conn.execute(text(f"DELETE FROM {table_name}"))
            
            # Prepare INSERT statement
            placeholders = ", ".join([f":{col}" for col in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert rows
            for row in rows:
                row_dict = dict(zip(columns, row))
                target_conn.execute(text(insert_sql), row_dict)
            
            target_conn.commit()
        
        logger.info(f"✅ Successfully migrated {len(rows)} rows")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed for {table_name}: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting Supabase → Railway PostgreSQL migration")
    
    # Connect to databases
    supabase_engine, railway_engine = connect_to_databases()
    if not supabase_engine or not railway_engine:
        sys.exit(1)
    
    # Tables to migrate
    tables_to_migrate = ["users"]  # Add more tables as needed
    
    for table_name in tables_to_migrate:
        logger.info(f"\n📋 Processing table: {table_name}")
        
        # Get table schema
        columns = get_table_schema(supabase_engine, table_name)
        if not columns:
            logger.warning(f"⚠️ Could not get schema for {table_name}, skipping")
            continue
        
        # Create table in Railway
        create_sql = create_table_sql(columns, table_name)
        if create_sql:
            try:
                with railway_engine.connect() as conn:
                    conn.execute(text(create_sql))
                    conn.commit()
                logger.info(f"✅ Table {table_name} created in Railway")
            except Exception as e:
                logger.error(f"❌ Failed to create table {table_name}: {e}")
                continue
        
        # Migrate data
        success = migrate_table_data(supabase_engine, railway_engine, table_name)
        if not success:
            logger.error(f"❌ Failed to migrate data for {table_name}")
            continue
    
    logger.info("\n🎉 Migration completed!")
    logger.info("💡 Update your app to use Railway DATABASE_URL")

if __name__ == "__main__":
    main()