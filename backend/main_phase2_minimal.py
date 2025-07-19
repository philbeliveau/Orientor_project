#!/usr/bin/env python3
"""
Phase 2 - Minimal with ONLY fallback endpoints
Focus on dashboard functionality without real router dependencies
"""

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
import sys
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create FastAPI app with ONLY fallback endpoints"""
    
    app = FastAPI(
        title="Orientor Platform - Phase 2 Minimal",
        description="Minimal fallback endpoints for dashboard functionality",
        version="2.1.0-minimal",
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

    logger.info("🔧 Creating minimal app with ONLY fallback endpoints...")

    # ESSENTIAL MODELS
    class LoginRequest(BaseModel):
        email: str
        password: str
        
    class Token(BaseModel):
        access_token: str
        token_type: str

    # AUTHENTICATION HELPER
    async def get_current_user_from_token(authorization: Optional[str] = Header(None)):
        """Extract user info from our simple token"""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        try:
            token = authorization.split(" ")[1]
            decoded = base64.b64decode(token).decode()
            email, timestamp = decoded.split(":", 1)
            return {"email": email, "id": 1, "name": email.split("@")[0]}
        except:
            raise HTTPException(status_code=401, detail="Invalid token")

    # FALLBACK LOGIN ENDPOINT
    @app.post("/auth/login", response_model=Token, tags=["auth"])
    async def fallback_login(login_request: LoginRequest):
        """Login endpoint with database authentication"""
        logger.info(f"🔄 Login attempt for: {login_request.email}")
        
        try:
            import bcrypt
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
                
                logger.info(f"✅ Login successful for: {login_request.email}")
                return {"access_token": access_token, "token_type": "bearer"}
                
        except Exception as e:
            logger.error(f"❌ Auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )

    # CRITICAL DASHBOARD ENDPOINTS
    @app.get("/auth/me", tags=["auth"])
    async def get_current_user(current_user=Depends(get_current_user_from_token)):
        """Get current user profile - Frontend expects this after login"""
        logger.info(f"📋 Profile request for: {current_user['email']}")
        return {
            "id": current_user["id"],
            "email": current_user["email"],
            "name": current_user["name"],
            "avatar_url": None,
            "created_at": "2024-01-01T00:00:00Z"
        }

    @app.get("/auth/onboarding-status", tags=["auth"])
    async def get_onboarding_status(current_user=Depends(get_current_user_from_token)):
        """Get user onboarding status - Frontend checks this for navigation"""
        logger.info(f"📋 Onboarding status for: {current_user['email']}")
        return {
            "completed": True,
            "current_step": "completed",
            "steps": {
                "profile": True,
                "assessment": True,
                "goals": True,
                "preferences": True
            }
        }

    @app.get("/api/v1/avatar/me", tags=["avatar"])
    async def get_user_avatar(current_user=Depends(get_current_user_from_token)):
        """Get user avatar - Frontend displays this in header"""
        logger.info(f"🖼️ Avatar request for: {current_user['email']}")
        return {
            "avatar_url": None,
            "has_avatar": False,
            "initials": current_user["name"][:2].upper()
        }

    @app.get("/user-progress/", tags=["progress"])
    async def get_user_progress(current_user=Depends(get_current_user_from_token)):
        """Get user progress - Dashboard shows this"""
        logger.info(f"📊 Progress request for: {current_user['email']}")
        return {
            "overall_progress": 75,
            "courses_completed": 3,
            "assessments_taken": 2,
            "goals_set": 1,
            "last_activity": "2024-07-19T10:00:00Z"
        }

    @app.get("/api/v1/courses", tags=["courses"])
    async def get_courses(current_user=Depends(get_current_user_from_token)):
        """Get available courses - Education page needs this"""
        logger.info(f"📚 Courses request for: {current_user['email']}")
        return {
            "courses": [
                {
                    "id": 1,
                    "title": "Career Exploration Basics",
                    "description": "Learn fundamental career exploration techniques",
                    "progress": 100,
                    "status": "completed"
                },
                {
                    "id": 2,
                    "title": "Interview Preparation",
                    "description": "Master job interview skills",
                    "progress": 50,
                    "status": "in_progress"
                },
                {
                    "id": 3,
                    "title": "Professional Networking",
                    "description": "Build meaningful professional relationships",
                    "progress": 0,
                    "status": "available"
                }
            ],
            "total": 3,
            "completed": 1
        }

    @app.get("/api/v1/career-goals/active", tags=["goals"])
    async def get_active_career_goals(current_user=Depends(get_current_user_from_token)):
        """Get active career goals - Dashboard highlights these"""
        logger.info(f"🎯 Career goals request for: {current_user['email']}")
        return {
            "active_goals": [
                {
                    "id": 1,
                    "title": "Transition to Software Engineering",
                    "target_date": "2025-01-01",
                    "progress": 60,
                    "status": "active",
                    "milestones": [
                        {"title": "Complete Python course", "completed": True},
                        {"title": "Build portfolio project", "completed": False},
                        {"title": "Apply to 10 positions", "completed": False}
                    ]
                }
            ],
            "total": 1
        }

    @app.get("/space/notes", tags=["space"])
    async def get_space_notes(current_user=Depends(get_current_user_from_token)):
        """Get user notes - Space page displays these"""
        logger.info(f"📝 Space notes request for: {current_user['email']}")
        return {
            "notes": [
                {
                    "id": 1,
                    "title": "Career Reflection",
                    "content": "Key insights from today's career exploration session...",
                    "created_at": "2024-07-19T09:00:00Z",
                    "tags": ["reflection", "career"]
                }
            ],
            "total": 1
        }

    @app.get("/peers/compatible", tags=["peers"])
    async def get_compatible_peers(current_user=Depends(get_current_user_from_token)):
        """Get compatible peers - Networking features"""
        logger.info(f"👥 Compatible peers request for: {current_user['email']}")
        return {
            "peers": [
                {
                    "id": 1,
                    "name": "Alex Johnson",
                    "field": "Software Engineering",
                    "compatibility_score": 85,
                    "shared_interests": ["Programming", "Career Change"]
                }
            ],
            "total": 1
        }

    @app.get("/api/tests/holland/user-results", tags=["assessments"])
    async def get_holland_results(current_user=Depends(get_current_user_from_token)):
        """Get Holland test results - Career assessments"""
        logger.info(f"🧪 Holland results request for: {current_user['email']}")
        return {
            "test_taken": True,
            "results": {
                "primary_type": "Investigative",
                "secondary_type": "Artistic",
                "scores": {
                    "realistic": 3,
                    "investigative": 8,
                    "artistic": 7,
                    "social": 5,
                    "enterprising": 4,
                    "conventional": 3
                },
                "career_matches": [
                    "Software Engineer",
                    "Data Scientist",
                    "UX Designer"
                ]
            },
            "taken_at": "2024-07-15T14:30:00Z"
        }

    # BASIC ENDPOINTS
    @app.get("/")
    async def root():
        return {
            "message": "Orientor Platform - Phase 2 Minimal",
            "version": "2.1.0-minimal",
            "status": "operational",
            "endpoints": "fallback_only"
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "message": "Phase 2 Minimal - Fallback endpoints operational",
            "version": "2.1.0-minimal",
            "platform": "minimal_fallback_endpoints"
        }

    logger.info("✅ Minimal app created successfully")
    return app

# Create the app
app = create_app()

@app.on_event("startup")
async def startup_event():
    """Startup configuration"""
    logger.info("🚀 Phase 2 Minimal startup initiated")
    logger.info("🎯 Focus: Essential dashboard endpoints only")
    logger.info("✅ Phase 2 Minimal startup completed")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Phase 2 Minimal on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)