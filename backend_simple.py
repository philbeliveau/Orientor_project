#!/usr/bin/env python3
"""
Simplified Railway Backend Entry Point
Minimal FastAPI backend for deployment testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create minimal FastAPI app
app = FastAPI(
    title="Orientor API - Railway Test",
    description="Minimal FastAPI backend for Railway deployment",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://navigoproject.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000",
        "https://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Orientor Backend is running on Railway!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is operational"}

@app.get("/test")
async def test_endpoint():
    return {"test": "success", "environment": "railway"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)