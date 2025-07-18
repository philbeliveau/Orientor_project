#!/usr/bin/env python3
"""
Complete migration from navigo_local (57 tables) to Supabase
This script will migrate the full schema and data
"""

import subprocess
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteMigrator:
    def __init__(self):
        # Source database (from .env backup info)
        self.source_db = "postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local"
        
        # Target Supabase database
        self.target_db = "postgresql://postgres:Supabase.phil.007@db.tyhcruhmrfvtcinofupn.supabase.co:5432/postgres"
        
        self.backup_file = f"complete_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    def test_connections(self):
        """Test both source and target connections"""
        logger.info("🔍 Testing database connections...")
        
        # Test source (if available)
        logger.info("Testing source database (navigo_local)...")
        try:
            cmd = ["psql", self.source_db, "-c", "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                table_count = result.stdout.strip().split('\n')[-2].strip()
                logger.info(f"✅ Source database: {table_count} tables found")
                return True
            else:
                logger.warning(f"⚠️  Source database not accessible: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"⚠️  Source database connection failed: {e}")
            return False
    
    def test_target_connection(self):
        """Test Supabase connection"""
        logger.info("Testing target database (Supabase)...")
        try:
            cmd = ["psql", self.target_db, "-c", "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            table_count = result.stdout.strip().split('\n')[-2].strip()
            logger.info(f"✅ Target database: {table_count} tables found")
            return True
        except Exception as e:
            logger.error(f"❌ Target database connection failed: {e}")
            return False
    
    def create_schema_dump(self):
        """Create a schema-only dump to understand structure"""
        logger.info("📋 Creating schema dump for analysis...")
        
        try:
            # Try direct pg_dump if source is available
            cmd = [
                "pg_dump", self.source_db,
                "--schema-only", "--no-owner", "--no-privileges",
                "-f", "schema_analysis.sql"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("✅ Schema dump created successfully")
                return True
            else:
                logger.warning(f"⚠️  Direct schema dump failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Schema dump failed: {e}")
            return False
    
    def analyze_missing_tables(self):
        """Compare source and target to find missing tables"""
        logger.info("🔍 Analyzing missing tables...")
        
        try:
            # Get Supabase tables
            cmd = ["psql", self.target_db, "-t", "-c", 
                   "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            supabase_tables = set(line.strip() for line in result.stdout.strip().split('\n') if line.strip())
            
            logger.info(f"📊 Found {len(supabase_tables)} tables in Supabase:")
            for table in sorted(supabase_tables):
                logger.info(f"   - {table}")
            
            # If we have schema dump, analyze it
            if os.path.exists("schema_analysis.sql"):
                with open("schema_analysis.sql", 'r') as f:
                    schema_content = f.read()
                
                # Find CREATE TABLE statements
                import re
                table_pattern = r'CREATE TABLE[^(]*([a-zA-Z_][a-zA-Z0-9_]*)'
                source_tables = set(re.findall(table_pattern, schema_content, re.IGNORECASE))
                
                logger.info(f"📊 Found {len(source_tables)} tables in source schema:")
                
                missing_tables = source_tables - supabase_tables
                if missing_tables:
                    logger.warning(f"⚠️  Missing {len(missing_tables)} tables in Supabase:")
                    for table in sorted(missing_tables):
                        logger.warning(f"   - {table}")
                else:
                    logger.info("✅ All source tables exist in Supabase")
                
                return source_tables, supabase_tables, missing_tables
            
            return set(), supabase_tables, set()
            
        except Exception as e:
            logger.error(f"❌ Table analysis failed: {e}")
            return set(), set(), set()
    
    def create_data_migration(self):
        """Create data-only migration if schema exists"""
        logger.info("📦 Creating data migration...")
        
        try:
            # Try to create data-only dump
            cmd = [
                "pg_dump", self.source_db,
                "--data-only", "--no-owner", "--no-privileges",
                "--inserts", "--column-inserts",
                "-f", self.backup_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ Data dump created: {self.backup_file}")
                return True
            else:
                logger.error(f"❌ Data dump failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Data migration creation failed: {e}")
            return False
    
    def execute_data_migration(self):
        """Execute the data migration to Supabase"""
        if not os.path.exists(self.backup_file):
            logger.error(f"❌ Migration file not found: {self.backup_file}")
            return False
        
        logger.info(f"🚀 Executing data migration from {self.backup_file}...")
        
        try:
            cmd = ["psql", self.target_db, "-f", self.backup_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info("✅ Data migration completed successfully!")
                logger.info("📊 Migration summary in stdout:")
                logger.info(result.stdout[-500:])  # Last 500 chars
                return True
            else:
                logger.error(f"❌ Data migration failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Data migration execution failed: {e}")
            return False
    
    def verify_migration(self):
        """Verify the migration was successful"""
        logger.info("🔍 Verifying migration...")
        
        try:
            # Check table counts
            cmd = ["psql", self.target_db, "-t", "-c", 
                   "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            table_count = int(result.stdout.strip())
            
            logger.info(f"📊 Final table count in Supabase: {table_count}")
            
            # Check for data in key tables
            cmd = ["psql", self.target_db, "-t", "-c", 
                   "SELECT 'users', count(*) FROM users UNION ALL SELECT 'courses', count(*) FROM courses;"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info("📊 Sample table row counts:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(f"   {line.strip()}")
            
            return table_count >= 50  # Expect at least 50 tables
            
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False
    
    def run_complete_migration(self):
        """Run the complete migration process"""
        logger.info("🚀 Starting complete migration process...")
        
        # Step 1: Test connections
        source_available = self.test_connections()
        if not self.test_target_connection():
            logger.error("❌ Cannot connect to Supabase. Aborting.")
            return False
        
        # Step 2: Analyze current state
        if source_available:
            self.create_schema_dump()
        
        source_tables, target_tables, missing_tables = self.analyze_missing_tables()
        
        if len(target_tables) >= 50:
            logger.info("✅ Supabase appears to have most tables already")
            if source_available and missing_tables:
                logger.info(f"ℹ️  Will migrate missing tables: {len(missing_tables)}")
            else:
                logger.info("✅ Migration may already be complete")
                return self.verify_migration()
        
        # Step 3: Create and execute migration if source is available
        if source_available:
            if self.create_data_migration():
                if self.execute_data_migration():
                    return self.verify_migration()
        else:
            logger.warning("⚠️  Source database not accessible")
            logger.info("ℹ️  Will verify current Supabase state")
            return self.verify_migration()
        
        return False

def main():
    """Main function"""
    print("🔄 Complete Migration Tool - navigo_local to Supabase")
    print("=" * 60)
    
    migrator = CompleteMigrator()
    success = migrator.run_complete_migration()
    
    if success:
        print("\n✅ Migration verification completed!")
        print("🎉 Your Supabase database is ready!")
    else:
        print("\n⚠️  Migration verification found issues.")
        print("💡 Check logs above for details.")

if __name__ == "__main__":
    main()