#!/usr/bin/env python3
"""
Railway deployment entry point
Imports the app from backend.main_deploy
"""

import os
import sys

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the app from main_deploy
from main_deploy import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)