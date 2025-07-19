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
        version="2.1.1-minimal-fixed",
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
        
    class RegisterRequest(BaseModel):
        email: str
        password: str
        name: str
        
    class Token(BaseModel):
        access_token: str
        token_type: str
        user_id: int

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

    # AUTHENTICATION ENDPOINTS
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
                # Find user with onboarding status
                result = conn.execute(
                    text("SELECT id, email, encrypted_password, name, onboarding_completed FROM users WHERE email = :email LIMIT 1"),
                    {"email": login_request.email}
                )
                user_row = result.fetchone()
                
                if not user_row:
                    logger.warning(f"User not found: {login_request.email}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password"
                    )
                
                user_id, email, encrypted_password, name, onboarding_completed = user_row
                logger.info(f"✅ Found user: {email}")
                
                # Verify password
                if encrypted_password and encrypted_password.startswith('$2b$'):
                    password_valid = bcrypt.checkpw(
                        login_request.password.encode('utf-8'), 
                        encrypted_password.encode('utf-8')
                    )
                    logger.info(f"🔐 Bcrypt verification: {password_valid}")
                else:
                    password_valid = encrypted_password == login_request.password
                    logger.info(f"🔓 Plain text verification: {password_valid}")
                
                if not password_valid:
                    logger.warning(f"Password verification failed for: {login_request.email}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password"
                    )
                
                # Create token with user info
                token_data = f"{email}:{user_id}:{onboarding_completed}:{datetime.utcnow().isoformat()}"
                access_token = base64.b64encode(token_data.encode()).decode()
                
                logger.info(f"✅ Login successful for: {login_request.email}")
                return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}
                
        except Exception as e:
            logger.error(f"❌ Auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )

    @app.post("/auth/register", response_model=Token, tags=["auth"])
    async def fallback_register(register_request: RegisterRequest):
        """Register new user endpoint"""
        logger.info(f"🔄 Registration attempt for: {register_request.email}")
        
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
                # Check if user already exists
                result = conn.execute(
                    text("SELECT email FROM users WHERE email = :email LIMIT 1"),
                    {"email": register_request.email}
                )
                existing_user = result.fetchone()
                
                if existing_user:
                    logger.warning(f"User already exists: {register_request.email}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User already exists"
                    )
                
                # Hash password
                hashed_password = bcrypt.hashpw(
                    register_request.password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                # Create new user
                result = conn.execute(
                    text("""
                        INSERT INTO users (email, encrypted_password, name, onboarding_completed, created_at) 
                        VALUES (:email, :password, :name, :onboarding, :created_at)
                        RETURNING id
                    """),
                    {
                        "email": register_request.email,
                        "password": hashed_password,
                        "name": register_request.name,
                        "onboarding": False,  # New users need onboarding
                        "created_at": datetime.utcnow()
                    }
                )
                new_user_id = result.fetchone()[0]
                conn.commit()
                
                # Create token
                token_data = f"{register_request.email}:{new_user_id}:False:{datetime.utcnow().isoformat()}"
                access_token = base64.b64encode(token_data.encode()).decode()
                
                logger.info(f"✅ Registration successful for: {register_request.email}")
                return {"access_token": access_token, "token_type": "bearer", "user_id": new_user_id}
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration service error"
            )

    # ENHANCED AUTH HELPER WITH ONBOARDING INFO
    async def get_current_user_with_onboarding(authorization: Optional[str] = Header(None)):
        """Extract user info including onboarding status from token"""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        try:
            token = authorization.split(" ")[1]
            decoded = base64.b64decode(token).decode()
            email, user_id, onboarding_completed, timestamp = decoded.split(":", 3)
            return {
                "email": email, 
                "id": int(user_id), 
                "name": email.split("@")[0],
                "onboarding_completed": onboarding_completed.lower() == 'true'
            }
        except:
            raise HTTPException(status_code=401, detail="Invalid token")

    # CRITICAL DASHBOARD ENDPOINTS
    @app.get("/auth/me", tags=["auth"])
    async def get_current_user(current_user=Depends(get_current_user_with_onboarding)):
        """Get current user profile - Frontend expects this after login"""
        logger.info(f"📋 Profile request for: {current_user['email']}")
        return {
            "id": current_user["id"],
            "email": current_user["email"],
            "name": current_user["name"],
            "avatar_url": None,
            "created_at": "2024-01-01T00:00:00Z",
            "onboarding_completed": current_user["onboarding_completed"]
        }

    @app.get("/auth/onboarding-status", tags=["auth"])
    async def get_onboarding_status(current_user=Depends(get_current_user_with_onboarding)):
        """Get user onboarding status - Frontend checks this for navigation"""
        logger.info(f"📋 Onboarding status for: {current_user['email']}")
        
        # Return status based on user's onboarding_completed field
        if current_user["onboarding_completed"]:
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
        else:
            return {
                "completed": False,
                "current_step": "profile",
                "steps": {
                    "profile": False,
                    "assessment": False,
                    "goals": False,
                    "preferences": False
                }
            }

    @app.post("/auth/onboarding-complete", tags=["auth"])
    async def complete_onboarding(current_user=Depends(get_current_user_with_onboarding)):
        """Mark user's onboarding as complete - Frontend calls this when onboarding finishes"""
        logger.info(f"🎉 Completing onboarding for: {current_user['email']}")
        
        try:
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
            
            # Connect to database and update onboarding status
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            
            with engine.connect() as conn:
                # Update onboarding_completed to true
                result = conn.execute(
                    text("UPDATE users SET onboarding_completed = :completed WHERE id = :user_id"),
                    {"completed": True, "user_id": current_user["id"]}
                )
                conn.commit()
                
                logger.info(f"✅ Onboarding marked complete for user: {current_user['email']}")
                
                return {
                    "message": "Onboarding completed successfully",
                    "onboarding_completed": True,
                    "user_id": current_user["id"]
                }
                
        except Exception as e:
            logger.error(f"❌ Error completing onboarding: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete onboarding"
            )

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

    @app.get("/api/v1/jobs/recommendations/me", tags=["jobs"])
    async def get_job_recommendations(current_user=Depends(get_current_user_from_token), top_k: int = 3):
        """Get job recommendations - Dashboard displays these"""
        logger.info(f"💼 Job recommendations request for: {current_user['email']} (top_k: {top_k})")
        return {
            "recommendations": [
                {
                    "id": 1,
                    "title": "Senior Software Engineer",
                    "company": "TechCorp Inc.",
                    "location": "Remote",
                    "match_score": 95,
                    "salary_range": "$120,000 - $160,000",
                    "description": "Build scalable web applications using modern technologies",
                    "required_skills": ["Python", "React", "PostgreSQL"],
                    "match_reasons": ["Strong Python background", "Leadership experience"]
                },
                {
                    "id": 2,
                    "title": "Full Stack Developer",
                    "company": "Startup Innovations",
                    "location": "San Francisco, CA",
                    "match_score": 88,
                    "salary_range": "$90,000 - $130,000",
                    "description": "Join our fast-growing team building the future of education",
                    "required_skills": ["JavaScript", "Node.js", "React"],
                    "match_reasons": ["Full-stack experience", "Education sector interest"]
                },
                {
                    "id": 3,
                    "title": "Data Scientist",
                    "company": "Analytics Pro",
                    "location": "New York, NY",
                    "match_score": 82,
                    "salary_range": "$110,000 - $150,000",
                    "description": "Apply machine learning to solve complex business problems",
                    "required_skills": ["Python", "Machine Learning", "SQL"],
                    "match_reasons": ["Analytical mindset", "Python expertise"]
                }
            ][:top_k],
            "total_available": 15,
            "last_updated": "2024-07-19T10:00:00Z"
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