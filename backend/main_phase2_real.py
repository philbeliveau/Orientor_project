#!/usr/bin/env python3
"""
Phase 2 - Real Platform Integration
Uses actual Orientor platform components with reduced dependencies
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging
import sys
from pathlib import Path

# Add app directory to path for imports
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create FastAPI app with real platform components"""
    
    app = FastAPI(
        title="Orientor Platform - Phase 2 Real",
        description="Real platform components with reduced AI dependencies",
        version="2.0.0-real",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )

    # Phase 2: Import REAL PLATFORM routers with smart dependency handling
    logger.info("🔧 Loading real platform routers...")
    
    # ✅ CONFIRMED WORKING ROUTERS (from test results)
    working_routers = [
        ("app.routers.user", "/auth", "auth", "Auth router"),
        ("app.routers.test", "/api", "test", "Test router"),  
        ("app.routers.avatar", "/api/v1/avatar", "avatar", "Avatar router"),
        ("app.routers.onboarding", "/api/v1", "onboarding", "Onboarding router"),
        ("app.routers.user_progress", "/user-progress", "progress", "User progress router"),
        ("app.routers.courses", "/api/v1", "courses", "Courses router"),
        ("app.routers.space", "/space", "space", "Space router"),
    ]
    
    # Load confirmed working routers
    loaded_routers = 0
    for module_name, prefix, tag, description in working_routers:
        try:
            module = __import__(module_name, fromlist=['router'])
            if hasattr(module, 'router'):
                app.include_router(module.router, prefix=prefix, tags=[tag])
                logger.info(f"   ✅ {description} loaded")
                loaded_routers += 1
            else:
                logger.warning(f"   ⚠️ {description}: No router attribute")
        except ImportError as e:
            logger.warning(f"   ❌ {description}: {e}")
    
    # ⚠️ DEPENDENCY-HEAVY ROUTERS (load with fallbacks)
    dependency_heavy_routers = [
        ("app.routers.profiles", "/api/v1", "profiles", "Profiles router", "sentence_transformers"),
        ("app.routers.career_goals", "/api/v1", "career_goals", "Career goals router", "pinecone"), 
        ("app.routers.peers", "/peers", "peers", "Peers router", "sentence_transformers"),
    ]
    
    logger.info("🧠 Loading AI-dependent routers with fallbacks...")
    for module_name, prefix, tag, description, missing_dep in dependency_heavy_routers:
        try:
            module = __import__(module_name, fromlist=['router'])
            if hasattr(module, 'router'):
                app.include_router(module.router, prefix=prefix, tags=[tag])
                logger.info(f"   ✅ {description} loaded (AI features may be limited)")
                loaded_routers += 1
            else:
                logger.warning(f"   ⚠️ {description}: No router attribute")
        except ImportError as e:
            logger.warning(f"   🚫 {description}: Missing {missing_dep} - will implement fallback in Phase 3")
    
    # 🤖 AI/ML ROUTERS - Load with fallbacks
    logger.info("🧠 Loading AI routers with fallbacks...")
    
    try:
        # Holland personality test (might work without heavy AI)
        from app.routers.holland_test import router as holland_test_router
        app.include_router(holland_test_router, prefix="/api/tests/holland", tags=["assessments"])
        logger.info("   ✅ Holland test router loaded")
    except ImportError as e:
        logger.warning(f"   ⚠️ Holland test router failed: {e}")
    
    try:
        # Job recommendations (will need mocking)
        from app.api.endpoints.job_recommendations import router as job_recommendations_router
        app.include_router(job_recommendations_router, prefix="/api/v1/jobs", tags=["jobs"])
        logger.info("   ✅ Job recommendations router loaded")
    except ImportError as e:
        logger.warning(f"   ⚠️ Job recommendations router failed: {e}")
        
    # Static files
    try:
        static_dir = Path("static")
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory="static"), name="static")
            logger.info("   ✅ Static files mounted")
    except Exception as e:
        logger.warning(f"   ⚠️ Static files failed: {e}")

    # FALLBACK AUTH ENDPOINTS - In case real auth router fails to load
    from pydantic import BaseModel
    
    class LoginRequest(BaseModel):
        email: str
        password: str
        
    class Token(BaseModel):
        access_token: str
        token_type: str

    @app.post("/auth/login", response_model=Token, tags=["fallback-auth"])
    async def fallback_login(login_request: LoginRequest):
        """Fallback login endpoint in case real auth router fails to load"""
        logger.info(f"🔄 Fallback login attempt for: {login_request.email}")
        
        # Self-contained auth logic
        try:
            import bcrypt
            import base64
            from datetime import datetime
            from sqlalchemy import create_engine, text
            
            # Database setup
            DATABASE_URL = (
                os.getenv("DATABASE_URL") or 
                os.getenv("DATABASE_PRIVATE_URL") or 
                os.getenv("POSTGRES_URL") or
                os.getenv("RAILWAY_DATABASE_URL")
            )
            
            if not DATABASE_URL:
                logger.error("❌ No database URL available")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database unavailable"
                )
            
            # Connect to database
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            
            with engine.connect() as conn:
                # Find user
                result = conn.execute(
                    text("SELECT id, email, encrypted_password, name FROM users WHERE email = :email LIMIT 1"),
                    {"email": login_request.email}
                )
                user_row = result.fetchone()
                
                if not user_row:
                    logger.warning(f"User not found: {login_request.email}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password"
                    )
                
                user_id, email, encrypted_password, name = user_row
                logger.info(f"✅ Found user: {email}")
                
                # Verify password
                if encrypted_password and encrypted_password.startswith('$2b$'):
                    # Bcrypt verification
                    password_valid = bcrypt.checkpw(
                        login_request.password.encode('utf-8'), 
                        encrypted_password.encode('utf-8')
                    )
                    logger.info(f"🔐 Bcrypt verification: {password_valid}")
                else:
                    # Plain text fallback
                    password_valid = encrypted_password == login_request.password
                    logger.info(f"🔓 Plain text verification: {password_valid}")
                
                if not password_valid:
                    logger.warning(f"Password verification failed for: {login_request.email}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password"
                    )
                
                # Create simple token
                token_data = f"{email}:{datetime.utcnow().isoformat()}"
                access_token = base64.b64encode(token_data.encode()).decode()
                
                logger.info(f"✅ Fallback login successful for: {login_request.email}")
                return {"access_token": access_token, "token_type": "bearer"}
                
        except Exception as e:
            logger.error(f"❌ Fallback auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Orientor Platform - Phase 2 Real Components",
            "version": "2.0.0-real",
            "status": "operational",
            "components": "real_platform_with_reduced_ai"
        }

    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "message": "Phase 2 Real Platform operational",
            "version": "2.0.0-real",
            "platform": "real_orientor_components"
        }

    return app

# Create the app
app = create_app()

@app.on_event("startup")
async def startup_event():
    """Startup configuration"""
    logger.info("🚀 Phase 2 Real Platform startup initiated")
    logger.info("🔧 Using real Orientor platform components")
    logger.info("💡 AI features: lightweight/mocked for Phase 2")
    logger.info("✅ Phase 2 Real Platform startup completed")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Phase 2 Real Platform on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)