from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv
import os
import logging
import sys
import time
from urllib.parse import urlparse, urlunparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def wait_for_db(engine, max_retries=5, initial_delay=1):
    """Wait for database to become available with exponential backoff."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                logger.info(f"Successfully connected to database after {attempt + 1} attempts")
                return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                return False
    return False

def get_database_url():
    """Get the database URL based on the environment."""
    # Check if we're running on Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("RAILWAY") is not None
    
    if is_railway:
        logger.info("Running on Railway environment")
        # When on Railway, use their DATABASE_URL
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            logger.error("DATABASE_URL not found in Railway environment!")
            logger.error("Please set the DATABASE_URL variable in your Railway dashboard.")
            sys.exit(1)
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
    
    # Create engine with optimized connection pooling and timeout settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,  # Enable connection health checks
        connect_args={
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    )
    
    # Wait for database to become available ONLY on Railway
    if os.getenv("RAILWAY_ENVIRONMENT"):
        if not wait_for_db(engine, max_retries=5, initial_delay=2):
            logger.warning("Database not available after retries, but continuing startup")
    
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
        logger.warning("Continuing with application startup despite connection test failure")
        
except SQLAlchemyError as e:
    logger.error(f"Database connection error: {str(e)}")
    # Don't raise the error here, we want the application to at least start
    # The real connection errors will be handled in the get_db() function
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    # Don't raise the error here either for the same reason

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session with retry mechanism."""
    retries = 3
    delay = 1
    
    for attempt in range(retries):
        db = SessionLocal()
        try:
            # Test the connection
            db.execute(text("SELECT 1"))
            break  # Connection successful, exit the retry loop
        except SQLAlchemyError as e:
            db.close()
            if attempt < retries - 1:
                logger.warning(f"Database session attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                logger.error(f"Failed to get database session after {retries} attempts: {str(e)}")
                raise
    
    # Now we have a working db session (or raised an exception)
    try:
        yield db
    finally:
        db.close()