from app.utils.database import engine

try:
    with engine.connect() as connection:
        print("Database connection successful!")
    
    # Test if tables exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    
except Exception as e:
    print(f"Database connection failed: {e}") 