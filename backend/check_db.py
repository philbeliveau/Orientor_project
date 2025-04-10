import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    load_dotenv()
    
    # Get database URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("DATABASE_URL is not set!")
        return False
        
    try:
        # Create engine
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(DATABASE_URL)
        
        # Get inspector
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        logger.info(f"Found tables: {tables}")
        
        # For each table, get column information
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            logger.info(f"\nTable: {table_name}")
            for column in columns:
                logger.info(f"Column: {column['name']}, Type: {column['type']}")
                
        return True
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return False

if __name__ == "__main__":
    check_database() 