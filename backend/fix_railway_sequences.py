#!/usr/bin/env python3
"""
Fix Railway database sequences - Critical issue with conversations table
The previous sequence fix didn't properly set the DEFAULT constraint on Railway
"""

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def fix_railway_sequences():
    """Fix Railway database sequences with explicit DEFAULT constraint"""
    
    print("[START] Fixing Railway database sequences...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        print("[SUCCESS] Connected to Railway database")
        
        # Fix conversations table specifically
        print("\n[FIX] Fixing conversations table sequence...")
        
        try:
            # Get current max ID
            result = connection.execute(text("SELECT COALESCE(MAX(id), 0) FROM conversations;"))
            max_id = result.fetchone()[0]
            print(f"   [INFO] Current max conversation ID: {max_id}")
            
            # Drop existing default if any
            connection.execute(text("""
                ALTER TABLE conversations 
                ALTER COLUMN id DROP DEFAULT;
            """))
            print("   [INFO] Dropped existing default")
            
            # Create or replace sequence
            connection.execute(text(f"""
                DROP SEQUENCE IF EXISTS conversations_id_seq CASCADE;
                CREATE SEQUENCE conversations_id_seq 
                START WITH {max_id + 1} 
                INCREMENT BY 1 
                OWNED BY conversations.id;
            """))
            print(f"   [SUCCESS] Created sequence starting at {max_id + 1}")
            
            # Set sequence as default
            connection.execute(text("""
                ALTER TABLE conversations 
                ALTER COLUMN id SET DEFAULT nextval('conversations_id_seq');
            """))
            print("   [SUCCESS] Set sequence as default for conversations.id")
            
            # Set current value
            if max_id > 0:
                connection.execute(text(f"SELECT setval('conversations_id_seq', {max_id}, true);"))
                print(f"   [SUCCESS] Set sequence current value to {max_id}")
            
            # Test the sequence
            test_result = connection.execute(text("SELECT nextval('conversations_id_seq');"))
            next_val = test_result.fetchone()[0]
            print(f"   [TEST] Next ID will be: {next_val}")
            
        except Exception as e:
            print(f"   [ERROR] Error fixing conversations: {e}")
            raise
        
        # Fix chat_messages table too
        print("\n[FIX] Fixing chat_messages table sequence...")
        
        try:
            # Get current max ID
            result = connection.execute(text("SELECT COALESCE(MAX(id), 0) FROM chat_messages;"))
            max_id = result.fetchone()[0]
            print(f"   [INFO] Current max chat_messages ID: {max_id}")
            
            # Drop existing default
            connection.execute(text("""
                ALTER TABLE chat_messages 
                ALTER COLUMN id DROP DEFAULT;
            """))
            
            # Create or replace sequence
            connection.execute(text(f"""
                DROP SEQUENCE IF EXISTS chat_messages_id_seq CASCADE;
                CREATE SEQUENCE chat_messages_id_seq 
                START WITH {max_id + 1} 
                INCREMENT BY 1 
                OWNED BY chat_messages.id;
            """))
            print(f"   [SUCCESS] Created sequence starting at {max_id + 1}")
            
            # Set sequence as default
            connection.execute(text("""
                ALTER TABLE chat_messages 
                ALTER COLUMN id SET DEFAULT nextval('chat_messages_id_seq');
            """))
            print("   [SUCCESS] Set sequence as default for chat_messages.id")
            
            # Set current value
            if max_id > 0:
                connection.execute(text(f"SELECT setval('chat_messages_id_seq', {max_id}, true);"))
                print(f"   [SUCCESS] Set sequence current value to {max_id}")
            
        except Exception as e:
            print(f"   [ERROR] Error fixing chat_messages: {e}")
            raise
        
        # Commit all changes
        connection.commit()
        print("\n[SUCCESS] All sequence fixes committed successfully")
        
        return True

if __name__ == "__main__":
    try:
        success = fix_railway_sequences()
        if success:
            print("\n[SUCCESS] Railway sequences fixed successfully!")
            print("[INFO] Conversations and chat messages can now be created properly")
        else:
            print("[ERROR] Failed to fix Railway sequences")
            exit(1)
    except Exception as e:
        print(f"[ERROR] Critical error: {e}")
        exit(1)