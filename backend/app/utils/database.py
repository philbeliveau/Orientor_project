from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
import logging
import sys
from urllib.parse import urlparse, urlunparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_database_url():
    """Get the database URL based on the environment."""
    # Check if we're running on Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("RAILWAY") is not None
    
    # 1. Try to use Railway PostgreSQL variables if running on Railway
    if is_railway:
        logger.info("Running on Railway environment")
        pg_host = os.getenv("PGHOST")
        pg_db = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB")
        pg_user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER")
        pg_password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")
        pg_port = os.getenv("PGPORT") or "5432"
        
        if pg_host and pg_db and pg_user and pg_password:
            DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
            logger.info(f"Constructed DATABASE_URL from Railway variables")
        else:
            # Fallback to DATABASE_URL
            DATABASE_URL = os.getenv("DATABASE_URL")
            logger.info(f"Using Railway DATABASE_URL environment variable")
    else:
        # Local development - use the local PostgreSQL URL
        logger.info("Running in local development environment")
        # Try environment variables first
        pg_user = os.getenv("POSTGRES_USER") or "postgres"
        pg_password = os.getenv("POSTGRES_PASSWORD")
        pg_host = os.getenv("POSTGRES_HOST") or "localhost"
        pg_port = os.getenv("POSTGRES_PORT") or "5432"
        pg_db = os.getenv("POSTGRES_DB") or "orientor_db"
        
        if pg_password:
            # Construct URL from components
            DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
            logger.info(f"Constructed local DATABASE_URL from environment variables")
        else:
            # Fallback to DATABASE_URL
            DATABASE_URL = os.getenv("DATABASE_URL")
            
            # If multiple URLs exist, take the one with localhost
            if DATABASE_URL and "localhost" not in DATABASE_URL:
                # Check if there's a line with localhost in the .env file
                try:
                    with open(".env", "r") as f:
                        for line in f:
                            if line.startswith("DATABASE_URL") and "localhost" in line:
                                DATABASE_URL = line.split("=", 1)[1].strip()
                                logger.info("Using local DATABASE_URL from .env file")
                                break
                except FileNotFoundError:
                    logger.warning("No .env file found")
    
    if not DATABASE_URL:
        logger.error("DATABASE_URL could not be determined!")
        sys.exit(1)
    
    # Ensure correct protocol
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        logger.info("Updated DATABASE_URL to use postgresql:// protocol")
    
    # Log URL (without sensitive info)
    parsed_url = urlparse(DATABASE_URL)
    safe_url = f"{parsed_url.scheme}://{parsed_url.username}:****@{parsed_url.hostname}:{parsed_url.port}/{parsed_url.path.lstrip('/')}"
    logger.info(f"Using database URL: {safe_url}")
    
    return DATABASE_URL

try:
    DATABASE_URL = get_database_url()
    
    # Create engine with connection pooling and timeout settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        connect_args={
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    )
    
    # Test the connection
    try:
        with engine.connect() as conn:
            # Get database info - use text() for SQLAlchemy queries
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
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()