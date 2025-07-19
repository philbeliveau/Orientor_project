#!/usr/bin/env python3
"""
Orientor Platform - Phase 1 Simple Application
Core Features: Basic Authentication, Health Checks (no complex config dependencies)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging
import sys
import os
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create FastAPI app with minimal configuration
app = FastAPI(
    title="Orientor API - Phase 1 Simple",
    description="Core authentication without complex dependencies",
    version="1.0.0-phase1-simple",
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
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Simple auth setup
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-replace-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

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

# In-memory user store for Phase 1 (replace with database later)
users_db = {
    "test@example.com": {
        "id": 1,
        "email": "test@example.com", 
        "name": "Test User",
        "hashed_password": pwd_context.hash("password123")
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return users_db.get(email)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for Railway health checks"""
    return {
        "message": "Orientor Platform - Phase 1 Simple Active",
        "version": "1.0.0-phase1-simple",
        "status": "operational",
        "features": ["simple_auth", "health_checks"]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment monitoring"""
    return {
        "status": "healthy",
        "message": "Phase 1 Simple deployment operational",
        "version": "1.0.0-phase1-simple"
    }

# Auth endpoints
@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Simple login endpoint"""
    logger.info(f"Login attempt for: {login_request.email}")
    
    user = users_db.get(login_request.email)
    if not user or not verify_password(login_request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    logger.info(f"Login successful for: {login_request.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register", response_model=Token)
async def register(register_request: RegisterRequest):
    """Simple registration endpoint"""
    logger.info(f"Registration attempt for: {register_request.email}")
    
    if register_request.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Add user to in-memory store
    users_db[register_request.email] = {
        "id": len(users_db) + 1,
        "email": register_request.email,
        "name": register_request.name,
        "hashed_password": pwd_context.hash(register_request.password)
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": register_request.email}, expires_delta=access_token_expires
    )
    
    logger.info(f"Registration successful for: {register_request.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return User(**current_user)

# Test endpoint
@app.get("/api/test/")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Phase 1 Simple test endpoint working", "status": "ok"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Phase 1 Simple startup configuration"""
    logger.info("🚀 Phase 1 Simple startup initiated")
    logger.info(f"JWT Secret configured: {bool(SECRET_KEY != 'dev-secret-key-replace-in-production')}")
    logger.info("✅ Phase 1 Simple startup completed successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Phase 1 Simple app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)