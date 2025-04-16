from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging

# Import routers directly
from app.routes.user import router as auth_router, get_current_user
from app.routers.users import router as users_router
from app.routes.chat import router as chat_router
from app.routers.peers import router as peers_router
from app.routers.messages import router as messages_router
from app.routers.profiles import router as profiles_router
from app.routers.test import router as test_router

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create FastAPI app
app = FastAPI(title="Orientor API")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://localhost:3000",
    "https://localhost:5173",
    # Add additional allowed origins as needed for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Print debug information about routers
logger.info(f"Registering auth_router routes: {[route.path for route in auth_router.routes]}")
logger.info(f"Registering users_router routes: {[route.path for route in users_router.routes]}")
logger.info(f"Registering chat_router routes: {[route.path for route in chat_router.routes]}")
logger.info(f"Registering peers_router routes: {[route.path for route in peers_router.routes]}")
logger.info(f"Registering messages_router routes: {[route.path for route in messages_router.routes]}")
logger.info(f"Registering profiles_router routes: {[route.path for route in profiles_router.routes]}")
logger.info(f"Registering test_router routes: {[route.path for route in test_router.routes]}")

# Include routers
app.include_router(auth_router)  # Include auth router first - it defines dependencies
app.include_router(profiles_router)  # Include profiles router after auth router
app.include_router(test_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(peers_router)
app.include_router(messages_router)

# Explicitly capture route after including it
logger.info("=== Available Routes ===")
for route in app.routes:
    logger.info(f"Route: {route.path}, Methods: {route.methods}")
logger.info("======================")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Orientor API"}

# Direct routes for testing profiles
@app.get("/direct-profile-test")
def direct_profile_test():
    return {"message": "Direct profile test is working"}

@app.get("/direct-profile-me")
def direct_profile_me(current_user = Depends(get_current_user)):
    from app.models import UserProfile
    from app.utils.database import get_db
    db = next(get_db())
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)