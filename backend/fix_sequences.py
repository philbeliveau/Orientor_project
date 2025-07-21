#!/usr/bin/env python3
"""
Fix database sequence issues that cause null ID constraint violations
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def fix_conversation_sequence():
    """Fix the conversations table sequence issue"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
        
    try:
        # Fix for Railway/Heroku SSL issue
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        if '?sslmode=' not in database_url:
            database_url += '?sslmode=require'
            
        print("🔧 Connecting to database...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check current sequence value for conversations
            result = conn.execute(text('SELECT last_value FROM conversations_id_seq;'))
            last_value = result.fetchone()[0]
            print(f'Current conversations sequence last_value: {last_value}')
            
            # Check max ID in table
            result = conn.execute(text('SELECT COALESCE(MAX(id), 0) FROM conversations;'))
            max_id = result.fetchone()[0]
            print(f'Max ID in conversations table: {max_id}')
            
            if max_id >= last_value:
                new_value = max_id + 1
                conn.execute(text(f'ALTER SEQUENCE conversations_id_seq RESTART WITH {new_value};'))
                conn.commit()
                print(f'✅ Fixed conversations sequence: set to {new_value}')
            else:
                print('✅ Conversations sequence is already correct')
                
            # Also check other critical sequences
            sequences_to_check = [
                ('users_id_seq', 'users'),
                ('saved_recommendations_id_seq', 'saved_recommendations'),
                ('chat_messages_id_seq', 'chat_messages'),
                ('user_notes_id_seq', 'user_notes')
            ]
            
            for seq_name, table_name in sequences_to_check:
                try:
                    # Check if sequence exists
                    result = conn.execute(text(f"SELECT 1 FROM pg_sequence WHERE sequencename = '{seq_name}';"))
                    if result.fetchone():
                        # Get sequence and table values
                        result = conn.execute(text(f'SELECT last_value FROM {seq_name};'))
                        seq_last_value = result.fetchone()[0]
                        
                        result = conn.execute(text(f'SELECT COALESCE(MAX(id), 0) FROM {table_name};'))
                        table_max_id = result.fetchone()[0]
                        
                        if table_max_id >= seq_last_value:
                            new_seq_value = table_max_id + 1
                            conn.execute(text(f'ALTER SEQUENCE {seq_name} RESTART WITH {new_seq_value};'))
                            conn.commit()
                            print(f'✅ Fixed {seq_name}: set to {new_seq_value}')
                        else:
                            print(f'✅ {seq_name} is already correct (seq:{seq_last_value}, max:{table_max_id})')
                except Exception as e:
                    print(f'⚠️ Skipping {seq_name}: {e}')
                    
        return True
        
    except Exception as e:
        print(f'❌ Database sequence fix failed: {e}')
        return False

if __name__ == '__main__':
    print("🔧 Fixing database sequence issues...")
    success = fix_conversation_sequence()
    if success:
        print("✅ Database sequence fix completed successfully")
        sys.exit(0)
    else:
        print("❌ Database sequence fix failed")
        sys.exit(1)