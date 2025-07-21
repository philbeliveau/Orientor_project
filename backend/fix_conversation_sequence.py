#!/usr/bin/env python3
"""
Fix conversation table sequence issue
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_conversation_sequence():
    """Fix the conversation table sequence for auto-increment IDs"""
    
    # Connect to database
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if conversations table exists
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'conversations'
            );
        """))
        
        if not result.fetchone()[0]:
            print("❌ Conversations table doesn't exist")
            return False
            
        # Check current max ID
        result = connection.execute(text("SELECT COALESCE(MAX(id), 0) FROM conversations;"))
        max_id = result.fetchone()[0]
        print(f"📊 Current max conversation ID: {max_id}")
        
        # Create sequence if it doesn't exist
        connection.execute(text("""
            CREATE SEQUENCE IF NOT EXISTS conversations_id_seq 
            START WITH %s 
            INCREMENT BY 1 
            OWNED BY conversations.id;
        """ % (max_id + 1)))
        
        # Set the sequence as default for the id column
        connection.execute(text("""
            ALTER TABLE conversations 
            ALTER COLUMN id SET DEFAULT nextval('conversations_id_seq');
        """))
        
        # Set the sequence current value
        if max_id > 0:
            connection.execute(text(f"SELECT setval('conversations_id_seq', {max_id}, true);"))
        else:
            connection.execute(text("SELECT setval('conversations_id_seq', 1, false);"))
        
        connection.commit()
        print("✅ Conversation sequence fixed successfully")
        return True

if __name__ == "__main__":
    try:
        success = fix_conversation_sequence()
        if success:
            print("🚀 Conversation table is ready for auto-increment IDs")
        else:
            print("❌ Failed to fix conversation sequence")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error fixing sequence: {e}")
        sys.exit(1)