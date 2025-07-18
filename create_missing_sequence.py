from sqlalchemy import create_engine, text
from backend.app.core.config import settings

def create_missing_sequence():
    """Create missing sequence for personality_assessments table"""
    print("=== Creating Missing Sequence ===")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            with conn.begin():
                # Create sequence
                print("1. Creating sequence...")
                conn.execute(text("CREATE SEQUENCE personality_assessments_id_seq;"))
                
                # Get current max ID
                result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM personality_assessments;"))
                max_id = result.scalar()
                print(f"2. Current max ID: {max_id}")
                
                # Set sequence to next value
                next_val = max_id + 1
                print(f"3. Setting sequence to: {next_val}")
                conn.execute(text(f"SELECT setval('personality_assessments_id_seq', {next_val});"))
                
                # Set column default
                print("4. Setting column default...")
                conn.execute(text("""
                    ALTER TABLE personality_assessments 
                    ALTER COLUMN id SET DEFAULT nextval('personality_assessments_id_seq');
                """))
                
                # Associate sequence with column
                print("5. Associating sequence with column...")
                conn.execute(text("""
                    ALTER SEQUENCE personality_assessments_id_seq 
                    OWNED BY personality_assessments.id;
                """))
                
                # Test sequence
                print("6. Testing sequence...")
                result = conn.execute(text("SELECT nextval('personality_assessments_id_seq');"))
                test_val = result.scalar()
                print(f"   Next value: {test_val}")
                
                print("✅ Sequence created successfully!")
                
    except Exception as e:
        print(f"❌ Error creating sequence: {e}")

if __name__ == "__main__":
    create_missing_sequence()