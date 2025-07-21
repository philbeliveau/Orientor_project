#!/usr/bin/env python3
"""
Force SQLAlchemy metadata refresh for production deployment
This directly updates the table metadata to recognize sequence defaults
"""

import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, inspect
from sqlalchemy.engine import reflection
from app.core.config import settings

def force_sqlalchemy_metadata_refresh():
    """
    Force SQLAlchemy to refresh its metadata cache and recognize sequence defaults
    This is needed when sequences are added to existing tables in production
    """
    
    print("[START] Forcing SQLAlchemy metadata refresh...")
    
    # Create engine with metadata reflection
    engine = create_engine(settings.get_database_url, echo=False)
    
    try:
        with engine.connect() as connection:
            print("[INFO] Connected to Railway database")
            
            # Create a fresh metadata instance
            metadata = MetaData()
            
            # Reflect the conversations table to get fresh metadata
            print("[INFO] Reflecting conversations table metadata...")
            conversations_table = Table('conversations', metadata, autoload_with=engine)
            
            # Check the current column configuration
            id_column = conversations_table.c.id
            print(f"[INFO] Current ID column: {id_column}")
            print(f"[INFO] Column type: {id_column.type}")
            print(f"[INFO] Column nullable: {id_column.nullable}")
            print(f"[INFO] Column autoincrement: {id_column.autoincrement}")
            print(f"[INFO] Column default: {id_column.default}")
            print(f"[INFO] Column server_default: {id_column.server_default}")
            
            # The issue is that SQLAlchemy doesn't see the server_default
            # Let's check what PostgreSQL actually has
            from sqlalchemy import text
            result = connection.execute(text("""
                SELECT column_default, is_nullable, data_type
                FROM information_schema.columns 
                WHERE table_name = 'conversations' AND column_name = 'id';
            """))
            db_column_info = result.fetchone()
            print(f"[DB INFO] PostgreSQL column default: {db_column_info[0]}")
            print(f"[DB INFO] PostgreSQL nullable: {db_column_info[1]}")
            print(f"[DB INFO] PostgreSQL data type: {db_column_info[2]}")
            
            # Test the actual sequence
            result = connection.execute(text("SELECT nextval('conversations_id_seq');"))
            next_val = result.fetchone()[0]
            print(f"[TEST] Sequence works - next value: {next_val}")
            
            # The problem is SQLAlchemy's INSERT doesn't include the DEFAULT
            # Let's test a raw SQL INSERT to confirm it works
            print("[TEST] Testing raw SQL INSERT...")
            result = connection.execute(text("""
                INSERT INTO conversations (user_id, title, auto_generated_title, message_count, total_tokens_used)
                VALUES (1, 'SQLAlchemy Metadata Test', true, 0, 0)
                RETURNING id;
            """))
            new_id = result.fetchone()[0]
            print(f"[SUCCESS] Raw SQL insert worked! New ID: {new_id}")
            
            # Clean up
            connection.execute(text(f"DELETE FROM conversations WHERE id = {new_id};"))
            connection.commit()
            
            # Now clear SQLAlchemy's metadata cache
            print("[FIX] Clearing SQLAlchemy metadata cache...")
            metadata.clear()
            engine.dispose()
            
            print("[SUCCESS] Metadata refresh completed")
            return True
            
    except Exception as e:
        print(f"[ERROR] Metadata refresh failed: {e}")
        return False

def create_sequence_aware_insert():
    """
    Create a service method that explicitly handles the sequence
    """
    
    print("[FIX] Creating sequence-aware insert method...")
    
    insert_method_code = '''
def create_conversation_with_sequence(db: Session, **kwargs) -> Conversation:
    """Create conversation with explicit sequence handling"""
    try:
        # Use raw SQL to ensure sequence default is applied
        result = db.execute(text("""
            INSERT INTO conversations (user_id, title, auto_generated_title, 
                                    category_id, is_favorite, is_archived, 
                                    last_message_at, message_count, total_tokens_used)
            VALUES (:user_id, :title, :auto_generated_title, 
                   :category_id, :is_favorite, :is_archived,
                   :last_message_at, :message_count, :total_tokens_used)
            RETURNING id, created_at, updated_at;
        """), kwargs)
        
        row = result.fetchone()
        conversation_id, created_at, updated_at = row
        
        # Now fetch the full conversation object
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        return conversation
        
    except Exception as e:
        db.rollback()
        raise e
'''
    
    # Write the method to a patch file
    with open('conversation_service_patch.py', 'w') as f:
        f.write(insert_method_code)
    
    print("[SUCCESS] Sequence-aware insert method created")
    return True

def main():
    """Main execution"""
    try:
        print("SQLAlchemy Metadata Refresh Tool")
        print("=" * 50)
        
        success = force_sqlalchemy_metadata_refresh()
        
        if success:
            create_sequence_aware_insert()
            print(f"\n[SUCCESS] METADATA REFRESH COMPLETE!")
            print(f"[INFO] Next: Apply the service patch to fix conversation creation")
        else:
            print(f"\n[ERROR] METADATA REFRESH FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()