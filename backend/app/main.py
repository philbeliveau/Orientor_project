from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging

# Import routers directly
from app.routers.user import router as auth_router, get_current_user
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
from app.api.endpoints.job_recommendations import router as job_recommendations_router
from app.routers.llm_career_advisor import router as llm_career_advisor_router
from app.routers.orientator import router as orientator_router
from fastapi import FastAPI, HTTPException
from pathlib import Path
# from scripts.model_loader import load_models
from logging.handlers import RotatingFileHandler
from .utils.logging_config import setup_logging

# from app.routers.resume import router as resume_router  # Commented out resume router

# Set up logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Navigo API",
    description="API for the Navigo Career and Skill Tree Explorer",
    version="0.1.0",
)

# Configure static files for avatars
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
origins = [
    "http://localhost:3000",  # Frontend development server
    "http://localhost:8000",  # Backend when served 
    "https://navigoproject.vercel.app",  # Production frontend
    "http://localhost:5173",  # Vite development server
    "https://localhost:3000",  # HTTPS local development
    "https://localhost:5173",  # HTTPS Vite development
    "https://*.up.railway.app",  # Railway domains
    "https://*.railway.app",    # Railway domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Set-Cookie"],
    max_age=600,
)

# Print debug information about routers
try:
    logger.info("======= ROUTER REGISTRATION DETAILS =======")
    logger.info(f"auth_router import path: {auth_router.__module__}")
    logger.info(f"get_current_user import path: {get_current_user.__module__}")
    logger.info(f"profiles_router import path: {profiles_router.__module__}")
    
    logger.info(f"Registering auth_router routes: {[f'{route.path} [{route.methods}]' for route in auth_router.routes]}")
    logger.info(f"Registering profiles_router routes: {[f'{route.path} [{route.methods}]' for route in profiles_router.routes]}")
    logger.info(f"Registering chat_router routes: {[f'{route.path} [{route.methods}]' for route in chat_router.routes]}")
    logger.info(f"Registering peers_router routes: {[f'{route.path} [{route.methods}]' for route in peers_router.routes]}")
    logger.info(f"Registering messages_router routes: {[f'{route.path} [{route.methods}]' for route in messages_router.routes]}")
    logger.info(f"Registering test_router routes: {[f'{route.path} [{route.methods}]' for route in test_router.routes]}")
    logger.info(f"Registering space_router routes: {[f'{route.path} [{route.methods}]' for route in space_router.routes]}")
    logger.info(f"Registering vector_router routes: {[f'{route.path} [{route.methods}]' for route in vector_router.routes]}")
    logger.info(f"Registering recommendations_router routes: {[f'{route.path} [{route.methods}]' for route in recommendations_router.routes]}")
    logger.info(f"Registering careers_router routes: {[f'{route.path} [{route.methods}]' for route in careers_router.routes]}")
    logger.info(f"Registering tree_router routes: {[f'{route.path} [{route.methods}]' for route in tree_router.routes]}")
    logger.info(f"Registering tree_paths_router routes: {[f'{route.path} [{route.methods}]' for route in tree_paths_router.routes]}")
    logger.info(f"Registering node_notes_router routes: {[f'{route.path} [{route.methods}]' for route in node_notes_router.routes]}")
    logger.info(f"Registering user_progress_router routes: {[f'{route.path} [{route.methods}]' for route in user_progress_router.routes]}")
    logger.info(f"Registering holland_test_router routes: {[f'{route.path} [{route.methods}]' for route in holland_test_router.routes]}")
    logger.info(f"Registering hexaco_test_router routes: {[f'{route.path} [{route.methods}]' for route in hexaco_test_router.routes]}")
    logger.info(f"Registering insight_router routes: {[f'{route.path} [{route.methods}]' for route in insight_router.routes]}")
    logger.info(f"Registering orientator_router routes: {[f'{route.path} [{route.methods}]' for route in orientator_router.routes]}")
    logger.info("============================================")
except Exception as e:
    logger.error(f"Error while logging router details: {str(e)}")

# Include routers in the correct order
logger.info("Including routers in the FastAPI app")
# Include auth router first - it defines dependencies
app.include_router(auth_router)
logger.info("Auth router included successfully")
# Include profiles router after auth router
app.include_router(profiles_router, prefix="/api/v1")
logger.info("Profiles router included successfully")
# Include remaining routers  
app.include_router(test_router)
# Mount conversations_router BEFORE chat_router to prioritize specific routes
app.include_router(conversations_router)
app.include_router(chat_router)
app.include_router(share_router)
app.include_router(chat_analytics_router)
app.include_router(peers_router)
app.include_router(messages_router)
app.include_router(space_router)
app.include_router(vector_router)
app.include_router(recommendations_router)
app.include_router(careers_router)
app.include_router(tree_router)
app.include_router(tree_paths_router)
app.include_router(node_notes_router)
app.include_router(user_progress_router)
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(program_recommendations_router, prefix="/api/v1")
app.include_router(holland_test_router)
app.include_router(hexaco_test_router)
app.include_router(insight_router)
app.include_router(competence_tree_router, prefix="/api/v1")
app.include_router(career_progression_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(reflection_router)
app.include_router(avatar_router, prefix="/api/v1")
app.include_router(onboarding_router)
app.include_router(education_router)
app.include_router(school_programs_router)
app.include_router(courses_router)
app.include_router(enhanced_chat_router, prefix="/api/v1")
app.include_router(socratic_chat_router)
app.include_router(career_goals_router)
app.include_router(job_recommendations_router, prefix="/api/v1/jobs")
app.include_router(llm_career_advisor_router)
app.include_router(orientator_router, prefix="/api")
logger.info("All routers included successfully")

# Explicitly capture route after including it
logger.info("=== Available Routes ===")
for route in app.routes:
    if hasattr(route, 'methods'):
        logger.info(f"Route: {route.path}, Methods: {route.methods}")
    else:
        logger.info(f"Mount: {route.path}")
logger.info("======================")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Navigo API. Go to /docs for API documentation."}

# @app.get("/api/health") # /api/health
# def health_check():
#     try:
#         return {"status": "ok"}
#     except Exception as e:
#         logger.error(f"Health check failed: {str(e)}")
#         return {"status": "error", "detail": str(e)}

@app.get("/health")
async def health_check():
    try:
        # Basic health check without model dependency
        return {"status": "healthy", "message": "Service is running"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "error", "detail": str(e)}

# Startup event with error handling
@app.on_event("startup")
async def startup_event():
    """Application startup configuration"""
    try:
        logger.info("🚀 Application startup initiated")
        
        # Load models if available
        try:
            load_models()
            logger.info("✅ Models loaded successfully")
        except Exception as model_e:
            logger.warning(f"⚠️ Model loading failed (continuing anyway): {str(model_e)}")
        
        # Initialize database if not already done
        try:
            from .utils.database import initialize_database, database_connected
            if not database_connected:
                logger.info("🔌 Attempting database initialization...")
                initialize_database()
        except Exception as db_e:
            logger.warning(f"⚠️ Database initialization failed (continuing anyway): {str(db_e)}")
        
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        # Don't fail startup - let Railway handle gracefully
        pass

def load_models():
    """Load ML models with graceful error handling"""
    try:
        logger.info("Loading models...")
        
        # Try to load models from scripts if available
        try:
            from scripts.model_loader import load_models as script_load_models
            script_load_models()
            logger.info("Models loaded from scripts")
        except ImportError:
            logger.info("No model loader script found, skipping model loading")
        except Exception as e:
            logger.warning(f"Script model loading failed: {str(e)}")
        
        # Try to load any other models
        # Add your specific model loading code here
        
        logger.info("Model loading process completed")
        
    except Exception as e:
        logger.error(f"Error in load_models: {str(e)}")
        # Don't raise the exception, just log it for graceful degradation
        pass

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000) #, reload=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Railway-assigned port
    print(f"🚀 Starting app on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
