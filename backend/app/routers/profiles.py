from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from ..utils.database import get_db
from ..models import User, UserProfile
from ..routes.user import get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])

class ProfileUpdate(BaseModel):
    favorite_movie: Optional[str] = None
    favorite_book: Optional[str] = None
    favorite_celebrities: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[str] = None

@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/update")
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # Create new profile if it doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update profile fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile 