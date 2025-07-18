#!/usr/bin/env python3
"""
Extract INSERT statements from navigo_local backup for Supabase data migration
"""

import re
from pathlib import Path

def extract_insert_statements():
    """Extract only INSERT statements from backup file"""
    
    backup_file = Path("orientor-clean/navigo_local_backup.sql")
    output_file = Path("navigo_data_migration.sql")
    
    insert_statements = []
    
    print("🔍 Extracting INSERT statements...")
    
    with open(backup_file, 'r') as f:
        content = f.read()
    
    # Find all INSERT statements
    insert_pattern = r'INSERT INTO [^;]+;'
    inserts = re.findall(insert_pattern, content, re.MULTILINE | re.DOTALL)
    
    # Filter out empty or problematic inserts
    valid_inserts = []
    for insert in inserts:
        # Skip if contains problematic patterns
        if any(skip in insert.lower() for skip in ['pg_stat', 'pg_catalog', 'information_schema']):
            continue
        valid_inserts.append(insert.strip())
    
    print(f"📊 Found {len(valid_inserts)} INSERT statements")
    
    # Write to output file
    with open(output_file, 'w') as f:
        f.write("-- Data migration for Supabase\n")
        f.write("-- Generated from navigo_local backup\n\n")
        
        # Disable triggers for faster insertion
        f.write("SET session_replication_role = replica;\n\n")
        
        for insert in valid_inserts:
            f.write(insert + "\n\n")
        
        # Re-enable triggers
        f.write("SET session_replication_role = DEFAULT;\n")
    
    print(f"✅ Data migration file created: {output_file}")
    print(f"📝 Contains {len(valid_inserts)} INSERT statements")
    
    return output_file

if __name__ == "__main__":
    extract_insert_statements()