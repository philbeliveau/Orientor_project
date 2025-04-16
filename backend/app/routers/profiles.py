from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
import logging
from app.utils.database import get_db
from app.models import User, UserProfile
from app.routes.user import get_current_user

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ProfileResponse(BaseModel):
    user_id: int
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    gpa: Optional[float] = None
    hobbies: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    unique_quality: Optional[str] = None
    story: Optional[str] = None
    favorite_movie: Optional[str] = None
    favorite_book: Optional[str] = None
    favorite_celebrities: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[str] = None

    class Config:
        orm_mode = True

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/test")
def test_profiles_route():
    return {"message": "Profiles router is working"}

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0)
    sex: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = Field(None, ge=1)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    hobbies: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    unique_quality: Optional[str] = None
    story: Optional[str] = None
    favorite_movie: Optional[str] = None
    favorite_book: Optional[str] = None
    favorite_celebrities: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[str] = None

@router.get("/me", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to get profile for user ID: {current_user.id}")
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            logger.info(f"No profile found for user ID: {current_user.id}, creating a new one")
            # If no profile exists, create a blank one to avoid 404 errors
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

@router.put("/update", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Attempting to update profile for user ID: {current_user.id}")
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not profile:
            logger.info(f"No profile found for user ID: {current_user.id}, creating a new one")
            # Create new profile if it doesn't exist
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Update profile fields
        updated_fields = profile_data.dict(exclude_unset=True)
        logger.info(f"Updating fields: {list(updated_fields.keys())}")
        for field, value in updated_fields.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        logger.info(f"Successfully updated profile for user ID: {current_user.id}")
        return profile
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

# Add module-level debug message after routes are defined
logger.debug("Initializing profiles router module")
logger.debug(f"Created profiles router with routes: {[route.path for route in router.routes]}") 