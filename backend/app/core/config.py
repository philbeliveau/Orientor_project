from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Base configuration
    ENV: str = os.getenv("ENV", "development")
    
    # Database URLs
    DATABASE_URL: Optional[str] = None
    RAILWAY_DATABASE_URL: Optional[str] = os.getenv("RAILWAY_DATABASE_URL")
    LOCAL_DATABASE_URL: Optional[str] = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orientor")

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    @property
    def get_database_url(self) -> str:
        """
        Returns the appropriate database URL based on the environment
        """
        if self.ENV == "production":
            if not self.RAILWAY_DATABASE_URL:
                raise ValueError("RAILWAY_DATABASE_URL must be set in production environment")
            return self.RAILWAY_DATABASE_URL
        return self.LOCAL_DATABASE_URL or ""

    class Config:
        env_file = ".env"
        # Allow extra fields in case we add more environment variables later
        extra = "allow"

# Initialize settings
settings = Settings() 