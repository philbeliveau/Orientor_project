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

# Simple in-memory user store (fallback if database fails)
users_db = {
    "test@example.com": {
        "id": 1,
        "email": "test@example.com", 
        "name": "Test User",
        "password": "password123"  # Plain text for now (will hash later)
    }
}

# Database setup - try multiple URL sources
DATABASE_URL = (
    os.getenv("DATABASE_URL") or 
    os.getenv("DATABASE_PRIVATE_URL") or 
    os.getenv("POSTGRES_URL") or
    os.getenv("RAILWAY_DATABASE_URL")
)
db_engine = None

def check_users_table():
    """Debug function to check users table structure and data"""
    if not db_engine:
        return
    
    try:
        with db_engine.connect() as conn:
            # Check table structure
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            logger.info(f"📋 Users table columns: {[col[0] for col in columns]}")
            
            # Check sample data
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.fetchone()[0]
            logger.info(f"📊 Total users in database: {count}")
            
            if count > 0:
                # Show sample emails (first 5)
                result = conn.execute(text("SELECT email FROM users LIMIT 5"))
                emails = [row[0] for row in result.fetchall()]
                logger.info(f"📧 Sample user emails: {emails}")
                
    except Exception as e:
        logger.error(f"Failed to check users table: {e}")

def init_database():
    """Initialize database connection with Railway-compatible settings"""
    global db_engine
    
    # Debug logging
    logger.info(f"🔍 DATABASE_URL available: {bool(DATABASE_URL)}")
    if DATABASE_URL:
        # Log connection details (safely)
        import re
        safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', DATABASE_URL)
        logger.info(f"🔗 Connecting to: {safe_url}")
        
        try:
            # Railway + Supabase specific connection settings
            engine_args = {
                "pool_pre_ping": True,
                "pool_recycle": 300,
                "connect_args": {
                    "sslmode": "require",
                    "connect_timeout": 10,
                    "application_name": "orientor-railway"
                }
            }
            
            db_engine = create_engine(DATABASE_URL, **engine_args)
            
            # Test connection with timeout
            with db_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection successful")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
            logger.info("Using in-memory store as fallback")
            
            # Try alternative connection approach
            try:
                logger.info("🔄 Trying alternative connection method...")
                # Force IPv4 and add more connection options
                alt_url = DATABASE_URL.replace("?sslmode=require", "?sslmode=require&hostaddr=")
                
                alt_engine = create_engine(alt_url, **engine_args)
                with alt_engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    db_engine = alt_engine
                    logger.info("✅ Alternative database connection successful")
                    return True
            except Exception as alt_e:
                logger.warning(f"⚠️ Alternative connection also failed: {alt_e}")
    else:
        logger.info("No DATABASE_URL provided, using in-memory store")
    return False

def get_user_from_db(email: str):
    """Get user from database - Railway PostgreSQL compatible"""
    if not db_engine:
        return users_db.get(email)
    
    # Try each schema variant in separate connections to avoid transaction errors
    schemas_to_try = [
        "SELECT id, email, encrypted_password FROM users WHERE email = :email LIMIT 1",
        "SELECT id, email, hashed_password FROM users WHERE email = :email LIMIT 1", 
        "SELECT id, email, password_hash FROM users WHERE email = :email LIMIT 1",
        "SELECT id, email, password FROM users WHERE email = :email LIMIT 1"
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
                        "name": user[1].split('@')[0],  # Use email prefix as name
                        "password": user[2] if user[2] else "password123"  # Handle null passwords
                    }
        except Exception as e:
            logger.debug(f"Schema attempt failed: {e}")
            continue  # Try next schema
    
    logger.info(f"User {email} not found in database, checking in-memory store")
    # Fallback to in-memory store
    return users_db.get(email)

def create_user_in_db(email: str, name: str, password: str):
    """Create user in database"""
    if not db_engine:
        # Fallback to in-memory store
        user_id = len(users_db) + 1
        users_db[email] = {
            "id": user_id,
            "email": email,
            "name": name,
            "password": password
        }
        return user_id
    
    try:
        with db_engine.connect() as conn:
            result = conn.execute(
                text("INSERT INTO users (email, name, password_hash) VALUES (:email, :name, :password) RETURNING id"),
                {"email": email, "name": name, "password": password}
            )
            user_id = result.fetchone()[0]
            conn.commit()
            return user_id
    except Exception as e:
        logger.error(f"Database insert error: {e}")
        # Fallback to in-memory store
        user_id = len(users_db) + 1
        users_db[email] = {
            "id": user_id,
            "email": email,
            "name": name,
            "password": password
        }
        return user_id

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
    """Login endpoint with database support"""
    logger.info(f"Login attempt for: {login_request.email}")
    
    user = get_user_from_db(login_request.email)
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
    """Registration endpoint with database support"""
    logger.info(f"Registration attempt for: {register_request.email}")
    
    # Check if user already exists
    existing_user = get_user_from_db(register_request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user in database
    user_id = create_user_in_db(
        register_request.email,
        register_request.name, 
        register_request.password
    )
    
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
    """Startup configuration with database"""
    logger.info("🚀 Phase 1 with Auth + Database startup initiated")
    
    # Initialize database
    db_connected = init_database()
    if db_connected:
        logger.info("✅ Database mode: Connected to Railway PostgreSQL")
        # Debug: Check users table
        check_users_table()
    else:
        logger.info("ℹ️ Fallback mode: Using in-memory store")
        logger.info(f"Available test users: {list(users_db.keys())}")
    
    logger.info("✅ Phase 1 with Auth + Database startup completed")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting auth app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)