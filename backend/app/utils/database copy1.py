from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Print environment variables for debugging
print(f"ENV DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"ENV POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD')}")

# Get DATABASE_URL from environment or construct it
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # If DATABASE_URL is provided, ensure it uses psycopg2
    if "postgresql://" in DATABASE_URL and "psycopg2" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    
    # If DATABASE_URL contains "db" as host, replace it with "localhost"
    if "@db:" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("@db:", "@localhost:")
    
    print(f"Using provided DATABASE_URL (possibly modified): {DATABASE_URL.replace(os.getenv('POSTGRES_PASSWORD', ''), '****')}")
else:
    # If no DATABASE_URL is provided, construct it from individual components
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Mac.phil.007")
    POSTGRES_HOST = "localhost"  # Force localhost
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "orientor_db")
    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    print(f"Constructed new DATABASE_URL: {DATABASE_URL.replace(POSTGRES_PASSWORD, '****')}")

# Force the password to be correct
DATABASE_URL = DATABASE_URL.replace(":password@", ":Mac.phil.007@")

# Log connection details (without password)
print(f"FINAL DATABASE_URL: {DATABASE_URL.replace('Mac.phil.007', '****')}")
logger.info(f"Using database URL: {DATABASE_URL.replace('Mac.phil.007', '****')}")

try:
    print(f"Attempting to connect with URL: {DATABASE_URL.replace('Mac.phil.007', '****')}")
    engine = create_engine(DATABASE_URL)
    # Test the connection
    with engine.connect() as conn:
        logger.info("Successfully connected to the database!")
except Exception as e:
    logger.error(f"Failed to connect to the database: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()