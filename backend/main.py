from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes import user  # Import the user router
from app.routes import chat  # Import the chat router
from app.routers.profiles import router as profiles_router  # Import the profiles router
from app.utils.database import engine  # Import database configuration from utils

load_dotenv()

app = FastAPI(title="Orientor API")

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(profiles_router)  # Include the profiles router

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Orientor API"}