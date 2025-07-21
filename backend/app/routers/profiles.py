from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
import logging
from app.utils.database import get_db
from app.models import User, UserProfile, UserSkill
from app.utils.auth import get_current_user_unified as get_current_user
from sqlalchemy.sql import text
import uuid

# Configure logging FIRST
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Optional ML services - graceful fallback if not available
try:
    from app.services.Oasisembedding_service import process_user_embedding, process_user_oasis_embedding
    OASIS_EMBEDDING_AVAILABLE = True
    logger.info("✅ OaSIS embedding service available")
except ImportError as e:
    logger.warning(f"⚠️ OaSIS embedding service not available (requires torch): {e}")
    OASIS_EMBEDDING_AVAILABLE = False

try:
    from app.services.esco_embedding_service384 import process_user_esco_embeddings
    ESCO_EMBEDDING_AVAILABLE = True
    logger.info("✅ ESCO embedding service available")
except ImportError as e:
    logger.warning(f"⚠️ ESCO embedding service not available (requires torch): {e}")
    ESCO_EMBEDDING_AVAILABLE = False

try:
    from app.services.peer_matching_service import generate_peer_suggestions
    PEER_MATCHING_AVAILABLE = True
    logger.info("✅ Peer matching service available")
except ImportError as e:
    logger.warning(f"⚠️ Peer matching service not available (requires ML dependencies): {e}")
    PEER_MATCHING_AVAILABLE = False

# Add a more detailed log message to help with debugging
logger.info("Profiles router module loaded with unified authentication")

class ProfileResponse(BaseModel):
    id: int
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
    interests: Optional[Union[str, List[str]]] = None
    # Add skill fields
    creativity: Optional[float] = None
    leadership: Optional[float] = None
    digital_literacy: Optional[float] = None
    critical_thinking: Optional[float] = None
    problem_solving: Optional[float] = None
    # Job-related fields for embeddings
    job_title: Optional[str] = None
    industry: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[List[str]] = None
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    evaluation: Optional[float] = None
    decision_making: Optional[float] = None
    stress_tolerance: Optional[float] = None

    class Config:
        from_attributes = True

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
    interests: Optional[Union[str, List[str]]] = None
    # Add skill fields
    creativity: Optional[float] = Field(None, ge=0, le=5)
    leadership: Optional[float] = Field(None, ge=0, le=5)
    digital_literacy: Optional[float] = Field(None, ge=0, le=5)
    critical_thinking: Optional[float] = Field(None, ge=0, le=5)
    problem_solving: Optional[float] = Field(None, ge=0, le=5)
    # Add cognitive traits
    analytical_thinking: Optional[float] = Field(None, ge=0, le=5)
    attention_to_detail: Optional[float] = Field(None, ge=0, le=5)
    collaboration: Optional[float] = Field(None, ge=0, le=5)
    adaptability: Optional[float] = Field(None, ge=0, le=5)
    independence: Optional[float] = Field(None, ge=0, le=5)
    evaluation: Optional[float] = Field(None, ge=0, le=5)
    decision_making: Optional[float] = Field(None, ge=0, le=5)
    stress_tolerance: Optional[float] = Field(None, ge=0, le=5)
    # Job-related fields for embeddings
    job_title: Optional[str] = None
    industry: Optional[str] = None
    years_experience: Optional[int] = Field(None, ge=0)
    education_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[List[str]] = None

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
        
        # Get user skills
        skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        response = ProfileResponse.model_validate(profile)
        response.id = current_user.id
        
        # Add all skills to response if they exist
        if skills:
            response.creativity = skills.creativity
            response.leadership = skills.leadership
            response.digital_literacy = skills.digital_literacy
            response.critical_thinking = skills.critical_thinking
            response.problem_solving = skills.problem_solving
            response.analytical_thinking = skills.analytical_thinking
            response.attention_to_detail = skills.attention_to_detail
            response.collaboration = skills.collaboration
            response.adaptability = skills.adaptability
            response.independence = skills.independence
            response.evaluation = skills.evaluation
            response.decision_making = skills.decision_making
            response.stress_tolerance = skills.stress_tolerance
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

@router.put("/update")
async def update_profile(
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Attempting to update profile for user ID: {current_user.id}")
        
        # Get the current profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Extract skill fields from profile update
        skill_fields = {
            "creativity": profile_update.creativity,
            "leadership": profile_update.leadership,
            "digital_literacy": profile_update.digital_literacy,
            "critical_thinking": profile_update.critical_thinking,
            "problem_solving": profile_update.problem_solving,
            "analytical_thinking": profile_update.analytical_thinking,
            "attention_to_detail": profile_update.attention_to_detail,
            "collaboration": profile_update.collaboration,
            "adaptability": profile_update.adaptability,
            "independence": profile_update.independence,
            "evaluation": profile_update.evaluation,
            "decision_making": profile_update.decision_making,
            "stress_tolerance": profile_update.stress_tolerance
        }
        
        # Update user skills
        skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        if not skills:
            skills = UserSkill(user_id=current_user.id)
            db.add(skills)
        
        # Update skill fields
        for field, value in skill_fields.items():
            if value is not None:
                setattr(skills, field, value)
        
        # Update profile fields (excluding skill fields)
        update_data = profile_update.dict(
            exclude={
                "creativity", "leadership", "digital_literacy", "critical_thinking",
                "problem_solving", "analytical_thinking", "attention_to_detail",
                "collaboration", "adaptability", "independence", "evaluation",
                "decision_making", "stress_tolerance"
            },
            exclude_unset=True
        )
        
        logger.info(f"Updating profile fields: {list(update_data.keys())}")
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        # Commit the changes
        db.commit()
        db.refresh(profile)
        db.refresh(skills)
        
        # Generate new embedding using the centralized service
        try:
            # Create a UUID v5 based on the user ID (namespace UUID + user ID)
            user_id_str = str(current_user.id)
            namespace_uuid = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # UUID namespace DNS
            user_uuid = str(uuid.uuid5(namespace_uuid, user_id_str))
            
            logger.info(f"Original user ID: {user_id_str}, Generated UUID: {user_uuid}")
            
            # Fetch RIASEC scores using integer user_id
            riasec_query = text("""
                SELECT r_score, i_score, a_score, s_score, e_score, c_score, top_3_code
                FROM gca_results 
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT 1
            """)
            riasec_result = db.execute(riasec_query, {"user_id": current_user.id}).fetchone()
            
            # Fetch saved recommendations using integer user_id
            recommendations_query = text("""
                SELECT label 
                FROM saved_recommendations 
                WHERE user_id = :user_id
            """)
            recommendations_result = db.execute(recommendations_query, {"user_id": current_user.id}).fetchall()
            
            # Prepare complete profile data for embedding generation
            profile_data = {
                "profile": {
                    "user_id": current_user.id,
                    "name": profile.name,
                    "age": profile.age,
                    "sex": profile.sex,
                    "major": profile.major,
                    "year": profile.year,
                    "gpa": profile.gpa,
                    "hobbies": profile.hobbies,
                    "country": profile.country,
                    "state_province": profile.state_province,
                    "unique_quality": profile.unique_quality,
                    "story": profile.story,
                    "favorite_movie": profile.favorite_movie,
                    "favorite_book": profile.favorite_book,
                    "favorite_celebrities": profile.favorite_celebrities,
                    "learning_style": profile.learning_style,
                    "interests": profile.interests,
                    "job_title": profile.job_title,
                    "industry": profile.industry,
                    "years_experience": profile.years_experience,
                    "education_level": profile.education_level,
                    "career_goals": profile.career_goals,
                    "skills": profile.skills
                },
                "skills": {
                    "creativity": skills.creativity,
                    "leadership": skills.leadership,
                    "digital_literacy": skills.digital_literacy,
                    "critical_thinking": skills.critical_thinking,
                    "problem_solving": skills.problem_solving,
                    "analytical_thinking": skills.analytical_thinking,
                    "attention_to_detail": skills.attention_to_detail,
                    "collaboration": skills.collaboration,
                    "adaptability": skills.adaptability,
                    "independence": skills.independence,
                    "evaluation": skills.evaluation,
                    "decision_making": skills.decision_making,
                    "stress_tolerance": skills.stress_tolerance
                }
            }

            # Add RIASEC data if available
            if riasec_result:
                profile_data["riasec"] = {
                    "r_score": float(riasec_result.r_score),
                    "i_score": float(riasec_result.i_score),
                    "a_score": float(riasec_result.a_score),
                    "s_score": float(riasec_result.s_score),
                    "e_score": float(riasec_result.e_score),
                    "c_score": float(riasec_result.c_score),
                    "top_3_code": riasec_result.top_3_code
                }
                logger.info(f"RIASEC scores added to profile data: {profile_data['riasec']}")
            else:
                logger.warning("No RIASEC scores found for user")
                profile_data["riasec"] = {}

            # Add saved recommendations if available
            if recommendations_result:
                profile_data["saved_recommendations"] = [
                    {"label": row.label}
                    for row in recommendations_result
                ]
                logger.info(f"Added {len(recommendations_result)} saved recommendations to profile data")
            else:
                logger.warning("No saved recommendations found for user")
                profile_data["saved_recommendations"] = []
            
            # Log the complete profile data
            logger.info("Complete profile data for embedding generation:")
            logger.info(f"Profile data: {profile_data}")
            
            # Optional embedding generation - only if ML services available
            if OASIS_EMBEDDING_AVAILABLE:
                try:
                    success = process_user_embedding(db, current_user.id, profile_data)
                    if not success:
                        logger.warning(f"Failed to generate embedding for user ID: {current_user.id}")
                    else:
                        logger.info(f"Successfully generated new embedding for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in embedding generation: {str(e)}")
                    success = False
            else:
                logger.info("⚠️ Embedding generation skipped - ML services not available")
                success = True  # Don't block profile update
                
            # Generate peer suggestions if available and embedding succeeded
            if PEER_MATCHING_AVAILABLE and success:
                try:
                    peer_success = generate_peer_suggestions(db, current_user.id)
                    if peer_success:
                        logger.info(f"Successfully generated peer suggestions for user ID: {current_user.id}")
                    else:
                        logger.warning(f"Failed to generate peer suggestions for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in peer matching: {str(e)}")
            elif not PEER_MATCHING_AVAILABLE:
                logger.info("⚠️ Peer matching skipped - service not available")
                
            # Generate the OaSIS embedding if available
            if OASIS_EMBEDDING_AVAILABLE:
                try:
                    logger.info(f"Generating OaSIS embedding for user ID: {current_user.id}")
                    oasis_success = process_user_oasis_embedding(db, current_user.id)
                    if oasis_success:
                        logger.info(f"OaSIS embedding generated and stored successfully for user ID: {current_user.id}")
                    else:
                        logger.warning(f"Failed to generate or store OaSIS embedding for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in OaSIS embedding process: {str(e)}")
            else:
                logger.info("⚠️ OaSIS embedding skipped - service not available")
                
            # Generate the ESCO embeddings if available
            if ESCO_EMBEDDING_AVAILABLE:
                try:
                    logger.info(f"Generating ESCO embeddings for user ID: {current_user.id}")
                    esco_success = process_user_esco_embeddings(db, current_user.id)
                    if esco_success:
                        logger.info(f"ESCO embeddings generated and stored successfully for user ID: {current_user.id}")
                    else:
                        logger.warning(f"Failed to generate or store ESCO embeddings for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in ESCO embedding process: {str(e)}")
            else:
                logger.info("⚠️ ESCO embedding skipped - service not available")
                
        except Exception as e:
            logger.error(f"Error in embedding/peer suggestion process: {str(e)}")
            # Don't fail the profile update if embedding generation fails
        
        logger.info(f"Successfully updated profile for user ID: {current_user.id}")
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=ProfileResponse)
def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get profile information for a specific user."""
    try:
        logger.info(f"Attempting to get profile for user ID: {user_id}")
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            logger.info(f"No profile found for user ID: {user_id}, creating a new one")
            # Create a new profile if it doesn't exist
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        # Get user skills
        skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
        response = ProfileResponse.model_validate(profile)
        
        # Add skills to response if they exist
        if skills:
            response.creativity = skills.creativity
            response.leadership = skills.leadership
            response.digital_literacy = skills.digital_literacy
            response.critical_thinking = skills.critical_thinking
            response.problem_solving = skills.problem_solving
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

# Add module-level debug message after routes are defined
logger.debug("Initializing profiles router module")
logger.debug(f"Created profiles router with routes: {[route.path for route in router.routes]}") 