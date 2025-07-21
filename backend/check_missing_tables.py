#!/usr/bin/env python3
"""
Check for missing critical tables and fix their sequences
"""

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def check_and_fix_missing_tables():
    """Check for conversations and chat_messages tables specifically"""
    
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as connection:
        all_tables = inspector.get_table_names()
        print(f"📋 All tables in database: {sorted(all_tables)}")
        
        # Check for critical chat tables
        critical_tables = ['conversations', 'chat_messages']
        
        for table in critical_tables:
            if table in all_tables:
                print(f"✅ Found {table} table")
                
                # Check if it has ID column
                columns = inspector.get_columns(table)
                id_col = next((col for col in columns if col['name'] == 'id'), None)
                
                if id_col:
                    # Get max ID
                    result = connection.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table};"))
                    max_id = result.fetchone()[0]
                    print(f"   📊 Max ID in {table}: {max_id}")
                    
                    # Fix sequence
                    sequence_name = f"{table}_id_seq"
                    connection.execute(text(f"""
                        CREATE SEQUENCE IF NOT EXISTS {sequence_name} 
                        START WITH {max_id + 1} 
                        INCREMENT BY 1 
                        OWNED BY {table}.id;
                    """))
                    
                    connection.execute(text(f"""
                        ALTER TABLE {table} 
                        ALTER COLUMN id SET DEFAULT nextval('{sequence_name}');
                    """))
                    
                    if max_id > 0:
                        connection.execute(text(f"SELECT setval('{sequence_name}', {max_id}, true);"))
                    else:
                        connection.execute(text(f"SELECT setval('{sequence_name}', 1, false);"))
                    
                    print(f"   ✅ Fixed sequence for {table}")
                    
            else:
                print(f"❌ Missing {table} table")
        
        connection.commit()

if __name__ == "__main__":
    check_and_fix_missing_tables()