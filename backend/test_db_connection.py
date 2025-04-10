import os
import sys
import socket
import time
import logging
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_network_connection(host, port, timeout=5):
    """Test if we can establish a socket connection to a host:port."""
    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, int(port)))
        elapsed = (time.time() - start_time) * 1000  # ms
        if result == 0:
            logger.info(f"✅ Network connection to {host}:{port} successful (took {elapsed:.2f}ms)")
            return True
        else:
            logger.error(f"❌ Network connection to {host}:{port} failed with code {result} (took {elapsed:.2f}ms)")
            return False
    except socket.gaierror:
        logger.error(f"❌ Network connection failed: hostname {host} could not be resolved")
        return False
    except socket.timeout:
        logger.error(f"❌ Network connection to {host}:{port} timed out after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"❌ Network connection error: {str(e)}")
        return False
    finally:
        sock.close()

def test_db_connection(db_url, connection_name=""):
    """Test database connection using SQLAlchemy."""
    try:
        # Parse URL for network test
        parsed_url = urlparse(db_url)
        host = parsed_url.hostname
        port = parsed_url.port or 5432
        
        # Test network connectivity first
        if not test_network_connection(host, port):
            return False
        
        # Create SQLAlchemy engine with timeout
        start_time = time.time()
        engine = create_engine(
            db_url, 
            connect_args={"connect_timeout": 10},
            pool_pre_ping=True
        )
        
        # Try connecting and getting db info
        with engine.connect() as conn:
            elapsed = (time.time() - start_time) * 1000  # ms
            
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar().split()[1]
            
            # Get tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            logger.info(f"✅ {connection_name} PostgreSQL connection successful!")
            logger.info(f"   Connection time: {elapsed:.2f}ms")
            logger.info(f"   PostgreSQL version: {version}")
            logger.info(f"   Available tables: {tables}")
            return True
            
    except Exception as e:
        logger.error(f"❌ {connection_name} PostgreSQL connection failed: {str(e)}")
        return False

def main():
    """Test both local and Railway database connections."""
    # Track successful connections
    success = False
    
    # Check for Railway environment
    railway_vars = {
        "PGHOST": os.getenv("PGHOST"),
        "PGDATABASE": os.getenv("PGDATABASE"),
        "PGUSER": os.getenv("PGUSER"),
        "PGPASSWORD": os.getenv("PGPASSWORD"),
        "PGPORT": os.getenv("PGPORT", "5432")
    }
    
    # Check if Railway variables are set
    missing_vars = [var for var, value in railway_vars.items() if not value]
    
    if not missing_vars:
        logger.info("✅ Found Railway PostgreSQL environment variables")
        logger.info("\nTesting Railway PostgreSQL connection...")
        
        # Construct Railway DB URL
        railway_url = f"postgresql://{railway_vars['PGUSER']}:{railway_vars['PGPASSWORD']}@{railway_vars['PGHOST']}:{railway_vars['PGPORT']}/{railway_vars['PGDATABASE']}"
        if test_db_connection(railway_url, "Railway"):
            success = True
    else:
        logger.warning("❌ Railway PostgreSQL environment variables not found")
        logger.warning(f"   Missing variables: {', '.join(missing_vars)}")
    
    # Check for local DATABASE_URL
    local_db_url = os.getenv("DATABASE_URL")
    if local_db_url:
        logger.info("Found DATABASE_URL environment variable")
        logger.info("\nTesting local PostgreSQL connection...")
        if test_db_connection(local_db_url, "Local"):
            success = True
    else:
        # Try to construct from individual variables
        pg_user = os.getenv("POSTGRES_USER", "postgres")
        pg_password = os.getenv("POSTGRES_PASSWORD")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_db = os.getenv("POSTGRES_DB", "orientor_db")
        
        if pg_password:
            logger.info("Found individual PostgreSQL environment variables")
            logger.info("\nTesting local PostgreSQL connection...")
            local_db_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
            if test_db_connection(local_db_url, "Local"):
                success = True
        else:
            logger.error("❌ No database connection information found")
    
    logger.info("")
    if success:
        logger.info("✅ At least one database connection was successful")
        return 0
    else:
        logger.error("❌ All database connection attempts failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 