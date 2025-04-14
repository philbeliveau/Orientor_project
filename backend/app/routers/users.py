from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..utils.database import get_db
from ..models import User, UserProfile
from ..routes.user import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

class ProfileResponse(BaseModel):
    user_id: int
    name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    hobbies: Optional[str] = None
    interests: Optional[str] = None
    
    class Config:
        orm_mode = True

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.get("/{user_id}/profile", response_model=ProfileResponse)
def read_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get profile information for a specific user."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile 