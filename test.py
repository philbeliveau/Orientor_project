from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Replace these with your actual PostgreSQL credentials
DATABASE_URL = "postgresql://postgres:Mac.phil.007@localhost:5432/orientor_db"

def test_connection():
    try:
        # Create engine and try to connect
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("✅ Successfully connected to the database!")
            
            # Test if we can execute a simple query
            result = connection.execute(text("SELECT 1"))
            print("✅ Successfully executed test query!")
            
    except SQLAlchemyError as e:
        print(f"❌ Error connecting to the database: {e}")

if __name__ == "__main__":
    test_connection()