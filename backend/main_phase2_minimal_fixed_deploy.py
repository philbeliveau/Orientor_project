#!/usr/bin/env python3
"""
Deploy script for Phase 2 Minimal Fixed version
"""

import os
import sys
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("🚀 Starting Phase 2 Minimal Fixed deployment...")
        
        # Import and run the fixed app
        from main_phase2_minimal_fixed import app
        import uvicorn
        
        # Get port from Railway environment
        port = int(os.environ.get("PORT", 8000))
        
        logger.info(f"🌐 Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        raise