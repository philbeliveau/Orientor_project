#!/usr/bin/env python3
"""
Supabase Migration Script for navigo_local database
Safely migrates database while preserving fallback options
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupabaseMigrator:
    def __init__(self):
        self.backup_dir = Path("./backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Supabase connection details (to be filled)
        self.supabase_url = os.getenv("SUPABASE_DATABASE_URL")
        self.local_backup_file = "orientor-clean/navigo_local_backup.sql"
        
    def validate_prerequisites(self):
        """Check if all required tools and configs are available"""
        logger.info("🔍 Validating prerequisites...")
        
        # Check if backup file exists
        if not Path(self.local_backup_file).exists():
            logger.error(f"❌ Backup file not found: {self.local_backup_file}")
            return False
            
        # Check if Supabase URL is configured
        if not self.supabase_url:
            logger.error("❌ SUPABASE_DATABASE_URL not configured")
            logger.info("ℹ️  Please set SUPABASE_DATABASE_URL in your .env file")
            return False
            
        # Check if psql is available
        try:
            subprocess.run(["psql", "--version"], capture_output=True, check=True)
            logger.info("✅ psql is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ psql not found. Please install PostgreSQL client tools")
            return False
            
        return True
    
    def test_supabase_connection(self):
        """Test connection to Supabase database"""
        logger.info("🔌 Testing Supabase connection...")
        
        try:
            # Test connection with a simple query
            cmd = [
                "psql", self.supabase_url, 
                "-c", "SELECT version();"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("✅ Supabase connection successful")
            logger.info(f"Database version: {result.stdout.strip()}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Supabase connection failed: {e.stderr}")
            return False
    
    def prepare_migration_sql(self):
        """Prepare SQL file for Supabase import (clean extensions, etc.)"""
        logger.info("📝 Preparing migration SQL...")
        
        input_file = Path(self.local_backup_file)
        output_file = self.backup_dir / f"supabase_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                # Add Supabase-compatible setup at the top
                outfile.write("-- Supabase migration setup\n")
                outfile.write("-- UUID and trigram extensions are pre-installed in Supabase\n\n")
                
                for line in infile:
                    # Skip problematic lines for Supabase
                    if any(skip_pattern in line.lower() for skip_pattern in [
                        'create extension if not exists pg_trgm',
                        'create extension if not exists "uuid-ossp"',
                        'comment on extension',
                        'create database',
                        'connect ',
                        '\\connect'
                    ]):
                        logger.debug(f"Skipping line: {line.strip()}")
                        continue
                    
                    # Handle CREATE FUNCTION to avoid conflicts
                    if line.strip().startswith('CREATE FUNCTION') or line.strip().startswith('create function'):
                        line = line.replace('CREATE FUNCTION', 'CREATE OR REPLACE FUNCTION')
                        line = line.replace('create function', 'CREATE OR REPLACE FUNCTION')
                    
                    # Handle CREATE TABLE to avoid conflicts  
                    if line.strip().startswith('CREATE TABLE') or line.strip().startswith('create table'):
                        line = line.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
                        line = line.replace('create table', 'CREATE TABLE IF NOT EXISTS')
                    
                    # Replace owner assignments (Supabase manages these)
                    if 'owner to' in line.lower():
                        continue
                    
                    # Fix UUID function calls for Supabase (UUID functions are in public schema)
                    line = line.replace('public.uuid_generate_v4()', 'uuid_generate_v4()')
                        
                    outfile.write(line)
            
            logger.info(f"✅ Prepared migration file: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare migration SQL: {e}")
            return None
    
    def execute_migration(self, migration_file):
        """Execute the migration to Supabase"""
        logger.info("🚀 Starting migration to Supabase...")
        
        try:
            cmd = [
                "psql", self.supabase_url,
                "-f", str(migration_file),
                "-v", "ON_ERROR_STOP=1"
            ]
            
            logger.info("📤 Uploading data to Supabase...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info("✅ Migration completed successfully!")
            logger.info("📊 Migration summary:")
            
            # Count tables created (simple heuristic)
            output_lines = result.stdout.split('\n')
            table_count = sum(1 for line in output_lines if 'CREATE TABLE' in line)
            logger.info(f"   Tables processed: ~{table_count}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Migration failed: {e.stderr}")
            logger.error("🔄 Your local database is still intact")
            return False
    
    def verify_migration(self):
        """Verify that the migration was successful"""
        logger.info("🔍 Verifying migration...")
        
        try:
            # Check table count
            cmd = [
                "psql", self.supabase_url,
                "-t", "-c", 
                "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            table_count = int(result.stdout.strip())
            
            logger.info(f"✅ Found {table_count} tables in Supabase")
            
            if table_count > 0:
                logger.info("🎉 Migration verification successful!")
                return True
            else:
                logger.warning("⚠️  No tables found - migration might have failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        logger.info("🚀 Starting Supabase migration process...")
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            logger.error("❌ Prerequisites not met. Aborting migration.")
            return False
        
        # Step 2: Test Supabase connection
        if not self.test_supabase_connection():
            logger.error("❌ Cannot connect to Supabase. Aborting migration.")
            return False
        
        # Step 3: Prepare migration SQL
        migration_file = self.prepare_migration_sql()
        if not migration_file:
            logger.error("❌ Failed to prepare migration file. Aborting.")
            return False
        
        # Step 4: Execute migration
        if not self.execute_migration(migration_file):
            logger.error("❌ Migration failed. Your local database is still intact.")
            return False
        
        # Step 5: Verify migration
        if not self.verify_migration():
            logger.warning("⚠️  Migration verification failed. Check manually.")
            return False
        
        logger.info("🎉 Migration completed successfully!")
        logger.info("📋 Next steps:")
        logger.info("   1. Update your .env file with SUPABASE_DATABASE_URL")
        logger.info("   2. Test your application")
        logger.info("   3. Update connection configs if needed")
        
        return True

def main():
    """Main migration function"""
    print("🔄 Supabase Migration Tool")
    print("=" * 50)
    
    # Auto-proceed for automated execution
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("🚀 Auto-migration mode enabled")
    else:
        # Check if user wants to proceed
        try:
            response = input("⚠️  This will migrate your database to Supabase. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled by user.")
                return
        except EOFError:
            print("🚀 Running in automated mode")
    
    migrator = SupabaseMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔧 Remember to update your application configuration.")
    else:
        print("\n❌ Migration failed. Your local database is intact.")
        print("🔧 Check the logs above for details.")

if __name__ == "__main__":
    main()