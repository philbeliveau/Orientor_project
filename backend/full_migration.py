#!/usr/bin/env python3
"""
Complete Supabase to Railway PostgreSQL migration
Migrates ALL tables with proper schema handling
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_tables(engine):
    """Get all table names from the database"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
        return tables
    except Exception as e:
        logger.error(f"❌ Failed to get table list: {e}")
        return []

def dump_table_schema(source_engine, table_name):
    """Get the CREATE TABLE statement for a table"""
    try:
        with source_engine.connect() as conn:
            # Get detailed column information
            result = conn.execute(text(f"""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            # Build CREATE TABLE statement
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            column_definitions = []
            
            for col in columns:
                col_name, data_type, max_length, is_nullable, default = col
                
                # Convert data types
                pg_type = data_type.upper()
                if pg_type == 'CHARACTER VARYING':
                    pg_type = f'VARCHAR({max_length})' if max_length else 'VARCHAR(255)'
                elif pg_type == 'USER-DEFINED':
                    pg_type = 'TEXT'  # Handle custom types as TEXT
                elif pg_type == 'TIMESTAMP WITHOUT TIME ZONE':
                    pg_type = 'TIMESTAMP'
                elif pg_type == 'TIMESTAMP WITH TIME ZONE':
                    pg_type = 'TIMESTAMPTZ'
                
                # Handle nullable
                nullable = "" if is_nullable == "YES" else " NOT NULL"
                
                # Handle defaults (be careful with complex defaults)
                default_clause = ""
                if default and not default.startswith("nextval("):
                    if "'" in default or default.lower() in ['now()', 'false', 'true']:
                        default_clause = f" DEFAULT {default}"
                
                column_def = f"    {col_name} {pg_type}{nullable}{default_clause}"
                column_definitions.append(column_def)
            
            create_sql += ",\n".join(column_definitions)
            create_sql += "\n);"
            
            return create_sql
            
    except Exception as e:
        logger.error(f"❌ Failed to dump schema for {table_name}: {e}")
        return None

def migrate_table_data_safely(source_engine, target_engine, table_name):
    """Migrate table data with error handling"""
    try:
        logger.info(f"📊 Migrating data for: {table_name}")
        
        # Get column names from target table (in case some columns were skipped)
        target_inspector = inspect(target_engine)
        target_columns = [col['name'] for col in target_inspector.get_columns(table_name)]
        
        # Get data from source table
        with source_engine.connect() as source_conn:
            # Only select columns that exist in target
            columns_str = ", ".join(target_columns)
            result = source_conn.execute(text(f"SELECT {columns_str} FROM {table_name}"))
            rows = result.fetchall()
        
        if not rows:
            logger.info(f"ℹ️ No data in {table_name}")
            return True
        
        logger.info(f"📦 Migrating {len(rows)} rows...")
        
        # Insert data in batches
        batch_size = 100
        with target_engine.connect() as target_conn:
            # Clear existing data
            target_conn.execute(text(f"DELETE FROM {table_name}"))
            
            # Insert in batches
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                
                # Prepare batch insert
                placeholders = ", ".join([f":{col}" for col in target_columns])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(target_columns)}) VALUES ({placeholders})"
                
                for row in batch:
                    row_dict = dict(zip(target_columns, row))
                    target_conn.execute(text(insert_sql), row_dict)
                
                logger.info(f"  ✅ Inserted batch {i//batch_size + 1}/{(len(rows)-1)//batch_size + 1}")
            
            target_conn.commit()
        
        logger.info(f"✅ Successfully migrated {len(rows)} rows to {table_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to migrate {table_name}: {e}")
        return False

def main():
    """Complete database migration"""
    logger.info("🚀 Starting COMPLETE Supabase → Railway migration")
    
    # Get database URLs
    supabase_url = os.getenv("SUPABASE_DATABASE_URL")
    railway_url = os.getenv("RAILWAY_DATABASE_URL")
    
    if not supabase_url or not railway_url:
        logger.error("❌ Missing database URLs!")
        logger.info("Set SUPABASE_DATABASE_URL and RAILWAY_DATABASE_URL")
        sys.exit(1)
    
    # Connect to databases
    try:
        logger.info("🔗 Connecting to databases...")
        supabase_engine = create_engine(supabase_url)
        railway_engine = create_engine(railway_url)
        
        # Test connections
        with supabase_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        with railway_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        logger.info("✅ Database connections successful")
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        sys.exit(1)
    
    # Get all tables from Supabase
    tables = get_all_tables(supabase_engine)
    if not tables:
        logger.error("❌ No tables found!")
        sys.exit(1)
    
    # Filter out system tables
    user_tables = [t for t in tables if not t.startswith(('auth.', 'storage.', 'realtime.', 'supabase_'))]
    logger.info(f"📋 User tables to migrate: {', '.join(user_tables)}")
    
    successful_migrations = 0
    
    for table_name in user_tables:
        logger.info(f"\n🔄 Processing table: {table_name}")
        
        # Get and create table schema
        create_sql = dump_table_schema(supabase_engine, table_name)
        if not create_sql:
            logger.warning(f"⚠️ Skipping {table_name} - schema dump failed")
            continue
        
        # Create table in Railway
        try:
            with railway_engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                conn.execute(text(create_sql))
                conn.commit()
            logger.info(f"✅ Created table: {table_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create {table_name}: {e}")
            continue
        
        # Migrate data
        success = migrate_table_data_safely(supabase_engine, railway_engine, table_name)
        if success:
            successful_migrations += 1
    
    logger.info(f"\n🎉 Migration completed!")
    logger.info(f"✅ Successfully migrated {successful_migrations}/{len(user_tables)} tables")
    logger.info("💡 Update your Railway app environment variables:")
    logger.info("   - Remove SUPABASE_DATABASE_URL")
    logger.info("   - Set DATABASE_URL to Railway PostgreSQL URL")

if __name__ == "__main__":
    main()