#!/usr/bin/env python3
"""
Phase 2 - Chunk 1: User Profile Endpoints
Extends Phase 1 with essential user profile functionality
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Orientor API - Phase 2 Chunk 1",
    description="Phase 1 Auth + User Profile Endpoints",
    version="2.1.0-chunk1",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Simple auth setup
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-replace-in-production")

# Pydantic models
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

class User(BaseModel):
    id: int
    email: str
    name: str

class UserAvatar(BaseModel):
    success: bool
    message: Optional[str] = None
    avatar_name: Optional[str] = None
    avatar_description: Optional[str] = None
    avatar_image_url: Optional[str] = None
    generated_at: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    email: str
    name: str
    onboarding_completed: bool
    created_at: str

# Simple in-memory user store (fallback)
users_db = {
    "test@example.com": {
        "id": 1,
        "email": "test@example.com", 
        "name": "Test User",
        "password": "password123"
    }
}

# Database setup
DATABASE_URL = (
    os.getenv("DATABASE_URL") or 
    os.getenv("DATABASE_PRIVATE_URL") or 
    os.getenv("POSTGRES_URL") or
    os.getenv("RAILWAY_DATABASE_URL")
)
db_engine = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    try:
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.warning(f"bcrypt verification failed: {e}, falling back to plain text")
        return plain_password == hashed_password

def init_database():
    """Initialize database connection"""
    global db_engine
    
    if DATABASE_URL:
        try:
            engine_args = {
                "pool_pre_ping": True,
                "pool_recycle": 300,
                "connect_args": {
                    "sslmode": "require",
                    "connect_timeout": 10,
                    "application_name": "orientor-phase2-chunk1"
                }
            }
            
            db_engine = create_engine(DATABASE_URL, **engine_args)
            
            with db_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection successful")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
    
    logger.info("Using in-memory store as fallback")
    return False

def get_user_from_db(email: str):
    """Get user from database"""
    if not db_engine:
        return users_db.get(email)
    
    schemas_to_try = [
        "SELECT id, email, encrypted_password, name FROM users WHERE email = :email LIMIT 1",
        "SELECT id, email, hashed_password, name FROM users WHERE email = :email LIMIT 1", 
        "SELECT id, email, password_hash, name FROM users WHERE email = :email LIMIT 1",
        "SELECT id, email, password, name FROM users WHERE email = :email LIMIT 1"
    ]
    
    for schema_query in schemas_to_try:
        try:
            with db_engine.connect() as conn:
                result = conn.execute(text(schema_query), {"email": email})
                user = result.fetchone()
                if user:
                    logger.info(f"✅ Found user in database using schema: {schema_query.split(' FROM ')[0]}")
                    return {
                        "id": user[0],
                        "email": user[1], 
                        "name": user[3] if len(user) > 3 and user[3] else user[1].split('@')[0],
                        "password": user[2] if user[2] else "password123",
                        "hashed_password": user[2]
                    }
        except Exception as e:
            logger.debug(f"Schema attempt failed: {e}")
            continue
    
    return users_db.get(email)

def create_simple_token(email: str) -> str:
    """Create a simple token"""
    import base64
    token_data = f"{email}:{datetime.utcnow().isoformat()}"
    return base64.b64encode(token_data.encode()).decode()

def verify_simple_token(token: str) -> Optional[str]:
    """Verify simple token and return email"""
    try:
        import base64
        decoded = base64.b64decode(token.encode()).decode()
        email, timestamp = decoded.split(":", 1)
        return email
    except:
        return None

def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Get current user from token"""
    try:
        token = authorization.credentials
        email = verify_simple_token(token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = get_user_from_db(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Orientor Platform - Phase 2 Chunk 1",
        "version": "2.1.0-chunk1",
        "status": "operational",
        "features": ["auth", "user_profiles", "avatars"]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Phase 2 Chunk 1 operational",
        "version": "2.1.0-chunk1",
        "features": ["auth", "user_profiles", "avatars"]
    }

# Auth endpoints (from Phase 1)
@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Login endpoint with database support and bcrypt verification"""
    logger.info(f"Login attempt for: {login_request.email}")
    
    user = get_user_from_db(login_request.email)
    if not user:
        logger.warning(f"User not found: {login_request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    password_valid = False
    if "hashed_password" in user and user["hashed_password"]:
        password_valid = verify_password(login_request.password, user["hashed_password"])
        logger.info(f"Used bcrypt verification for {login_request.email}: {password_valid}")
    else:
        password_valid = user["password"] == login_request.password
        logger.info(f"Used plain text verification for {login_request.email}: {password_valid}")
    
    if not password_valid:
        logger.warning(f"Password verification failed for: {login_request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_simple_token(user["email"])
    
    logger.info(f"Login successful for: {login_request.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserProfile)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        onboarding_completed=True,  # Default for now
        created_at=datetime.utcnow().isoformat()
    )

@app.get("/auth/onboarding-status")
async def get_onboarding_status(current_user: dict = Depends(get_current_user)):
    """Check if user has completed onboarding"""
    return {
        "onboarding_completed": True,  # Default for now
        "user_id": current_user["id"],
        "email": current_user["email"]
    }

# NEW: Avatar endpoints
@app.get("/api/v1/avatar/me", response_model=UserAvatar)
async def get_user_avatar(current_user: dict = Depends(get_current_user)):
    """Get current user's avatar - Phase 2 Chunk 1 implementation"""
    logger.info(f"Avatar request for user: {current_user['email']}")
    
    # For Phase 2 Chunk 1, return a default avatar structure
    # In Phase 3, this will query the actual UserRepresentation table
    return UserAvatar(
        success=False,
        message="Avatar generation not available in Phase 2 Chunk 1",
        avatar_name=None,
        avatar_description=None,
        avatar_image_url=None,
        generated_at=None
    )

# Test endpoint
@app.get("/api/test/")
async def test_endpoint():
    return {"message": "Phase 2 Chunk 1 test endpoint working", "status": "ok"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup configuration"""
    logger.info("🚀 Phase 2 Chunk 1 startup initiated")
    
    db_connected = init_database()
    if db_connected:
        logger.info("✅ Database mode: Connected to Railway PostgreSQL")
    else:
        logger.info("ℹ️ Fallback mode: Using in-memory store")
        logger.info(f"Available test users: {list(users_db.keys())}")
    
    logger.info("✅ Phase 2 Chunk 1 startup completed")
    logger.info("🎯 Available endpoints: /auth/login, /auth/me, /auth/onboarding-status, /api/v1/avatar/me")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Phase 2 Chunk 1 app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)