#!/usr/bin/env python3
"""
Fix all database sequences for Railway PostgreSQL
This ensures auto-increment IDs work properly for all tables
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def get_all_tables_with_id_columns(engine):
    """Get all tables that have an 'id' column for sequence fixing"""
    inspector = inspect(engine)
    tables_with_id = []
    
    with engine.connect() as connection:
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            id_column = next((col for col in columns if col['name'] == 'id'), None)
            
            if id_column and 'int' in str(id_column['type']).lower():
                # Check if it's likely a primary key
                pk_constraint = inspector.get_pk_constraint(table_name)
                if pk_constraint and 'id' in pk_constraint.get('constrained_columns', []):
                    tables_with_id.append(table_name)
                    print(f"[INFO] Found table with ID column: {table_name}")
    
    return tables_with_id

def fix_sequences_for_all_tables():
    """Fix sequences for all tables with ID columns"""
    
    print("[START] Starting comprehensive sequence fix for Railway database...")
    
    # Connect to Railway database
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        print("[SUCCESS] Connected to Railway database")
        
        # Get all tables with ID columns
        tables_with_id = get_all_tables_with_id_columns(engine)
        
        if not tables_with_id:
            print("[ERROR] No tables with ID columns found")
            return False
        
        print(f"[INFO] Found {len(tables_with_id)} tables needing sequence fixes")
        
        # Fix sequences for each table
        fixed_count = 0
        for table_name in tables_with_id:
            try:
                print(f"\n[FIX] Fixing sequence for: {table_name}")
                
                # Get current max ID
                result = connection.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name};"))
                max_id = result.fetchone()[0]
                print(f"   [INFO] Current max ID: {max_id}")
                
                # Create sequence name (PostgreSQL convention)
                sequence_name = f"{table_name}_id_seq"
                
                # Create sequence if it doesn't exist
                connection.execute(text(f"""
                    CREATE SEQUENCE IF NOT EXISTS {sequence_name} 
                    START WITH {max_id + 1} 
                    INCREMENT BY 1 
                    OWNED BY {table_name}.id;
                """))
                print(f"   [SUCCESS] Created/updated sequence: {sequence_name}")
                
                # Set the sequence as default for the id column
                connection.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ALTER COLUMN id SET DEFAULT nextval('{sequence_name}');
                """))
                print(f"   [SUCCESS] Set default nextval for {table_name}.id")
                
                # Set the sequence current value
                if max_id > 0:
                    connection.execute(text(f"SELECT setval('{sequence_name}', {max_id}, true);"))
                    print(f"   [SUCCESS] Set sequence value to {max_id}")
                else:
                    connection.execute(text(f"SELECT setval('{sequence_name}', 1, false);"))
                    print(f"   [SUCCESS] Set sequence to start at 1")
                
                fixed_count += 1
                
            except Exception as e:
                print(f"   [ERROR] Error fixing {table_name}: {e}")
                continue
        
        # Commit all changes
        connection.commit()
        
        print(f"\n[SUCCESS] Successfully fixed sequences for {fixed_count}/{len(tables_with_id)} tables")
        
        # Test a few critical tables
        critical_tables = ['conversations', 'chat_messages', 'users', 'user_profiles']
        print(f"\n[TEST] Testing critical tables...")
        
        for table in critical_tables:
            if table in tables_with_id:
                try:
                    # Test sequence nextval
                    result = connection.execute(text(f"SELECT nextval('{table}_id_seq');"))
                    next_val = result.fetchone()[0]
                    print(f"   [SUCCESS] {table}: next ID will be {next_val}")
                except Exception as e:
                    print(f"   [WARNING] {table}: {e}")
        
        return fixed_count > 0

def main():
    """Main execution function"""
    try:
        print("[START] Railway Database Sequence Repair Tool")
        print("=" * 50)
        
        success = fix_sequences_for_all_tables()
        
        if success:
            print(f"\n[SUCCESS] SEQUENCE REPAIR COMPLETE!")
            print(f"[INFO] All tables now have proper auto-increment sequences")
            print(f"[INFO] New records can be created without specifying IDs")
            print(f"[INFO] Chat, conversations, profiles should now work!")
        else:
            print(f"\n[ERROR] SEQUENCE REPAIR FAILED")
            print(f"[INFO] Check database connection and permissions")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Critical error during sequence repair: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()