import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create Base class for models
Base = declarative_base()

try:
    # Create engine using the URL from settings
    engine = create_engine(
        settings.get_database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True
    )
    
    # Test the connection and log database information
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database(), current_user, version()"))
        db_name, db_user, version = result.fetchone()
        logger.info(f"Connected to PostgreSQL database: {db_name}")
        logger.info(f"Database user: {db_user}")
        logger.info(f"PostgreSQL version: {version}")
        
        # Check if tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        logger.info(f"Available tables: {tables}")
        
except SQLAlchemyError as e:
    logger.error(f"Database connection error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()