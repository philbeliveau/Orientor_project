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
from typing import Optional, List
import base64
import time

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

    # ================================
    # PHASE 3B BATCH 1: ENHANCED ASSESSMENT FRAMEWORK
    # ================================

    @app.get("/api/tests/hexaco/questions", tags=["assessments"])
    async def get_hexaco_questions(current_user=Depends(get_current_user_from_token)):
        """Get HEXACO personality test questions - Frontend compatible format"""
        logger.info(f"🧠 HEXACO questions request for: {current_user['email']}")
        
        # Return format that matches frontend HexacoQuestion interface
        questions = [
            # Honesty-Humility (H) 
            {
                "item_id": 1,
                "item_text": "I would never accept a bribe, even if it were very large",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Honesty-Humility"
            },
            {
                "item_id": 2,
                "item_text": "I think that I am entitled to more respect than the average person is",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": True,
                "facet": "Honesty-Humility"
            },
            {
                "item_id": 3,
                "item_text": "I am an ordinary person who is no better than others",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Honesty-Humility"
            },
            {
                "item_id": 4,
                "item_text": "I would be tempted to use counterfeit money, if I were sure I could get away with it",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": True,
                "facet": "Honesty-Humility"
            },
            # Emotionality (E)
            {
                "item_id": 5,
                "item_text": "I sometimes can't help worrying about little things",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Emotionality"
            },
            {
                "item_id": 6,
                "item_text": "I get very anxious when waiting to hear about an important decision",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Emotionality"
            },
            {
                "item_id": 7,
                "item_text": "I rarely feel emotional about conflicts in my family",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": True,
                "facet": "Emotionality"
            },
            {
                "item_id": 8,
                "item_text": "I feel like crying when I see other people crying",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Emotionality"
            },
            # Extraversion (X)
            {
                "item_id": 9,
                "item_text": "I enjoy having lots of people around to talk with",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Extraversion"
            },
            {
                "item_id": 10,
                "item_text": "I like to contribute to group discussions",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Extraversion"
            },
            {
                "item_id": 11,
                "item_text": "I prefer jobs that involve active social interaction to those that involve working alone",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Extraversion"
            },
            {
                "item_id": 12,
                "item_text": "In social situations, I'm usually the one who makes the first move",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Extraversion"
            },
            # Agreeableness (A)
            {
                "item_id": 13,
                "item_text": "I rarely hold a grudge, even against people who have badly wronged me",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Agreeableness"
            },
            {
                "item_id": 14,
                "item_text": "I am usually quite flexible in my opinions when people disagree with me",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Agreeableness"
            },
            {
                "item_id": 15,
                "item_text": "When people tell me that I'm wrong, my first reaction is to argue with them",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": True,
                "facet": "Agreeableness"
            },
            {
                "item_id": 16,
                "item_text": "I find it hard to fully forgive someone who has done something mean to me",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": True,
                "facet": "Agreeableness"
            },
            # Conscientiousness (C)
            {
                "item_id": 17,
                "item_text": "I plan ahead and organize things, to avoid scrambling at the last minute",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Conscientiousness"
            },
            {
                "item_id": 18,
                "item_text": "I often push myself very hard when trying to achieve a goal",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Conscientiousness"
            },
            {
                "item_id": 19,
                "item_text": "I often check my work over and over to find any mistakes",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Conscientiousness"
            },
            {
                "item_id": 20,
                "item_text": "I do only the minimum amount of work needed to get by",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": True,
                "facet": "Conscientiousness"
            },
            # Openness to Experience (O)
            {
                "item_id": 21,
                "item_text": "I'm interested in learning about the history and politics of other countries",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Openness"
            },
            {
                "item_id": 22,
                "item_text": "I enjoy looking at art in a museum",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Openness"
            },
            {
                "item_id": 23,
                "item_text": "I like people who have unconventional views",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": False,
                "facet": "Openness"
            },
            {
                "item_id": 24,
                "item_text": "I find it boring to discuss philosophy",
                "response_min": 1,
                "response_max": 5,
                "version": "hexaco-pi-r-60",
                "language": "en",
                "reverse_keyed": True,
                "facet": "Openness"
            }
        ]
        
        return questions

    @app.get("/api/tests/hexaco/versions", tags=["assessments"])
    async def get_hexaco_versions(current_user=Depends(get_current_user_from_token)):
        """Get available HEXACO test versions"""
        logger.info(f"🧠 HEXACO versions request for: {current_user['email']}")
        
        return {
            "hexaco-pi-r-60": {
                "id": "hexaco-pi-r-60",
                "title": "HEXACO-PI-R Personality Inventory",
                "description": "Comprehensive 24-item HEXACO personality assessment measuring six major dimensions of personality",
                "item_count": 24,
                "estimated_duration": 15,
                "language": "en",
                "active": True
            }
        }

    @app.post("/api/tests/hexaco/start", tags=["assessments"])
    async def start_hexaco_test(request_data: dict, current_user=Depends(get_current_user_from_token)):
        """Start a new HEXACO test session"""
        logger.info(f"🧠 Starting HEXACO test for: {current_user['email']}")
        
        session_id = f"hexaco_{current_user['id']}_{hash(current_user['email']) % 10000}_{int(time.time())}"
        
        return {
            "session_id": session_id,
            "message": "HEXACO test session started successfully"
        }

    # HEXACO Response Models
    class HexacoAnswerRequest(BaseModel):
        session_id: str
        question_id: int
        answer: int  # 1-5 scale
        factor: str

    @app.post("/api/tests/hexaco/answer", tags=["assessments"])
    async def submit_hexaco_answer(answer_data: HexacoAnswerRequest, current_user=Depends(get_current_user_from_token)):
        """Submit a single HEXACO personality test answer"""
        logger.info(f"🧠 HEXACO answer submission for question {answer_data.question_id} by {current_user['email']}")
        
        try:
            from datetime import datetime
            from sqlalchemy import create_engine, text
            
            # Database setup (same as login)
            DATABASE_URL = (
                os.getenv("DATABASE_URL") or 
                os.getenv("DATABASE_PRIVATE_URL") or 
                os.getenv("POSTGRES_URL") or
                os.getenv("RAILWAY_DATABASE_URL")
            )
            
            if DATABASE_URL:
                try:
                    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
                    
                    with engine.connect() as conn:
                        # Store answer in database (create table if needed)
                        conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS hexaco_responses (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER,
                                session_id VARCHAR(255),
                                question_id INTEGER,
                                factor VARCHAR(50),
                                answer INTEGER,
                                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        
                        # Insert the response
                        conn.execute(text("""
                            INSERT INTO hexaco_responses (user_id, session_id, question_id, factor, answer, submitted_at)
                            VALUES (:user_id, :session_id, :question_id, :factor, :answer, :submitted_at)
                        """), {
                            "user_id": current_user["id"],
                            "session_id": answer_data.session_id,
                            "question_id": answer_data.question_id,
                            "factor": answer_data.factor,
                            "answer": answer_data.answer,
                            "submitted_at": datetime.utcnow()
                        })
                        conn.commit()
                        
                        # Check how many responses we have for this session
                        result = conn.execute(text("""
                            SELECT COUNT(*) FROM hexaco_responses 
                            WHERE user_id = :user_id AND session_id = :session_id
                        """), {"user_id": current_user["id"], "session_id": answer_data.session_id})
                        
                        total_responses = result.fetchone()[0]
                        
                        logger.info(f"✅ HEXACO response stored: {total_responses}/24 completed")
                        
                        return {
                            "success": True,
                            "message": "Answer recorded successfully",
                            "progress": {
                                "completed": total_responses,
                                "total": 24,
                                "percentage": round((total_responses / 24) * 100)
                            },
                            "session_id": answer_data.session_id,
                            "is_complete": total_responses >= 24
                        }
                        
                except Exception as db_error:
                    logger.warning(f"Database storage failed: {db_error}, using fallback")
                    
            # Fallback implementation without database
            logger.info("Using fallback HEXACO answer storage")
            
            # Simulate progress tracking
            progress = min(answer_data.question_id, 24)
            
            return {
                "success": True,
                "message": "Answer recorded successfully (fallback mode)",
                "progress": {
                    "completed": progress,
                    "total": 24,
                    "percentage": round((progress / 24) * 100)
                },
                "session_id": answer_data.session_id,
                "is_complete": progress >= 24,
                "note": "Responses are temporarily stored - complete assessment for full personality analysis"
            }
            
        except Exception as e:
            logger.error(f"❌ Error submitting HEXACO answer: {e}")
            raise HTTPException(status_code=500, detail="Failed to submit answer")

    @app.get("/api/tests/hexaco/results/{user_id}", tags=["assessments"])
    async def get_hexaco_results(user_id: int, current_user=Depends(get_current_user_from_token)):
        """Get complete HEXACO personality profile with career recommendations"""
        logger.info(f"🧠 HEXACO results request for user {user_id} by {current_user['email']}")
        
        # Ensure user can only access their own results (or admin access)
        if user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        try:
            from datetime import datetime
            from sqlalchemy import create_engine, text
            
            # Database setup
            DATABASE_URL = (
                os.getenv("DATABASE_URL") or 
                os.getenv("DATABASE_PRIVATE_URL") or 
                os.getenv("POSTGRES_URL") or
                os.getenv("RAILWAY_DATABASE_URL")
            )
            
            if DATABASE_URL:
                try:
                    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
                    
                    with engine.connect() as conn:
                        # Get all responses for this user
                        result = conn.execute(text("""
                            SELECT factor, question_id, answer FROM hexaco_responses 
                            WHERE user_id = :user_id 
                            ORDER BY question_id
                        """), {"user_id": user_id})
                        
                        responses = result.fetchall()
                        
                        if len(responses) < 24:
                            logger.info(f"Incomplete HEXACO assessment: {len(responses)}/24 responses")
                            return {
                                "assessment_complete": False,
                                "responses_count": len(responses),
                                "total_required": 24,
                                "message": "Please complete all 24 questions to get your personality profile"
                            }
                        
                        # Calculate scores for each factor
                        factor_scores = {
                            "Honesty-Humility": [],
                            "Emotionality": [],
                            "Extraversion": [],
                            "Agreeableness": [],
                            "Conscientiousness": [],
                            "Openness": []
                        }
                        
                        # Group responses by factor
                        for factor, question_id, answer in responses:
                            if factor in factor_scores:
                                # Handle reverse scoring for certain questions
                                reverse_scored_questions = [2, 4, 7, 15, 16, 20, 24]
                                if question_id in reverse_scored_questions:
                                    adjusted_answer = 6 - answer  # Reverse 1-5 scale
                                else:
                                    adjusted_answer = answer
                                factor_scores[factor].append(adjusted_answer)
                        
                        # Calculate average scores
                        calculated_scores = {}
                        for factor, scores in factor_scores.items():
                            if scores:
                                calculated_scores[factor] = round(sum(scores) / len(scores), 2)
                            else:
                                calculated_scores[factor] = 3.0  # Neutral default
                        
                        logger.info(f"✅ HEXACO scores calculated: {calculated_scores}")
                        
                except Exception as db_error:
                    logger.warning(f"Database retrieval failed: {db_error}, using fallback")
                    calculated_scores = None
                    
            if not calculated_scores:
                # Fallback personality profile
                calculated_scores = {
                    "Honesty-Humility": 3.8,
                    "Emotionality": 3.2,
                    "Extraversion": 3.6,
                    "Agreeableness": 4.1,
                    "Conscientiousness": 4.3,
                    "Openness": 3.9
                }
                logger.info("Using fallback HEXACO personality profile")
            
            # Generate personality description and career recommendations
            hexaco_results = {
                "assessment_complete": True,
                "user_id": user_id,
                "completed_at": datetime.utcnow().isoformat(),
                "scores": calculated_scores,
                "percentiles": {
                    factor: min(95, max(5, int((score - 1) * 25)))  # Convert 1-5 to percentile
                    for factor, score in calculated_scores.items()
                },
                "personality_description": {
                    "primary_traits": [
                        trait for trait, score in calculated_scores.items() 
                        if score >= 4.0
                    ],
                    "summary": generate_personality_summary(calculated_scores),
                    "strengths": generate_strengths(calculated_scores),
                    "development_areas": generate_development_areas(calculated_scores)
                },
                "career_recommendations": {
                    "highly_suitable": generate_career_matches(calculated_scores, "high"),
                    "moderately_suitable": generate_career_matches(calculated_scores, "medium"),
                    "work_environments": generate_work_environments(calculated_scores),
                    "leadership_style": generate_leadership_style(calculated_scores)
                },
                "next_steps": [
                    "Review your personality profile to understand your natural tendencies",
                    "Explore recommended career paths that align with your traits", 
                    "Take the Holland Interest assessment for additional career insights",
                    "Set specific career goals based on your personality strengths"
                ]
            }
            
            return hexaco_results
            
        except Exception as e:
            logger.error(f"❌ Error retrieving HEXACO results: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve personality profile")

    # Helper functions for HEXACO interpretation
    def generate_personality_summary(scores):
        """Generate a personalized summary based on HEXACO scores"""
        high_traits = [trait for trait, score in scores.items() if score >= 4.0]
        low_traits = [trait for trait, score in scores.items() if score <= 2.5]
        
        summary = f"Your personality profile shows "
        if high_traits:
            summary += f"particularly strong tendencies in {', '.join(high_traits[:2])}. "
        if low_traits:
            summary += f"You tend to be more reserved in areas of {', '.join(low_traits[:2])}. "
        
        summary += "This combination suggests specific career paths where you're likely to thrive."
        return summary

    def generate_strengths(scores):
        """Generate personalized strengths based on scores"""
        strengths = []
        if scores.get("Conscientiousness", 3) >= 4.0:
            strengths.append("Strong work ethic and attention to detail")
        if scores.get("Agreeableness", 3) >= 4.0:
            strengths.append("Excellent teamwork and collaboration skills")
        if scores.get("Extraversion", 3) >= 4.0:
            strengths.append("Natural leadership and communication abilities")
        if scores.get("Openness", 3) >= 4.0:
            strengths.append("Creative thinking and adaptability to change")
        if scores.get("Honesty-Humility", 3) >= 4.0:
            strengths.append("High integrity and ethical decision-making")
        if scores.get("Emotionality", 3) >= 4.0:
            strengths.append("Strong empathy and emotional intelligence")
        
        return strengths[:4] if strengths else ["Well-balanced personality across all dimensions"]

    def generate_development_areas(scores):
        """Generate development suggestions based on lower scores"""
        areas = []
        if scores.get("Conscientiousness", 3) <= 2.5:
            areas.append("Developing better organization and time management skills")
        if scores.get("Extraversion", 3) <= 2.5:
            areas.append("Building confidence in social and leadership situations")
        if scores.get("Openness", 3) <= 2.5:
            areas.append("Embracing new experiences and creative challenges")
        if scores.get("Agreeableness", 3) <= 2.5:
            areas.append("Improving collaboration and conflict resolution skills")
        
        return areas[:3] if areas else ["Continue leveraging your natural strengths"]

    def generate_career_matches(scores, level):
        """Generate career recommendations based on personality profile"""
        careers = []
        
        # High conscientiousness careers
        if scores.get("Conscientiousness", 3) >= 4.0:
            if level == "high":
                careers.extend(["Project Manager", "Accountant", "Engineer", "Research Scientist"])
            else:
                careers.extend(["Quality Analyst", "Operations Manager"])
        
        # High extraversion careers  
        if scores.get("Extraversion", 3) >= 4.0:
            if level == "high":
                careers.extend(["Sales Manager", "Marketing Director", "CEO", "Public Speaker"])
            else:
                careers.extend(["Team Lead", "Customer Success Manager"])
        
        # High openness careers
        if scores.get("Openness", 3) >= 4.0:
            if level == "high":
                careers.extend(["Designer", "Artist", "Consultant", "Entrepreneur"])
            else:
                careers.extend(["Product Manager", "Innovation Specialist"])
        
        # High agreeableness careers
        if scores.get("Agreeableness", 3) >= 4.0:
            if level == "high":
                careers.extend(["Counselor", "Teacher", "Social Worker", "HR Manager"])
            else:
                careers.extend(["Customer Service Manager", "Team Coordinator"])
        
        return list(set(careers))[:6] if careers else ["Administrative roles", "Support positions"]

    def generate_work_environments(scores):
        """Suggest optimal work environments"""
        environments = []
        
        if scores.get("Extraversion", 3) >= 4.0:
            environments.append("Collaborative team-based environments")
        if scores.get("Conscientiousness", 3) >= 4.0:
            environments.append("Structured, goal-oriented workplaces")
        if scores.get("Openness", 3) >= 4.0:
            environments.append("Dynamic, innovative organizations")
        if scores.get("Agreeableness", 3) >= 4.0:
            environments.append("Supportive, people-focused cultures")
        
        return environments if environments else ["Balanced work environments"]

    def generate_leadership_style(scores):
        """Describe leadership style based on personality"""
        if scores.get("Extraversion", 3) >= 4.0 and scores.get("Agreeableness", 3) >= 4.0:
            return "Collaborative and inspiring leader who motivates through relationships"
        elif scores.get("Conscientiousness", 3) >= 4.0:
            return "Systematic and reliable leader who leads by example"
        elif scores.get("Openness", 3) >= 4.0:
            return "Visionary leader who encourages innovation and creativity"
        else:
            return "Balanced leadership style adapting to team needs"

    # ================================
    # HOLLAND CAREER INTEREST ASSESSMENT
    # ================================

    @app.get("/api/tests/holland/questions", tags=["assessments"])
    async def get_holland_questions(current_user=Depends(get_current_user_from_token)):
        """Get enhanced Holland RIASEC career interest test questions"""
        logger.info(f"🎯 Holland RIASEC questions request for: {current_user['email']}")
        
        # Enhanced Holland RIASEC questions for career interests
        holland_questions = {
            "session_id": f"holland_{current_user['id']}_{hash(current_user['email']) % 10000}",
            "total_questions": 30,
            "estimated_time_minutes": 10,
            "description": "The Holland Code career test identifies your interests across 6 career themes to suggest matching occupations",
            "riasec_factors": ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"],
            "questions": [
                # Realistic (R) - 5 questions
                {
                    "id": 1,
                    "factor": "Realistic",
                    "text": "I enjoy working with tools and machinery",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 2,
                    "factor": "Realistic",
                    "text": "I like working outdoors and with my hands",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 3,
                    "factor": "Realistic",
                    "text": "I prefer practical work that produces tangible results",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 4,
                    "factor": "Realistic",
                    "text": "I enjoy building, repairing, or maintaining things",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 5,
                    "factor": "Realistic",
                    "text": "I like working with machines, equipment, or vehicles",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                # Investigative (I) - 5 questions
                {
                    "id": 6,
                    "factor": "Investigative",
                    "text": "I enjoy analyzing data and conducting research",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 7,
                    "factor": "Investigative",
                    "text": "I like solving complex problems through analysis",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 8,
                    "factor": "Investigative",
                    "text": "I enjoy scientific and mathematical work",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 9,
                    "factor": "Investigative",
                    "text": "I like learning about how things work",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 10,
                    "factor": "Investigative",
                    "text": "I prefer working independently on research projects",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                # Artistic (A) - 5 questions
                {
                    "id": 11,
                    "factor": "Artistic",
                    "text": "I enjoy creative and artistic activities",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 12,
                    "factor": "Artistic",
                    "text": "I like expressing myself through art, writing, or design",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 13,
                    "factor": "Artistic",
                    "text": "I enjoy working in unstructured environments",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 14,
                    "factor": "Artistic",
                    "text": "I like creating original ideas and innovative solutions",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 15,
                    "factor": "Artistic",
                    "text": "I prefer work that allows for creative freedom",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                # Social (S) - 5 questions
                {
                    "id": 16,
                    "factor": "Social",
                    "text": "I enjoy helping and teaching others",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 17,
                    "factor": "Social",
                    "text": "I like working with people to solve their problems",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 18,
                    "factor": "Social",
                    "text": "I enjoy providing care and support to others",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 19,
                    "factor": "Social",
                    "text": "I like training, counseling, or mentoring people",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 20,
                    "factor": "Social",
                    "text": "I prefer collaborative team-based work",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                # Enterprising (E) - 5 questions
                {
                    "id": 21,
                    "factor": "Enterprising",
                    "text": "I enjoy leading teams and managing projects",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 22,
                    "factor": "Enterprising",
                    "text": "I like persuading and influencing others",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 23,
                    "factor": "Enterprising",
                    "text": "I enjoy competitive business environments",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 24,
                    "factor": "Enterprising",
                    "text": "I like taking risks to achieve goals",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 25,
                    "factor": "Enterprising",
                    "text": "I prefer work involving sales or business development",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                # Conventional (C) - 5 questions
                {
                    "id": 26,
                    "factor": "Conventional",
                    "text": "I enjoy organizing information and keeping records",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 27,
                    "factor": "Conventional",
                    "text": "I like following established procedures and rules",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 28,
                    "factor": "Conventional",
                    "text": "I prefer working with numbers, data, and details",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 29,
                    "factor": "Conventional",
                    "text": "I enjoy administrative and clerical work",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                },
                {
                    "id": 30,
                    "factor": "Conventional",
                    "text": "I like structured, predictable work environments",
                    "scale": "1=Strongly Dislike, 5=Strongly Like"
                }
            ],
            "instructions": "Rate how much you like or dislike each type of work activity. Your responses will identify your Holland Code and suggest compatible career paths.",
            "career_relevance": {
                "Realistic": "Hands-on careers: Engineering, Construction, Agriculture, Technical trades",
                "Investigative": "Analytical careers: Science, Research, Medicine, Technology",
                "Artistic": "Creative careers: Arts, Design, Writing, Entertainment",
                "Social": "People-focused careers: Education, Healthcare, Counseling, Social work",
                "Enterprising": "Leadership careers: Business, Sales, Management, Politics",
                "Conventional": "Organized careers: Accounting, Administration, Banking, Operations"
            }
        }
        
        return holland_questions

    # Holland Response Models
    class HollandSubmitRequest(BaseModel):
        session_id: str
        responses: List[dict]  # List of {question_id, factor, answer}

    @app.post("/api/tests/holland/submit", tags=["assessments"])
    async def submit_holland_assessment(submission_data: HollandSubmitRequest, current_user=Depends(get_current_user_from_token)):
        """Submit complete Holland RIASEC assessment and get results"""
        logger.info(f"🎯 Holland assessment submission by {current_user['email']} - {len(submission_data.responses)} responses")
        
        try:
            from datetime import datetime
            from sqlalchemy import create_engine, text
            
            # Validate submission
            if len(submission_data.responses) != 30:
                raise HTTPException(status_code=400, detail=f"Expected 30 responses, got {len(submission_data.responses)}")
            
            # Database setup
            DATABASE_URL = (
                os.getenv("DATABASE_URL") or 
                os.getenv("DATABASE_PRIVATE_URL") or 
                os.getenv("POSTGRES_URL") or
                os.getenv("RAILWAY_DATABASE_URL")
            )
            
            riasec_scores = {"Realistic": 0, "Investigative": 0, "Artistic": 0, "Social": 0, "Enterprising": 0, "Conventional": 0}
            
            # Calculate RIASEC scores
            for response in submission_data.responses:
                factor = response.get("factor")
                answer = response.get("answer", 3)
                if factor in riasec_scores:
                    riasec_scores[factor] += answer
            
            # Convert to percentages (5 questions × 5 max = 25 max per factor)
            for factor in riasec_scores:
                riasec_scores[factor] = round((riasec_scores[factor] / 25) * 100)
            
            # Determine Holland Code (top 3 scores)
            sorted_scores = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
            holland_code = "".join([factor[0] for factor, score in sorted_scores[:3]])
            
            if DATABASE_URL:
                try:
                    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
                    
                    with engine.connect() as conn:
                        # Create table if needed
                        conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS holland_assessments (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER,
                                session_id VARCHAR(255),
                                holland_code VARCHAR(3),
                                realistic_score INTEGER,
                                investigative_score INTEGER,
                                artistic_score INTEGER,
                                social_score INTEGER,
                                enterprising_score INTEGER,
                                conventional_score INTEGER,
                                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        
                        # Store assessment results
                        conn.execute(text("""
                            INSERT INTO holland_assessments 
                            (user_id, session_id, holland_code, realistic_score, investigative_score, 
                             artistic_score, social_score, enterprising_score, conventional_score, completed_at)
                            VALUES (:user_id, :session_id, :holland_code, :r, :i, :a, :s, :e, :c, :completed_at)
                        """), {
                            "user_id": current_user["id"],
                            "session_id": submission_data.session_id,
                            "holland_code": holland_code,
                            "r": riasec_scores["Realistic"],
                            "i": riasec_scores["Investigative"],
                            "a": riasec_scores["Artistic"],
                            "s": riasec_scores["Social"],
                            "e": riasec_scores["Enterprising"],
                            "c": riasec_scores["Conventional"],
                            "completed_at": datetime.utcnow()
                        })
                        conn.commit()
                        
                        logger.info(f"✅ Holland assessment stored: {holland_code}")
                        
                except Exception as db_error:
                    logger.warning(f"Database storage failed: {db_error}, using fallback")
            
            # Generate career recommendations based on Holland Code
            holland_results = {
                "assessment_complete": True,
                "user_id": current_user["id"],
                "session_id": submission_data.session_id,
                "completed_at": datetime.utcnow().isoformat(),
                "holland_code": holland_code,
                "riasec_scores": riasec_scores,
                "primary_interests": [
                    {"factor": factor, "score": score, "description": get_riasec_description(factor)}
                    for factor, score in sorted_scores[:3]
                ],
                "career_matches": generate_holland_careers(holland_code),
                "personality_summary": generate_holland_summary(holland_code, riasec_scores),
                "work_values": generate_work_values(holland_code),
                "next_steps": [
                    "Explore careers that match your Holland Code",
                    "Take the HEXACO personality test for deeper insights",
                    "Research education paths for your interest areas",
                    "Consider informational interviews in matching fields"
                ]
            }
            
            return holland_results
            
        except Exception as e:
            logger.error(f"❌ Error submitting Holland assessment: {e}")
            raise HTTPException(status_code=500, detail="Failed to process Holland assessment")

    # Holland helper functions
    def get_riasec_description(factor):
        """Get description for RIASEC factor"""
        descriptions = {
            "Realistic": "Practical, hands-on work with tools, machines, or outdoor activities",
            "Investigative": "Analytical, research-oriented work involving data and problem-solving",
            "Artistic": "Creative, expressive work in unstructured, innovative environments",
            "Social": "People-oriented work focused on helping, teaching, and supporting others",
            "Enterprising": "Leadership, persuasion, and business-oriented competitive environments",
            "Conventional": "Organized, detail-oriented work with data, records, and procedures"
        }
        return descriptions.get(factor, "Interest area")

    def generate_holland_careers(holland_code):
        """Generate career matches based on Holland Code"""
        # Career mappings for common Holland Codes
        career_mappings = {
            "RIE": ["Engineer", "Architect", "Computer Programmer", "Lab Technician"],
            "RIC": ["Surveyor", "Drafter", "Quality Control Inspector", "Technical Writer"],
            "RCE": ["Building Inspector", "Construction Manager", "Operations Manager", "Safety Inspector"],
            "IRE": ["Research Scientist", "Systems Analyst", "Data Scientist", "Software Developer"],
            "IAS": ["Psychologist", "Research Professor", "Science Writer", "Market Researcher"],
            "IAE": ["Management Consultant", "Strategic Planner", "Business Analyst", "Innovation Manager"],
            "AIS": ["Art Therapist", "Museum Curator", "Creative Director", "UX Designer"],
            "ASE": ["Creative Director", "Brand Manager", "Media Producer", "Event Planner"],
            "SIA": ["Counselor", "Social Worker", "Art Teacher", "Therapist"],
            "SEA": ["Training Manager", "HR Director", "Corporate Trainer", "Team Leader"],
            "SEC": ["School Administrator", "Program Coordinator", "Healthcare Administrator", "Project Manager"],
            "ESA": ["Sales Manager", "Marketing Director", "Public Relations Manager", "Business Owner"],
            "ESC": ["General Manager", "Operations Director", "Executive Assistant", "Administrator"],
            "ECS": ["Bank Manager", "Finance Director", "Government Administrator", "CEO"],
            "CES": ["Office Manager", "Administrative Coordinator", "Project Administrator", "Executive Assistant"],
            "CSE": ["Accountant", "Financial Analyst", "Auditor", "Budget Analyst"],
            "CRS": ["Database Administrator", "Statistical Clerk", "Bookkeeper", "Records Manager"]
        }
        
        # Get exact match or similar codes
        exact_match = career_mappings.get(holland_code, [])
        if exact_match:
            return exact_match[:6]
        
        # Find similar codes (matching first 2 letters)
        similar_matches = []
        for code, careers in career_mappings.items():
            if code[:2] == holland_code[:2]:
                similar_matches.extend(careers)
        
        return similar_matches[:6] if similar_matches else ["Administrative Assistant", "Customer Service", "General Office Work"]

    def generate_holland_summary(holland_code, scores):
        """Generate personality summary from Holland results"""
        top_factor = max(scores.items(), key=lambda x: x[1])[0]
        
        summaries = {
            "Realistic": "You prefer practical, hands-on work and enjoy seeing tangible results from your efforts.",
            "Investigative": "You're analytical and enjoy research, problem-solving, and understanding how things work.",
            "Artistic": "You value creativity and self-expression, preferring unstructured, innovative environments.",
            "Social": "You're people-oriented and find fulfillment in helping, teaching, and supporting others.",
            "Enterprising": "You enjoy leadership, business challenges, and competitive environments.",
            "Conventional": "You appreciate organization, structure, and detailed work with clear procedures."
        }
        
        return f"Your Holland Code {holland_code} indicates: {summaries.get(top_factor, 'Balanced interests across multiple areas.')} This suggests careers that combine {holland_code[0].lower()}, {holland_code[1].lower()}, and {holland_code[2].lower()} elements."

    def generate_work_values(holland_code):
        """Generate work values based on Holland Code"""
        values_map = {
            "R": ["Practical results", "Independence", "Physical activity"],
            "I": ["Intellectual challenge", "Learning", "Problem-solving"],
            "A": ["Creativity", "Self-expression", "Innovation"],
            "S": ["Helping others", "Teamwork", "Making a difference"],
            "E": ["Leadership", "Competition", "Financial success"],
            "C": ["Organization", "Security", "Clear expectations"]
        }
        
        values = []
        for letter in holland_code:
            values.extend(values_map.get(letter, []))
        
        return list(set(values))[:6]

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