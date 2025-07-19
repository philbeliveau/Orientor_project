#!/usr/bin/env python3
"""
Orientor Platform - Phase 1 Application
Core Features: Authentication, User Profiles, Test Endpoints, Onboarding
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create FastAPI app with minimal configuration
app = FastAPI(
    title="Orientor API - Phase 1",
    description="Core authentication and user management features",
    version="1.0.0-phase1",
)

# Configure CORS for Railway deployment
origins = [
    "http://localhost:3000",  # Frontend development
    "https://navigoproject.vercel.app",  # Production frontend
    "https://*.up.railway.app",  # Railway domains
    "https://*.railway.app",     # Railway domains
    "https://*.vercel.app",      # Vercel domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

try:
    # Import only essential routers for Phase 1
    logger.info("🔄 Importing Phase 1 routers...")
    
    # Core authentication router
    from app.routers.user import router as auth_router
    app.include_router(auth_router)
    logger.info("✅ Auth router imported successfully")
    
    # Test endpoints
    from app.routers.test import router as test_router  
    app.include_router(test_router)
    logger.info("✅ Test router imported successfully")
    
    # User profiles
    try:
        from app.routers.profiles import router as profiles_router
        app.include_router(profiles_router, prefix="/api/v1")
        logger.info("✅ Profiles router imported successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Profiles router not available: {e}")
    
    # Onboarding (if available)
    try:
        from app.routers.onboarding import router as onboarding_router
        app.include_router(onboarding_router)
        logger.info("✅ Onboarding router imported successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Onboarding router not available: {e}")
        
    logger.info("✅ Phase 1 routers loaded successfully")
    
except Exception as e:
    logger.error(f"❌ Error importing routers: {e}")
    # Continue with basic app even if some routers fail

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for Railway health checks"""
    return {
        "message": "Orientor Platform - Phase 1 Active",
        "version": "1.0.0-phase1",
        "status": "operational",
        "features": ["authentication", "user_profiles", "health_checks"]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment monitoring"""
    try:
        return {
            "status": "healthy",
            "message": "Phase 1 deployment operational",
            "version": "1.0.0-phase1"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "error", 
            "detail": str(e)
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Phase 1 startup configuration"""
    try:
        logger.info("🚀 Phase 1 startup initiated")
        
        # Initialize database connection (gracefully handle failures)
        try:
            from app.utils.database import initialize_database
            initialize_database()
            logger.info("✅ Database initialized")
        except Exception as db_e:
            logger.warning(f"⚠️ Database initialization failed (continuing): {str(db_e)}")
        
        logger.info("✅ Phase 1 startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        # Don't fail startup - let Railway handle gracefully

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Phase 1 app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)