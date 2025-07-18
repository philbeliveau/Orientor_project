import requests
import json
from sqlalchemy import create_engine, text
from backend.app.core.config import settings

def diagnose_database():
    """Diagnose database issues"""
    print("=== Database Diagnosis ===")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Check if personality_assessments table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'personality_assessments'
                );
            """))
            table_exists = result.scalar()
            print(f"✅ personality_assessments table exists: {table_exists}")
            
            if table_exists:
                # Check table structure
                result = conn.execute(text("""
                    SELECT column_name, column_default, is_nullable, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'personality_assessments' 
                    AND column_name = 'id';
                """))
                id_column = result.fetchone()
                if id_column:
                    print(f"✅ ID column: {id_column}")
                else:
                    print("❌ ID column not found")
                
                # Check sequence
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM pg_class 
                        WHERE relkind = 'S' 
                        AND relname = 'personality_assessments_id_seq'
                    );
                """))
                sequence_exists = result.scalar()
                print(f"✅ Sequence exists: {sequence_exists}")
                
                if sequence_exists:
                    # Check sequence current value
                    result = conn.execute(text("SELECT currval('personality_assessments_id_seq')"))
                    try:
                        current_val = result.scalar()
                        print(f"✅ Current sequence value: {current_val}")
                    except Exception as e:
                        print(f"⚠️  Sequence not used yet: {e}")
                
                # Check existing records
                result = conn.execute(text("SELECT COUNT(*) FROM personality_assessments"))
                count = result.scalar()
                print(f"✅ Existing records: {count}")
                
                if count > 0:
                    result = conn.execute(text("SELECT MAX(id) FROM personality_assessments"))
                    max_id = result.scalar()
                    print(f"✅ Maximum ID: {max_id}")
                    
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    diagnose_database()