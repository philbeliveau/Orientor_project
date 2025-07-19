#!/usr/bin/env python3
"""
Railway Backend Deployment Entry Point
This file ensures Railway detects this as a Python backend project
"""

import os
import sys
import logging
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function for Railway deployment"""
    logger.info("🚀 Starting Orientor Backend on Railway")
    
    # Get port from Railway environment
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    
    try:
        # Import FastAPI app from backend
        sys.path.insert(0, str(backend_dir / "app"))
        from main import app
        
        import uvicorn
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()