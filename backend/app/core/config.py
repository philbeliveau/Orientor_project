from pydantic_settings import BaseSettings
from typing import Optional
import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file (for local development)
load_dotenv()

class Settings(BaseSettings):
    # Base configuration
    ENV: str = os.getenv("ENV", "development")
    RAILWAY_ENVIRONMENT: Optional[str] = os.getenv("RAILWAY_ENVIRONMENT")
    
    # Database URLs with Railway priority
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DATABASE_PUBLIC_URL: Optional[str] = os.getenv("DATABASE_PUBLIC_URL")  # Railway fallback
    RAILWAY_DATABASE_URL: Optional[str] = os.getenv("RAILWAY_DATABASE_URL")
    LOCAL_DATABASE_URL: Optional[str] = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orientor")

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-secret-key-replace-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Railway specific settings
    PORT: int = int(os.getenv("PORT", "8000"))
    RAILWAY_SERVICE_ID: Optional[str] = os.getenv("RAILWAY_SERVICE_ID")

    @property
    def get_database_url(self) -> str:
        """
        Returns the database URL with Railway prioritization
        """
        # Priority order for database URL selection
        if self.RAILWAY_ENVIRONMENT:
            # Running on Railway - prefer Railway database URLs
            if self.DATABASE_URL:
                logger.info("Using DATABASE_URL for Railway deployment")
                return self.DATABASE_URL
            elif self.DATABASE_PUBLIC_URL:
                logger.info("Using DATABASE_PUBLIC_URL fallback for Railway")
                return self.DATABASE_PUBLIC_URL
            elif self.RAILWAY_DATABASE_URL:
                logger.info("Using RAILWAY_DATABASE_URL for Railway")
                return self.RAILWAY_DATABASE_URL
            else:
                logger.warning("No Railway database URL found, using local fallback")
                return self.LOCAL_DATABASE_URL
        else:
            # Local development
            if self.DATABASE_URL:
                logger.info("Using DATABASE_URL for local development")
                return self.DATABASE_URL
            else:
                logger.info("Using LOCAL_DATABASE_URL for local development")
                return self.LOCAL_DATABASE_URL

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.RAILWAY_ENVIRONMENT == "production" or self.ENV == "production"

    @property
    def is_railway(self) -> bool:
        """Check if running on Railway"""
        return self.RAILWAY_ENVIRONMENT is not None

    def log_config(self):
        """Log current configuration (safely, without secrets)"""
        logger.info("=== Configuration Summary ===")
        logger.info(f"Environment: {self.ENV}")
        logger.info(f"Railway Environment: {self.RAILWAY_ENVIRONMENT}")
        logger.info(f"Port: {self.PORT}")
        logger.info(f"Is Production: {self.is_production}")
        logger.info(f"Is Railway: {self.is_railway}")
        logger.info(f"Database URL configured: {bool(self.get_database_url)}")
        logger.info(f"OpenAI API Key configured: {bool(self.OPENAI_API_KEY)}")
        logger.info("=============================")

    class Config:
        env_file = ".env"
        # Allow extra fields in case we add more environment variables later
        extra = "allow"

# Initialize settings
settings = Settings()

# Log configuration on module import
try:
    settings.log_config()
except Exception as e:
    logger.error(f"Error logging configuration: {e}") 