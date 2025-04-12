import os
import sys
import time
import logging
from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Create Base class for models
Base = declarative_base()

def get_database_url():
    """Get the database URL based on the environment."""
    # Check if we're running on Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("RAILWAY") is not None
    
    if is_railway:
        logger.info("Running on Railway environment")
        # Use DATABASE_URL which points to the internal Railway PostgreSQL instance
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            logger.error("DATABASE_URL not found in Railway environment!")
            sys.exit(1)
        
        # Log which URL we're using
        if "railway.internal" in DATABASE_URL:
            logger.info("Using Railway internal database connection")
        elif "proxy.rlwy.net" in DATABASE_URL:
            logger.info("Using Railway proxy database connection")
        else:
            logger.info("Using custom database connection")
            
        logger.info("Using Railway database configuration")
    else:
        # Local development - use the exact working configuration
        DATABASE_URL = "postgresql+psycopg2://postgres:Mac.phil.007@localhost:5432/orientor_db"
        logger.info("Using local development database configuration")
    
    # Log URL (without sensitive info)
    parsed_url = urlparse(DATABASE_URL)
    safe_url = f"{parsed_url.scheme}://{parsed_url.username}:****@{parsed_url.hostname}:{parsed_url.port}/{parsed_url.path.lstrip('/')}"
    logger.info(f"Using database URL: {safe_url}")
    
    return DATABASE_URL

try:
    DATABASE_URL = get_database_url()
    
    # Create engine with optimized connection settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        connect_args={
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    )
    
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created or verified")
    
    # Test the connection and log database information
    try:
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
        logger.error(f"Database connection test failed: {str(e)}")
        raise
        
except SQLAlchemyError as e:
    logger.error(f"Database connection error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()