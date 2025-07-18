from sqlalchemy import create_engine, text
from backend.app.core.config import settings

def diagnose_users_table():
    """Diagnose users table issues"""
    print("=== Users Table Diagnosis ===")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Check if users table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            table_exists = result.scalar()
            print(f"✅ users table exists: {table_exists}")
            
            if table_exists:
                # Check table structure
                result = conn.execute(text("""
                    SELECT column_name, column_default, is_nullable, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
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
                        AND relname = 'users_id_seq'
                    );
                """))
                sequence_exists = result.scalar()
                print(f"✅ Sequence exists: {sequence_exists}")
                
                # Check existing records
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"✅ Existing records: {count}")
                
                if count > 0:
                    result = conn.execute(text("SELECT MAX(id) FROM users"))
                    max_id = result.scalar()
                    print(f"✅ Maximum ID: {max_id}")
                    
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    diagnose_users_table()