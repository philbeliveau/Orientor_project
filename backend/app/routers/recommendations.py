from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from ..utils.database import get_db
from ..services.Oasisembedding_service import generate_embedding
from ..services.Swipe_career_recommendation_service import get_pinecone_career_recommendations
from ..models import User, UserRecommendation, SavedRecommendation
from ..utils.auth import get_current_user_unified as get_current_user
from ..schemas.space import SavedRecommendationCreate
import logging
from ..models import UserProfile
import re

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
logger = logging.getLogger(__name__)

# Models
class CareerRecommendation(BaseModel):
    id: str
    oasis_code: str
    label: str
    score: float
    lead_statement: Optional[str] = None
    main_duties: Optional[str] = None
    creativity: Optional[float] = None
    leadership: Optional[float] = None
    digital_literacy: Optional[float] = None
    critical_thinking: Optional[float] = None
    problem_solving: Optional[float] = None
    stress_tolerance: Optional[float] = None
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    all_fields: Optional[Dict[str, str]] = None

class RecommendationsResponse(BaseModel):
    recommendations: List[CareerRecommendation]

class SwipeRequest(BaseModel):
    oasis_code: str
    label: str
    swiped_right: bool
    lead_statement: Optional[str] = None
    main_duties: Optional[str] = None
    creativity: Optional[float] = None
    leadership: Optional[float] = None
    digital_literacy: Optional[float] = None
    critical_thinking: Optional[float] = None
    problem_solving: Optional[float] = None
    stress_tolerance: Optional[float] = None
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    evaluation: Optional[float] = None
    decision_making: Optional[float] = None
    all_fields: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True

class SwipeResponse(BaseModel):
    success: bool
    saved_id: Optional[int] = None
    message: str

def try_parse_float(value: str) -> Optional[float]:
    """Try to parse a string to float, return None if fails"""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None

def extract_fields_from_text(text: str) -> Dict[str, str]:
    """
    Extracts all key-value pairs from the raw Pinecone embedded text using robust pattern matching.
    """
    fields = {}

    # Replace unusual whitespace with normal space
    text = text.replace("\xa0", " ")

    # Normalize common field delimiters
    field_pattern = re.compile(r'([\w\s\-:]+):\s+([^.:|]+(?:\|[^.:]+)*)')
    matches = field_pattern.findall(text)

    for key, value in matches:
        key_clean = (
            key.strip()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("__", "_")
            .lower()
        )
        fields[key_clean] = value.strip()

    # Extract cognitive traits using a more specific pattern
    cognitive_traits = [
        "analytical_thinking",
        "attention_to_detail",
        "collaboration",
        "adaptability",
        "independence",
        "evaluation",
        "decision_making",
        "stress_tolerance"
    ]

    for trait in cognitive_traits:
        # Try both with and without underscores
        trait_name = trait.replace("_", " ").title()
        pattern = f"{trait_name}:\\s*(\\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[trait] = match.group(1)

    return fields

@router.get("", response_model=RecommendationsResponse)
def get_career_recommendations(
    limit: int = Query(30, gt=0, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get career recommendations for the current user based on their profile embedding."""
    try:
        # Get existing recommendations to exclude
        existing_recommendations = db.query(UserRecommendation.oasis_code).filter(
            UserRecommendation.user_id == current_user.id
        ).all()
        
        existing_codes = [rec[0] for rec in existing_recommendations]
        
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Generate embedding from profile
        profile_data = {
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
        }
        
        embedding = generate_embedding(profile_data)
        if not embedding:
            raise HTTPException(
                status_code=status.HTTP_500_interNAL_SERVER_ERROR,
                detail="Failed to generate embedding"
            )
        
        # Get recommendations from Pinecone
        recommendations = get_pinecone_career_recommendations(embedding, limit + len(existing_codes))
        
        # Filter out already seen recommendations
        filtered_recommendations = [
            rec for rec in recommendations 
            if rec.get("oasis_code") not in existing_codes
        ][:limit]
        
        # Convert to response model
        response_recommendations = []
        for rec in filtered_recommendations:
            response_recommendations.append(CareerRecommendation(
                id=rec.get("id", ""),
                oasis_code=rec.get("oasis_code", ""),
                label=rec.get("label", ""),
                score=rec.get("score", 0.0),
                lead_statement=rec.get("lead_statement"),
                main_duties=rec.get("main_duties"),
                creativity=rec.get("creativity"),
                leadership=rec.get("leadership"),
                digital_literacy=rec.get("digital_literacy"),
                critical_thinking=rec.get("critical_thinking"),
                problem_solving=rec.get("problem_solving"),
                stress_tolerance=rec.get("stress_tolerance"),
                analytical_thinking=rec.get("analytical_thinking"),
                attention_to_detail=rec.get("attention_to_detail"),
                collaboration=rec.get("collaboration"),
                adaptability=rec.get("adaptability"),
                independence=rec.get("independence"),
                all_fields=rec.get("all_fields")
            ))
        
        return RecommendationsResponse(recommendations=response_recommendations)
        
    except Exception as e:
        logger.error(f"Error getting career recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_interNAL_SERVER_ERROR,
            detail=f"Failed to get career recommendations: {str(e)}"
        )

@router.post("/swipe", response_model=SwipeResponse)
def swipe_recommendation(
    swipe: SwipeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a swipe action on a career recommendation."""
    try:
        # Record the recommendation as seen
        user_recommendation = UserRecommendation(
            user_id=current_user.id,
            oasis_code=swipe.oasis_code,
            label=swipe.label,
            swiped_right=swipe.swiped_right
        )
        
        db.add(user_recommendation)
        db.commit()
        
        # If swiped right, save to saved_recommendations
        if swipe.swiped_right:
            # Check if already saved
            existing = db.query(SavedRecommendation).filter(
                SavedRecommendation.user_id == current_user.id,
                SavedRecommendation.oasis_code == swipe.oasis_code
            ).first()
            
            if existing:
                return SwipeResponse(
                    success=True,
                    saved_id=existing.id,
                    message="This recommendation was already saved"
                )
            
            # Extract fields from text
            full_text = ""
            if swipe.lead_statement:
                full_text += swipe.lead_statement + " "
            if swipe.main_duties:
                full_text += swipe.main_duties
                
            parsed_fields = extract_fields_from_text(full_text)
            
            # Create new recommendation with extracted fields
            new_recommendation = SavedRecommendation(
                user_id=current_user.id,
                oasis_code=swipe.oasis_code,
                label=swipe.label,
                description=swipe.lead_statement,
                main_duties=swipe.main_duties,
                role_creativity=try_parse_float(parsed_fields.get("creativity")),
                role_leadership=try_parse_float(parsed_fields.get("leadership")),
                role_digital_literacy=try_parse_float(parsed_fields.get("digital_literacy")),
                role_critical_thinking=try_parse_float(parsed_fields.get("critical_thinking")),
                role_problem_solving=try_parse_float(parsed_fields.get("problem_solving")),
                analytical_thinking=try_parse_float(parsed_fields.get("analytical_thinking")),
                attention_to_detail=try_parse_float(parsed_fields.get("attention_to_detail")),
                collaboration=try_parse_float(parsed_fields.get("collaboration")),
                adaptability=try_parse_float(parsed_fields.get("adaptability")),
                independence=try_parse_float(parsed_fields.get("independence")),
                evaluation=try_parse_float(parsed_fields.get("evaluation")),
                decision_making=try_parse_float(parsed_fields.get("decision_making")),
                stress_tolerance=try_parse_float(parsed_fields.get("stress_tolerance")),
                all_fields=parsed_fields
            )
            
            # Log the values being saved for debugging
            logger.info(f"Saving recommendation with values:")
            logger.info(f"Oasis Code: {swipe.oasis_code}")
            logger.info(f"Label: {swipe.label}")
            logger.info(f"Lead Statement: {swipe.lead_statement}")
            logger.info(f"Main Duties: {swipe.main_duties}")
            logger.info(f"Parsed Fields: {parsed_fields}")
            
            db.add(new_recommendation)
            db.commit()
            db.refresh(new_recommendation)
            
            return SwipeResponse(
                success=True,
                saved_id=new_recommendation.id,
                message="Recommendation saved successfully"
            )
        else:
            return SwipeResponse(
                success=True,
                message="Recommendation skipped"
            )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing swipe action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_interNAL_SERVER_ERROR,
            detail=f"Failed to process swipe action: {str(e)}"
        ) 