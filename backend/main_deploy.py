#!/usr/bin/env python3
"""
Railway Deployment Entry Point - Minimal Viable Deployment
Phase 1: Basic FastAPI + Database connectivity only
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add the backend/app directory to the Python path
backend_path = Path(__file__).parent / "app"
sys.path.insert(0, str(backend_path))

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Railway deployment main function with progressive feature loading
    """
    logger.info("🚀 Starting Orientor Platform - Minimal Deployment")
    
    # Get port from Railway environment
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Railway requires binding to all interfaces
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    
    try:
        # Import the minimal FastAPI app
        from main import app
        logger.info("✅ FastAPI app imported successfully")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except ImportError as e:
        logger.error(f"❌ Failed to import FastAPI app: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()