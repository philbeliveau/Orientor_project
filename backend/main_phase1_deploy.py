#!/usr/bin/env python3
"""
Orientor Platform - Phase 1 Railway Deployment
Core Features: Authentication, User Profiles, Health Checks
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory (backend) to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Main function for Phase 2 Chunk 1 Railway deployment"""
    logger.info("🚀 Starting Orientor Platform - Phase 2 Chunk 1 Deployment")
    logger.info("📋 Features: Authentication, User Profiles, Avatar Endpoints, Health Checks")
    
    # Get port from Railway environment
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    
    try:
        # Import Phase 2 Real Platform app
        from main_phase2_real import app
        
        logger.info("✅ Phase 2 Real Platform app imported successfully")
        
        import uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start Phase 1 backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()