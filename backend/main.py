from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes import user  # Import the user router
from app.routes import chat  # Import the chat router
from app.routers.profiles import router as profiles_router  # Import the profiles router
from app.utils.database import engine  # Import database configuration from utils
import os

load_dotenv()

app = FastAPI(title="Orientor API")

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(profiles_router)  # Include the profiles router

# Configure CORS
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://navigoproject.vercel.app",  # Your Vercel deployment
    "https://orientor-backend-production.up.railway.app",  # Your Railway backend
    "https://orientor-frontend.vercel.app",  # Add this if it's your frontend URL
]

# Add Railway URL to allowed origins if it exists
RAILWAY_URL = os.getenv("RAILWAY_STATIC_URL")
if RAILWAY_URL:
    allowed_origins.append(f"https://{RAILWAY_URL}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Orientor API"}