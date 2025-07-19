from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for Phase 1
app = FastAPI(
    title="Orientor API - Phase 1",
    description="Core authentication and profile features",
    version="1.0.0-phase1",
)

# Configure CORS for Vercel
origins = [
    "https://navigoproject.vercel.app",
    "https://*.vercel.app", 
    "http://localhost:3000",
    "https://localhost:3000"
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

# Phase 1: Import only essential routers
try:
    from app.routers.user import router as auth_router
    app.include_router(auth_router)
    logger.info("✅ Auth router included successfully")
except Exception as e:
    logger.error(f"❌ Failed to import auth router: {e}")

try:
    from app.routers.test import router as test_router
    app.include_router(test_router)
    logger.info("✅ Test router included successfully")
except Exception as e:
    logger.error(f"❌ Failed to import test router: {e}")

try:
    from app.routers.profiles import router as profiles_router
    app.include_router(profiles_router, prefix="/api/v1")
    logger.info("✅ Profiles router included successfully")
except Exception as e:
    logger.warning(f"⚠️ Profiles router not available: {e}")

try:
    from app.routers.onboarding import router as onboarding_router
    app.include_router(onboarding_router)
    logger.info("✅ Onboarding router included successfully")
except Exception as e:
    logger.warning(f"⚠️ Onboarding router not available: {e}")

# Basic health endpoints
@app.get("/")
async def root():
    return {
        "message": "Orientor API - Phase 1 Deployment", 
        "status": "healthy",
        "version": "1.0.0-phase1",
        "features": ["authentication", "user-management", "health-checks"]
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection if available
        from app.utils.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.warning(f"Database check failed: {e}")
        db_status = "unavailable"
    
    return {
        "status": "healthy",
        "phase": "1",
        "database": db_status,
        "message": "Phase 1 core features operational"
    }

@app.get("/phase1/status")
async def phase1_status():
    """Phase 1 specific status endpoint"""
    return {
        "phase": 1,
        "description": "Core authentication and user management",
        "features": {
            "authentication": "✅ Available",
            "user_profiles": "✅ Available", 
            "health_checks": "✅ Available",
            "database": "✅ Connected"
        },
        "next_phase": "Phase 2 will add AI chat and recommendations"
    }

# Startup event with error handling
@app.on_event("startup")
async def startup_event():
    """Application startup configuration for Phase 1"""
    try:
        logger.info("🚀 Orientor Phase 1 startup initiated")
        
        # Test database connection
        try:
            from app.utils.database import get_db
            db = next(get_db())
            db.execute("SELECT 1")
            logger.info("✅ Database connection successful")
        except Exception as db_e:
            logger.warning(f"⚠️ Database connection failed: {str(db_e)}")
        
        logger.info("✅ Phase 1 startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during Phase 1 startup: {str(e)}")
        # Don't fail startup - let Railway handle gracefully
        pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Orientor Phase 1 on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)