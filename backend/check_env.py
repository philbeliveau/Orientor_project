import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    load_dotenv()
    
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'JWT_SECRET_KEY': 'Secret key for JWT tokens',
        'OPENAI_API_KEY': 'OpenAI API key for chat functionality'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values in logs
            masked_value = value[:5] + '...' if value else 'Not set'
            logger.info(f"{var}: {masked_value}")
        else:
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"- {var}")
        return False
    
    # Additional checks for DATABASE_URL format
    database_url = os.getenv('DATABASE_URL', '')
    if database_url.startswith('postgres://'):
        logger.warning("DATABASE_URL starts with 'postgres://', should be 'postgresql://'")
    
    return True

if __name__ == "__main__":
    check_environment() 