#!/usr/bin/env python3
"""
FastAPI app with basic auth endpoints - for main_phase1_deploy.py import
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Orientor API - Phase 1 with Auth",
    description="Working deployment with authentication",
    version="1.0.0-auth",
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "https://navigoproject.vercel.app",
    "https://*.up.railway.app",
    "https://*.railway.app",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Simple auth setup (no external dependencies)
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

# Simple in-memory user store (replace with database later)
users_db = {
    "test@example.com": {
        "id": 1,
        "email": "test@example.com", 
        "name": "Test User",
        "password": "password123"  # Plain text for now (will hash later)
    }
}

def create_simple_token(email: str) -> str:
    """Create a simple token (we'll improve this later)"""
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

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Orientor Platform - Phase 1 with Auth Active",
        "version": "1.0.0-auth",
        "status": "operational",
        "features": ["auth", "health_checks"]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Phase 1 with Auth operational",
        "version": "1.0.0-auth"
    }

# Auth endpoints
@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Login endpoint"""
    logger.info(f"Login attempt for: {login_request.email}")
    
    user = users_db.get(login_request.email)
    if not user or user["password"] != login_request.password:
        logger.warning(f"Login failed for: {login_request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_simple_token(user["email"])
    
    logger.info(f"Login successful for: {login_request.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register", response_model=Token)
async def register(register_request: RegisterRequest):
    """Registration endpoint"""
    logger.info(f"Registration attempt for: {register_request.email}")
    
    if register_request.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Add user to store
    users_db[register_request.email] = {
        "id": len(users_db) + 1,
        "email": register_request.email,
        "name": register_request.name,
        "password": register_request.password  # Plain text for now
    }
    
    access_token = create_simple_token(register_request.email)
    
    logger.info(f"Registration successful for: {register_request.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=User)
async def read_users_me(authorization: str = Depends(lambda: "dummy")):
    """Get current user - simplified for now"""
    # Return test user for now
    return User(id=1, email="test@example.com", name="Test User")

# Test endpoint
@app.get("/api/test/")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Auth test endpoint working", "status": "ok"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup configuration"""
    logger.info("🚀 Phase 1 with Auth startup initiated")
    logger.info(f"Available users: {list(users_db.keys())}")
    logger.info("✅ Phase 1 with Auth startup completed")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting auth app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)