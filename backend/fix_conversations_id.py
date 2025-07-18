#!/usr/bin/env python3
"""
Emergency fix for conversations table auto-increment ID issue
This script will fix the conversations table to have proper auto-increment functionality.
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings

def fix_conversations_id_sequence():
    """Fix the conversations table to have proper auto-increment ID"""
    
    # Get database URL
    settings = Settings()
    database_url = settings.get_database_url
    print(f"Connecting to database...")
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            print("Connected successfully!")
            
            # Check current max ID in conversations table
            result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM conversations"))
            max_id = result.fetchone()[0]
            print(f"Current maximum ID in conversations table: {max_id}")
            
            # Create sequence for conversations table
            print("Creating sequence for conversations table...")
            conn.execute(text("CREATE SEQUENCE IF NOT EXISTS conversations_id_seq START WITH 1;"))
            
            # Set the sequence to start from max_id + 1
            next_id = max_id + 1
            print(f"Setting sequence to start from: {next_id}")
            conn.execute(text(f"SELECT setval('conversations_id_seq', {next_id});"))
            
            # Alter the table to use the sequence as default for id column
            print("Altering conversations table to use sequence...")
            conn.execute(text("ALTER TABLE conversations ALTER COLUMN id SET DEFAULT nextval('conversations_id_seq');"))
            
            # Set ownership of the sequence to the table column
            print("Setting sequence ownership...")
            conn.execute(text("ALTER SEQUENCE conversations_id_seq OWNED BY conversations.id;"))
            
            # Test the fix by checking the default value
            result = conn.execute(text("""
                SELECT column_default 
                FROM information_schema.columns 
                WHERE table_name='conversations' AND column_name='id'
            """))
            default_value = result.fetchone()[0]
            print(f"New default value for conversations.id: {default_value}")
            
            # Commit the changes
            conn.commit()
            print("✅ Fix applied successfully!")
            
            # Also fix conversation_categories and chat_messages if needed
            print("\nChecking other tables...")
            
            # Fix conversation_categories
            result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM conversation_categories"))
            max_cat_id = result.fetchone()[0]
            print(f"Current maximum ID in conversation_categories: {max_cat_id}")
            
            conn.execute(text("CREATE SEQUENCE IF NOT EXISTS conversation_categories_id_seq START WITH 1;"))
            next_cat_id = max_cat_id + 1
            conn.execute(text(f"SELECT setval('conversation_categories_id_seq', {next_cat_id});"))
            conn.execute(text("ALTER TABLE conversation_categories ALTER COLUMN id SET DEFAULT nextval('conversation_categories_id_seq');"))
            conn.execute(text("ALTER SEQUENCE conversation_categories_id_seq OWNED BY conversation_categories.id;"))
            
            # Fix chat_messages
            result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM chat_messages"))
            max_msg_id = result.fetchone()[0]
            print(f"Current maximum ID in chat_messages: {max_msg_id}")
            
            conn.execute(text("CREATE SEQUENCE IF NOT EXISTS chat_messages_id_seq START WITH 1;"))
            next_msg_id = max_msg_id + 1
            conn.execute(text(f"SELECT setval('chat_messages_id_seq', {next_msg_id});"))
            conn.execute(text("ALTER TABLE chat_messages ALTER COLUMN id SET DEFAULT nextval('chat_messages_id_seq');"))
            conn.execute(text("ALTER SEQUENCE chat_messages_id_seq OWNED BY chat_messages.id;"))
            
            conn.commit()
            print("✅ All tables fixed successfully!")
            
    except Exception as e:
        print(f"❌ Error fixing conversations table: {e}")
        sys.exit(1)
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("🔧 Fixing conversations table auto-increment ID issue...")
    fix_conversations_id_sequence()
    print("🎉 Database fix completed!")