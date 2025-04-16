import os
import sys
from dotenv import load_dotenv
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    try:
        # Run Alembic migrations
        logger.info("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Migrations completed successfully!")
            logger.info(f"stdout:\n{result.stdout}")
            if result.stderr:
                logger.info(f"stderr:\n{result.stderr}")
            return True
        else:
            logger.error("Migration failed!")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"An error occurred while running migrations: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    
    # Verify DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        logger.error("DATABASE_URL environment variable is not set!")
        sys.exit(1)
        
    # Run migrations
    success = run_migrations()
    sys.exit(0 if success else 1) 