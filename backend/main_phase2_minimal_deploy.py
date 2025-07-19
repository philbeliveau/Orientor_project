#!/usr/bin/env python3
"""
Railway deployment entry point - Phase 2 Minimal
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for Railway deployment"""
    
    logger.info("🚁 Railway Phase 2 Minimal deployment starting...")
    
    # Import and run the minimal app
    try:
        from main_phase2_minimal import app
        import uvicorn
        
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"🚀 Starting on port {port}")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()