#!/usr/bin/env python3
"""
Minimal Railway Test - Just FastAPI with no dependencies
"""

from fastapi import FastAPI
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create minimal FastAPI app
app = FastAPI(
    title="Minimal Railway Test",
    version="minimal"
)

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {
        "message": "Minimal Railway test working",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {
        "status": "healthy",
        "message": "Minimal test working"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Minimal app starting up")
    port = os.environ.get("PORT", "unknown")
    logger.info(f"PORT environment variable: {port}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting minimal app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)