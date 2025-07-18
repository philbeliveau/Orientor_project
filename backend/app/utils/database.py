import logging
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import Optional
from fastapi import HTTPException
from ..core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create Base class for models
Base = declarative_base()

# Global variables for database connection
engine: Optional[object] = None
SessionLocal: Optional[object] = None
database_connected = False

def create_database_engine():
    """Create database engine with Railway-optimized configuration"""
    global engine
    
    try:
        database_url = settings.get_database_url
        logger.info(f"Attempting to connect to database...")
        
        # Railway-optimized engine configuration
        engine_kwargs = {
            "pool_size": 3,  # Reduced for Railway
            "max_overflow": 5,  # Reduced for Railway
            "pool_timeout": 20,  # Reduced timeout
            "pool_recycle": 1800,
            "pool_pre_ping": True,  # Important for Railway
            "connect_args": {
                "connect_timeout": 10,  # Connection timeout
                "options": "-c timezone=utc"  # Set timezone
            }
        }
        
        # Additional settings for Railway production
        if settings.is_railway:
            engine_kwargs.update({
                "pool_size": 2,  # Even smaller for Railway
                "max_overflow": 3,
                "pool_timeout": 15,
                "echo": False  # Disable SQL logging in production
            })
        
        engine = create_engine(database_url, **engine_kwargs)
        logger.info("✅ Database engine created successfully")
        return engine
        
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {str(e)}")
        raise

def test_database_connection():
    """Test database connection and log information"""
    global database_connected
    
    if not engine:
        logger.error("Database engine not initialized")
        return False
    
    try:
        # Test the connection with timeout
        with engine.connect() as conn:
            # Set a statement timeout
            conn.execute(text("SET statement_timeout = '30s'"))
            
            # Basic connection test
            result = conn.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            
            if test_result[0] == 1:
                logger.info("✅ Database connection test successful")
                
                # Get database information
                try:
                    result = conn.execute(text("SELECT current_database(), current_user, version()"))
                    db_name, db_user, version = result.fetchone()
                    logger.info(f"Database: {db_name}")
                    logger.info(f"User: {db_user}")
                    logger.info(f"PostgreSQL version: {version[:50]}...")  # Truncate long version string
                    
                    # Check if tables exist (with limit)
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        LIMIT 10
                    """))
                    tables = [row[0] for row in result]
                    logger.info(f"Sample tables: {tables[:5]}...")  # Show first 5 tables
                    
                except Exception as info_error:
                    logger.warning(f"Could not get database info: {info_error}")
                
                database_connected = True
                return True
            
    except OperationalError as e:
        logger.error(f"❌ Database connection failed (Operational): {str(e)}")
        database_connected = False
        return False
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed (SQLAlchemy): {str(e)}")
        database_connected = False
        return False
    except Exception as e:
        logger.error(f"❌ Database connection failed (Unexpected): {str(e)}")
        database_connected = False
        return False

def initialize_database():
    """Initialize database connection"""
    global SessionLocal, engine
    
    try:
        # Create engine
        engine = create_database_engine()
        
        # Test connection
        if test_database_connection():
            # Create session factory
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("✅ Database initialization completed successfully")
            return True
        else:
            logger.warning("⚠️ Database connection test failed, but continuing...")
            # Create session factory anyway for graceful degradation
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return False
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        # Create a mock session factory for graceful degradation
        SessionLocal = None
        return False

def get_db():
    """Get database session with enhanced error handling and recovery"""
    global SessionLocal, engine
    
    # Initialize database on first access if not already done
    if not SessionLocal or not engine:
        logger.info("🔌 Initializing database on first access...")
        initialize_database()
    
    if not SessionLocal:
        logger.error("Database session factory not initialized")
        raise Exception("Database not available")
    
    db = None
    try:
        db = SessionLocal()
        # Test the connection before yielding
        db.execute(text("SELECT 1"))
        yield db
    except OperationalError as e:
        logger.error(f"Database operational error: {str(e)}")
        if db:
            db.rollback()
        # Try to reinitialize database connection
        try:
            logger.info("🔄 Attempting to reinitialize database connection...")
            initialize_database()
            if SessionLocal:
                db = SessionLocal()
                db.execute(text("SELECT 1"))
                yield db
            else:
                raise Exception("Database reinitialize failed")
        except Exception as reinit_error:
            logger.error(f"Database reinitialize failed: {str(reinit_error)}")
            raise HTTPException(
                status_code=503, 
                detail="Database service temporarily unavailable"
            )
    except SQLAlchemyError as e:
        logger.error(f"Database SQLAlchemy error: {str(e)}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database query error"
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions from endpoints without wrapping them
        logger.info(f"HTTPException from endpoint: {e.detail}")
        if db:
            db.rollback()
        raise e
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database session error: {str(e)}"
        )
    finally:
        if db:
            try:
                db.close()
            except Exception as close_error:
                logger.warning(f"Error closing database session: {str(close_error)}")

def check_database_health():
    """Check if database is healthy"""
    global database_connected
    
    if not engine or not database_connected:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        database_connected = False
        return False

# Database initialization is now deferred to avoid caching issues
# The database will be initialized when first accessed
logger.info("📌 Database initialization deferred to avoid environment variable caching")