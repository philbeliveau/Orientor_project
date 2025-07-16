from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.utils.database import get_db
from app.models import User, UserProfile
from app.models.personality_profiles import PersonalityAssessment, PersonalityResponse, PersonalityProfile
from app.routers.user import get_current_user
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# Pydantic schemas for onboarding
class OnboardingResponse(BaseModel):
    questionId: str
    question: str
    response: str
    timestamp: Optional[datetime] = None

class OnboardingData(BaseModel):
    responses: List[OnboardingResponse]
    psychProfile: Optional[Dict[str, Any]] = None

class OnboardingStatus(BaseModel):
    isComplete: bool
    hasStarted: bool
    currentStep: Optional[str] = None
    completedAt: Optional[datetime] = None

class PsychProfileCreate(BaseModel):
    hexaco: Dict[str, float]
    riasec: Dict[str, float]
    topTraits: List[str]
    description: str

@router.get("/status", response_model=OnboardingStatus)
def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current onboarding status for a user"""
    try:
        logger.info(f"Getting onboarding status for user ID: {current_user.id}")
        
        # Check if user has completed onboarding by looking for personality profile
        personality_profile = db.query(PersonalityProfile).filter(
            PersonalityProfile.user_id == current_user.id
        ).first()
        
        # Check if user has started onboarding
        assessment = db.query(PersonalityAssessment).filter(
            PersonalityAssessment.user_id == current_user.id,
            PersonalityAssessment.assessment_type == "onboarding"
        ).first()
        
        has_started = assessment is not None
        is_complete = personality_profile is not None
        
        return OnboardingStatus(
            isComplete=is_complete,
            hasStarted=has_started,
            currentStep="profile_generation" if has_started and not is_complete else None,
            completedAt=personality_profile.created_at if personality_profile else None
        )
        
    except Exception as e:
        logger.error(f"Error getting onboarding status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding status: {str(e)}")

@router.post("/start")
def start_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new onboarding session"""
    try:
        logger.info(f"Starting onboarding for user ID: {current_user.id}")
        
        # Check if user already has an active onboarding session
        existing_assessment = db.query(PersonalityAssessment).filter(
            PersonalityAssessment.user_id == current_user.id,
            PersonalityAssessment.assessment_type == "onboarding",
            PersonalityAssessment.status == "in_progress"
        ).first()
        
        if existing_assessment:
            logger.info(f"User {current_user.id} already has active onboarding session")
            return {
                "session_id": str(existing_assessment.session_id),
                "message": "Onboarding session already in progress"
            }
        
        # Create new assessment session
        assessment = PersonalityAssessment(
            user_id=current_user.id,
            assessment_type="onboarding",
            assessment_version="v1.0",
            session_id=uuid.uuid4(),  # Keep as UUID object
            status="in_progress",
            started_at=datetime.utcnow(),
            total_items=9,  # 9 onboarding questions
            completed_items=0
        )
        
        db.add(assessment)
        db.commit()
        
        logger.info(f"Created onboarding session {assessment.session_id} for user {current_user.id}")
        
        return {
            "session_id": str(assessment.session_id),
            "message": "Onboarding session started successfully"
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error starting onboarding: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error starting onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start onboarding: {str(e)}")

@router.post("/response")
def save_onboarding_response(
    response_data: OnboardingResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a single onboarding response"""
    try:
        logger.info(f"Saving onboarding response for user ID: {current_user.id}")
        
        # Get the current assessment session
        assessment = db.query(PersonalityAssessment).filter(
            PersonalityAssessment.user_id == current_user.id,
            PersonalityAssessment.assessment_type == "onboarding",
            PersonalityAssessment.status == "in_progress"
        ).first()
        
        if not assessment:
            raise HTTPException(status_code=404, detail="No active onboarding session found")
        
        # Save the response
        personality_response = PersonalityResponse(
            assessment_id=assessment.id,
            item_id=response_data.questionId,
            item_type="onboarding_question",
            response_value={
                "question": response_data.question,
                "response": response_data.response
            },
            created_at=datetime.utcnow()
        )
        
        db.add(personality_response)
        
        # Update assessment progress
        assessment.completed_items += 1
        assessment.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Saved response for question {response_data.questionId}")
        
        return {
            "message": "Response saved successfully",
            "progress": assessment.completed_items,
            "total": assessment.total_items
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error saving response: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error saving response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save response: {str(e)}")

@router.post("/complete")
def complete_onboarding(
    onboarding_data: OnboardingData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete the onboarding process and generate psychological profile"""
    try:
        logger.info(f"Completing onboarding for user ID: {current_user.id}")
        
        # Get the assessment session
        assessment = db.query(PersonalityAssessment).filter(
            PersonalityAssessment.user_id == current_user.id,
            PersonalityAssessment.assessment_type == "onboarding",
            PersonalityAssessment.status == "in_progress"
        ).first()
        
        if not assessment:
            raise HTTPException(status_code=404, detail="No active onboarding session found")
        
        # Save any remaining responses
        for response_data in onboarding_data.responses:
            existing_response = db.query(PersonalityResponse).filter(
                PersonalityResponse.assessment_id == assessment.id,
                PersonalityResponse.item_id == response_data.questionId
            ).first()
            
            if not existing_response:
                personality_response = PersonalityResponse(
                    assessment_id=assessment.id,
                    item_id=response_data.questionId,
                    item_type="onboarding_question",
                    response_value={
                        "question": response_data.question,
                        "response": response_data.response
                    },
                    created_at=datetime.utcnow()
                )
                db.add(personality_response)
        
        # Create psychological profile
        if onboarding_data.psychProfile:
            personality_profile = PersonalityProfile(
                user_id=current_user.id,
                assessment_id=assessment.id,
                profile_type="hexaco",
                scores=onboarding_data.psychProfile,
                narrative_description=onboarding_data.psychProfile.get("description", ""),
                assessment_version="v1.0",
                computed_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(personality_profile)
        
        # Mark assessment as completed
        assessment.status = "completed"
        assessment.completed_at = datetime.utcnow()
        assessment.updated_at = datetime.utcnow()
        
        # Update user profile with basic onboarding completion flag
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if user_profile:
            # You can add a field to track onboarding completion
            user_profile.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Completed onboarding for user {current_user.id}")
        
        return {
            "message": "Onboarding completed successfully",
            "assessment_id": assessment.id,
            "profile_created": onboarding_data.psychProfile is not None
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error completing onboarding: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete onboarding: {str(e)}")

@router.get("/profile")
def get_onboarding_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the user's onboarding psychological profile"""
    try:
        logger.info(f"Getting onboarding profile for user ID: {current_user.id}")
        
        personality_profile = db.query(PersonalityProfile).filter(
            PersonalityProfile.user_id == current_user.id
        ).first()
        
        if not personality_profile:
            raise HTTPException(status_code=404, detail="No onboarding profile found")
        
        return {
            "profile": personality_profile.scores,
            "description": personality_profile.narrative_description,
            "created_at": personality_profile.created_at,
            "assessment_version": personality_profile.assessment_version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@router.get("/responses")
def get_onboarding_responses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all onboarding responses for a user"""
    try:
        logger.info(f"Getting onboarding responses for user ID: {current_user.id}")
        
        # Get the assessment
        assessment = db.query(PersonalityAssessment).filter(
            PersonalityAssessment.user_id == current_user.id,
            PersonalityAssessment.assessment_type == "onboarding"
        ).first()
        
        if not assessment:
            return {"responses": []}
        
        # Get all responses
        responses = db.query(PersonalityResponse).filter(
            PersonalityResponse.assessment_id == assessment.id
        ).all()
        
        formatted_responses = []
        for response in responses:
            formatted_responses.append({
                "questionId": response.item_id,
                "question": response.response_value.get("question", ""),
                "response": response.response_value.get("response", ""),
                "timestamp": response.created_at
            })
        
        return {
            "responses": formatted_responses,
            "assessment_status": assessment.status,
            "completed_items": assessment.completed_items,
            "total_items": assessment.total_items
        }
        
    except Exception as e:
        logger.error(f"Error getting onboarding responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get responses: {str(e)}")

@router.delete("/reset")
def reset_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset onboarding progress for a user"""
    try:
        logger.info(f"Resetting onboarding for user ID: {current_user.id}")
        
        # Delete existing assessment and responses
        assessments = db.query(PersonalityAssessment).filter(
            PersonalityAssessment.user_id == current_user.id,
            PersonalityAssessment.assessment_type == "onboarding"
        ).all()
        
        for assessment in assessments:
            # Delete responses first (foreign key constraint)
            db.query(PersonalityResponse).filter(
                PersonalityResponse.assessment_id == assessment.id
            ).delete()
            
            # Delete profiles
            db.query(PersonalityProfile).filter(
                PersonalityProfile.assessment_id == assessment.id
            ).delete()
            
            # Delete assessment
            db.delete(assessment)
        
        db.commit()
        
        logger.info(f"Reset onboarding for user {current_user.id}")
        
        return {"message": "Onboarding reset successfully"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error resetting onboarding: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error resetting onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset onboarding: {str(e)}")

@router.post("/skip")
def skip_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Skip onboarding for a user by creating a default profile"""
    try:
        logger.info(f"Skipping onboarding for user ID: {current_user.id}")
        
        # Check if user already has a profile
        existing_profile = db.query(PersonalityProfile).filter(
            PersonalityProfile.user_id == current_user.id
        ).first()
        
        if existing_profile:
            logger.info(f"User {current_user.id} already has a profile, skipping")
            return {"message": "User already has a profile"}
        
        # Create a fake assessment for tracking
        assessment = PersonalityAssessment(
            user_id=current_user.id,
            assessment_type="onboarding",
            assessment_version="v1.0",
            session_id=uuid.uuid4(),
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_items=1,
            completed_items=1
        )
        
        db.add(assessment)
        db.flush()
        
        # Create a default personality profile
        default_profile = PersonalityProfile(
            user_id=current_user.id,
            assessment_id=assessment.id,
            profile_type="hexaco",
            scores={
                "hexaco": {
                    "honesty": 0.5,
                    "emotionality": 0.5,
                    "extraversion": 0.5,
                    "agreeableness": 0.5,
                    "conscientiousness": 0.5,
                    "openness": 0.5
                },
                "riasec": {
                    "realistic": 0.5,
                    "investigative": 0.5,
                    "artistic": 0.5,
                    "social": 0.5,
                    "enterprising": 0.5,
                    "conventional": 0.5
                },
                "topTraits": ["Balanced", "Adaptable", "Versatile"]
            },
            narrative_description="This user chose to skip the onboarding assessment. Default balanced profile assigned.",
            assessment_version="v1.0",
            computed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(default_profile)
        db.commit()
        
        logger.info(f"Successfully skipped onboarding for user {current_user.id}")
        
        return {
            "message": "Onboarding skipped successfully",
            "profile_created": True,
            "assessment_id": assessment.id
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error skipping onboarding: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error skipping onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to skip onboarding: {str(e)}")