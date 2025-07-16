from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging
from datetime import datetime
from pathlib import Path

# Configure logging for Railway BEFORE importing routers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Railway captures stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

# Import all necessary routers for complete functionality
try:
    from app.routers.user import router as auth_router
    from app.routers.chat import router as chat_router
    from app.routers.conversations import router as conversations_router
    from app.routers.share import router as share_router
    from app.routers.chat_analytics import router as chat_analytics_router
    from app.routers.peers import router as peers_router
    from app.routers.messages import router as messages_router
    from app.routers.profiles import router as profiles_router
    from app.routers.test import router as test_router
    from app.routers.space import router as space_router
    from app.routers.vector_search import router as vector_router
    from app.routers.recommendations import router as recommendations_router
    from app.routers.careers import router as careers_router
    from app.routers.tree import router as tree_router
    from app.routers.tree_paths import router as tree_paths_router
    from app.routers.node_notes import router as node_notes_router
    from app.routers.user_progress import router as user_progress_router
    from app.routers.jobs import router as jobs_router
    from app.routers.program_recommendations import router as program_recommendations_router
    from app.routers.holland_test import router as holland_test_router
    from app.routers.hexaco_test import router as hexaco_test_router
    from app.routers.insight_router import router as insight_router
    from app.routers.competence_tree import router as competence_tree_router
    from app.routers.career_progression import router as career_progression_router
    from app.routers.users import router as users_router
    from app.routers.reflection_router import router as reflection_router
    from app.routers.avatar import router as avatar_router
    from app.routers.onboarding import router as onboarding_router
    from app.routers.education import router as education_router
    from app.routers.school_programs import router as school_programs_router
    from app.routers.courses import router as courses_router
    from app.routers.enhanced_chat import router as enhanced_chat_router
    from app.routers.socratic_chat import router as socratic_chat_router
    from app.routers.career_goals import router as career_goals_router
    from app.routers.llm_career_advisor import router as llm_career_advisor_router
    from app.routers.orientator import router as orientator_router
    ROUTERS_AVAILABLE = True
    logger.info("✅ All routers imported successfully")
except ImportError as e:
    ROUTERS_AVAILABLE = False
    logger.warning(f"⚠️ Some routers could not be imported: {str(e)}")
    # Set None for missing routers - fallback for basic mode
    auth_router = None
    holland_test_router = None
    profiles_router = None
    test_router = None
    conversations_router = None
    chat_router = None
    share_router = None
    chat_analytics_router = None
    peers_router = None
    messages_router = None
    space_router = None
    vector_router = None
    recommendations_router = None
    careers_router = None
    tree_router = None
    tree_paths_router = None
    node_notes_router = None
    user_progress_router = None
    jobs_router = None
    program_recommendations_router = None
    hexaco_test_router = None
    insight_router = None
    competence_tree_router = None
    career_progression_router = None
    users_router = None
    reflection_router = None
    avatar_router = None
    onboarding_router = None
    education_router = None
    school_programs_router = None
    courses_router = None
    enhanced_chat_router = None
    socratic_chat_router = None
    career_goals_router = None
    llm_career_advisor_router = None
    orientator_router = None

# Create a production-ready FastAPI app
app = FastAPI(
    title="Orientor Backend - Railway Deploy",
    description="Production FastAPI backend for Orientor career platform",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENV") != "production" else None,  # Disable docs in production
    redoc_url="/redoc" if os.getenv("ENV") != "production" else None
)

# Configure static files safely
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted from {static_path}")
else:
    logger.warning(f"Static directory not found at {static_path}")

# Configure CORS with Railway-specific origins
origins = [
    "https://navigo-explorer.vercel.app",
    "https://*.vercel.app",
    "https://*.up.railway.app",
    "https://*.railway.app",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://localhost:3000",
]

# Add wildcard for Railway domains if in production
if os.getenv("RAILWAY_ENVIRONMENT") == "production":
    origins.append("*")  # Allow all origins in Railway production for now

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Health check endpoints for Railway
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Orientor Backend is running on Railway!",
        "status": "success",
        "version": "2.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring"""
    try:
        # Basic health check
        return {
            "status": "healthy",
            "service": "orientor-backend",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
            "port": os.getenv("PORT", "8000"),
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "Railway managed"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/api/health")
async def api_health():
    """API-specific health check with database status"""
    try:
        # Check database health
        database_status = "not_connected"
        try:
            # Import database health check function
            from app.utils.database import check_database_health, database_connected
            if check_database_health():
                database_status = "connected"
            elif database_connected:
                database_status = "connected_but_unstable"
            else:
                database_status = "not_connected"
        except ImportError:
            database_status = "not_configured"
        except Exception as db_e:
            database_status = f"error: {str(db_e)[:50]}"
        
        return {
            "status": "ok", 
            "api_version": "v1",
            "endpoints": ["health", "auth", "status"],
            "database": database_status,
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"API unhealthy: {str(e)}")

# Authentication endpoints for frontend compatibility
@app.post("/api/auth/login")
async def login():
    """Mock login endpoint for frontend testing"""
    logger.info("Login endpoint accessed")
    return {
        "message": "Login endpoint working on Railway",
        "token": "railway-test-token-12345",
        "user": {
            "id": 1, 
            "name": "Railway Test User",
            "email": "test@orientor-railway.com"
        },
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
    }

@app.get("/api/auth/me")
async def get_me():
    """Mock user profile endpoint"""
    logger.info("User profile endpoint accessed")
    return {
        "id": 1,
        "name": "Railway Test User", 
        "email": "test@orientor-railway.com",
        "role": "user",
        "platform": "railway",
        "timestamp": datetime.utcnow().isoformat()
    }

# Include all routers if available
if ROUTERS_AVAILABLE:
    try:
        logger.info("🔌 Including routers in the FastAPI app...")
        
        # Include auth router first - it defines dependencies
        if auth_router:
            app.include_router(auth_router)
            logger.info("✅ Auth router included")
        
        # Include profiles router after auth router
        if profiles_router:
            app.include_router(profiles_router)
            logger.info("✅ Profiles router included")
            
        # Include remaining routers
        if test_router:
            app.include_router(test_router)
        if conversations_router:
            app.include_router(conversations_router)
        if chat_router:
            app.include_router(chat_router)
        if share_router:
            app.include_router(share_router)
        if chat_analytics_router:
            app.include_router(chat_analytics_router)
        if peers_router:
            app.include_router(peers_router)
        if messages_router:
            app.include_router(messages_router)
        if space_router:
            app.include_router(space_router)
        if vector_router:
            app.include_router(vector_router)
        if recommendations_router:
            app.include_router(recommendations_router)
        if careers_router:
            app.include_router(careers_router)
        if tree_router:
            app.include_router(tree_router)
        if tree_paths_router:
            app.include_router(tree_paths_router)
        if node_notes_router:
            app.include_router(node_notes_router)
        if user_progress_router:
            app.include_router(user_progress_router)
        if jobs_router:
            app.include_router(jobs_router, prefix="/api/v1")
        if program_recommendations_router:
            app.include_router(program_recommendations_router, prefix="/api/v1")
            
        # CRITICAL: Include Holland test router - this was missing and causing 404 errors
        if holland_test_router:
            app.include_router(holland_test_router)
            logger.info("✅ Holland test router included - /api/tests/holland endpoints now available")
            
        if hexaco_test_router:
            app.include_router(hexaco_test_router)
        if insight_router:
            app.include_router(insight_router)
        if competence_tree_router:
            app.include_router(competence_tree_router, prefix="/api/v1")
        if career_progression_router:
            app.include_router(career_progression_router, prefix="/api/v1")
        if users_router:
            app.include_router(users_router, prefix="/api/v1")
        if reflection_router:
            app.include_router(reflection_router, prefix="/api/v1")
        if avatar_router:
            app.include_router(avatar_router, prefix="/api/v1")
        if onboarding_router:
            app.include_router(onboarding_router, prefix="/api/v1")
        if education_router:
            app.include_router(education_router, prefix="/api/v1")
        if school_programs_router:
            app.include_router(school_programs_router, prefix="/api/v1")
        if courses_router:
            app.include_router(courses_router, prefix="/api/v1")
        if enhanced_chat_router:
            app.include_router(enhanced_chat_router, prefix="/api/v1")
        if socratic_chat_router:
            app.include_router(socratic_chat_router, prefix="/api/v1")
        if career_goals_router:
            app.include_router(career_goals_router, prefix="/api/v1")
        if llm_career_advisor_router:
            app.include_router(llm_career_advisor_router, prefix="/api/v1")
        if orientator_router:
            app.include_router(orientator_router, prefix="/api/v1")
            
        logger.info("✅ All available routers included successfully")
        
    except Exception as e:
        logger.error(f"❌ Error including routers: {str(e)}")
        # Continue with basic functionality even if routers fail to load
else:
    logger.warning("⚠️ Routers not available - running in basic mode")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"404 error for path: {request.url.path}")
    return {
        "error": "Not Found",
        "path": str(request.url.path),
        "message": "The requested endpoint was not found",
        "status_code": 404
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"500 error for path: {request.url.path}, error: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "path": str(request.url.path),
        "message": "An internal server error occurred",
        "status_code": 500
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup configuration"""
    try:
        logger.info("🚀 Starting Orientor Backend on Railway")
        logger.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
        logger.info(f"Port: {os.getenv('PORT', '8000')}")
        logger.info(f"Railway Service ID: {os.getenv('RAILWAY_SERVICE_ID', 'unknown')}")
        logger.info("✅ Application startup completed successfully")
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        # Don't fail startup - let Railway handle the error

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown cleanup"""
    logger.info("🛑 Shutting down Orientor Backend")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting Orientor Backend on {host}:{port}")
    logger.info(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    )