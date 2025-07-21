#!/usr/bin/env python3
"""
Refresh SQLAlchemy database metadata and connection pool
Forces SQLAlchemy to recognize new sequence configurations
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import reflection
from app.core.config import settings

def refresh_database_metadata():
    """Force refresh of SQLAlchemy metadata and connection pool"""
    
    print("[START] Refreshing database metadata and connection pool...")
    
    # Create a fresh engine with no connection pooling for this operation
    engine = create_engine(
        settings.get_database_url,
        poolclass=None,  # No connection pooling
        echo=False
    )
    
    try:
        with engine.connect() as connection:
            print("[INFO] Connected to Railway database with fresh engine")
            
            # Force SQLAlchemy to refresh table metadata
            inspector = reflection.Inspector.from_engine(engine)
            
            # Get fresh table information
            tables = inspector.get_table_names()
            print(f"[INFO] Found {len(tables)} tables in database")
            
            # Specifically check conversations table
            if 'conversations' in tables:
                columns = inspector.get_columns('conversations')
                id_column = next((col for col in columns if col['name'] == 'id'), None)
                
                if id_column:
                    print(f"[INFO] Conversations.id column type: {id_column['type']}")
                    print(f"[INFO] Conversations.id nullable: {id_column['nullable']}")
                    print(f"[INFO] Conversations.id autoincrement: {id_column.get('autoincrement', 'unknown')}")
                    print(f"[INFO] Conversations.id default: {id_column.get('default', 'none')}")
                
                # Test the sequence directly
                result = connection.execute(text("SELECT nextval('conversations_id_seq');"))
                next_val = result.fetchone()[0]
                print(f"[SUCCESS] Conversations sequence next value: {next_val}")
                
                # Test that column default is properly configured
                result = connection.execute(text("""
                    SELECT column_default 
                    FROM information_schema.columns 
                    WHERE table_name = 'conversations' AND column_name = 'id';
                """))
                default_val = result.fetchone()[0]
                print(f"[INFO] Column default value: {default_val}")
                
                # Test an actual insert without ID
                print("[TEST] Testing insert without ID specification...")
                try:
                    result = connection.execute(text("""
                        INSERT INTO conversations (user_id, title, auto_generated_title, message_count, total_tokens_used)
                        VALUES (1, 'Metadata Refresh Test', true, 0, 0)
                        RETURNING id;
                    """))
                    new_id = result.fetchone()[0]
                    print(f"[SUCCESS] Insert test worked! New ID: {new_id}")
                    
                    # Clean up test record
                    connection.execute(text(f"DELETE FROM conversations WHERE id = {new_id};"))
                    connection.commit()
                    print("[INFO] Test record cleaned up")
                    
                except Exception as e:
                    print(f"[ERROR] Insert test failed: {e}")
                    connection.rollback()
                    return False
            else:
                print("[ERROR] Conversations table not found!")
                return False
            
            print("[SUCCESS] Database metadata refresh completed!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Database metadata refresh failed: {e}")
        return False
    finally:
        # Dispose of the temporary engine
        engine.dispose()
        print("[INFO] Temporary engine disposed")

def main():
    """Main execution"""
    try:
        print("Railway Database Metadata Refresh Tool")
        print("=" * 50)
        
        success = refresh_database_metadata()
        
        if success:
            print(f"\n[SUCCESS] METADATA REFRESH COMPLETE!")
            print(f"[INFO] SQLAlchemy should now recognize the sequence configuration")
            print(f"[INFO] Application restart may be required to clear cached metadata")
        else:
            print(f"\n[ERROR] METADATA REFRESH FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Critical error during refresh: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()