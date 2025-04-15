from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging

# Import routers directly instead of through the routers module
from app.routes.user import router as auth_router
from app.routers.users import router as users_router
from app.routes.chat import router as chat_router
from app.routers.peers import router as peers_router
from app.routers.messages import router as messages_router
from app.routes.vector_search import router as vector_router

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

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(peers_router)
app.include_router(messages_router)
app.include_router(vector_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Orientor API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)