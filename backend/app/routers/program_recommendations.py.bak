from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import logging

from ..utils.database import get_db
from ..routers.user import get_current_user
from ..models import User
from ..services.program_matching_service import ProgramMatchingService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/program-recommendations",
    tags=["program-recommendations"],
    dependencies=[Depends(get_current_user)],
)

# Request/Response schemas
class ProgramRecommendationResponse(BaseModel):
    id: str
    program_name: str
    institution: str
    institution_type: str
    program_code: str = None
    duration: str = None
    admission_requirements: List[str] = []
    match_score: float
    cost_estimate: float = None
    location: Dict[str, Any] = {}
    intake_dates: List[str] = []
    relevance_explanation: str
    career_outcomes: List[str] = []
    website_url: str = None
    contact_info: Dict[str, Any] = {}

class ProgramRecommendationsListResponse(BaseModel):
    recommendations: List[ProgramRecommendationResponse]
    total: int
    goal_info: Dict[str, Any]

@router.get("/career-goal/{goal_id}", response_model=ProgramRecommendationsListResponse)
async def get_program_recommendations_for_goal(
    goal_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get educational program recommendations for a specific career goal.
    
    Args:
        goal_id: Career goal ID
        limit: Maximum number of recommendations to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of program recommendations with match scores
    """
    try:
        # Initialize the program matching service
        program_service = ProgramMatchingService(db)
        
        # Get program recommendations
        recommendations = await program_service.find_programs_for_career_goal(
            goal_id=goal_id,
            user_id=current_user.id,
            limit=limit
        )
        
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No career goal found with ID {goal_id} or no programs available"
            )
        
        # Get career goal information for context
        from sqlalchemy import text
        goal_query = text("""
            SELECT cg.id, cg.notes, cg.target_date, cg.set_at,
                   sj.job_title, sj.esco_id
            FROM career_goals cg
            JOIN saved_jobs sj ON cg.job_id = sj.id
            WHERE cg.id = :goal_id AND cg.user_id = :user_id AND cg.status = 'active'
        """)
        
        goal_result = db.execute(goal_query, {"goal_id": goal_id, "user_id": current_user.id}).fetchone()
        
        goal_info = {}
        if goal_result:
            goal_info = {
                "goal_id": goal_result[0],
                "notes": goal_result[1],
                "target_date": goal_result[2].isoformat() if goal_result[2] else None,
                "set_at": goal_result[3].isoformat() if goal_result[3] else None,
                "job_title": goal_result[4],
                "esco_id": goal_result[5]
            }
        
        # Convert to response format
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(ProgramRecommendationResponse(
                id=rec.get("id", ""),
                program_name=rec.get("program_name", ""),
                institution=rec.get("institution", ""),
                institution_type=rec.get("institution_type", ""),
                program_code=rec.get("program_code"),
                duration=rec.get("duration"),
                admission_requirements=rec.get("admission_requirements", []),
                match_score=rec.get("match_score", 0.0),
                cost_estimate=rec.get("cost_estimate"),
                location=rec.get("location", {}),
                intake_dates=rec.get("intake_dates", []),
                relevance_explanation=rec.get("relevance_explanation", ""),
                career_outcomes=rec.get("career_outcomes", []),
                website_url=rec.get("website_url"),
                contact_info=rec.get("contact_info", {})
            ))
        
        logger.info(f"Retrieved {len(response_recommendations)} program recommendations for goal {goal_id}")
        
        return ProgramRecommendationsListResponse(
            recommendations=response_recommendations,
            total=len(response_recommendations),
            goal_info=goal_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting program recommendations for goal {goal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get program recommendations: {str(e)}"
        )

@router.post("/career-goal/{goal_id}/save")
async def save_program_recommendation(
    goal_id: int,
    program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a specific program recommendation for future reference.
    
    Args:
        goal_id: Career goal ID
        program_id: Program ID to save
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message with saved recommendation ID
    """
    try:
        # Initialize the program matching service
        program_service = ProgramMatchingService(db)
        
        # Get the specific program recommendation
        recommendations = await program_service.find_programs_for_career_goal(
            goal_id=goal_id,
            user_id=current_user.id,
            limit=50  # Get more to find the specific one
        )
        
        # Find the specific program
        program_to_save = None
        for rec in recommendations:
            if rec.get("id") == program_id:
                program_to_save = rec
                break
        
        if not program_to_save:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
        
        # Save the recommendation
        saved_id = await program_service.save_program_recommendation(
            goal_id=goal_id,
            program_data=program_to_save
        )
        
        logger.info(f"Saved program recommendation {program_id} for goal {goal_id} as ID {saved_id}")
        
        return {
            "message": "Program recommendation saved successfully",
            "saved_id": saved_id,
            "program_name": program_to_save.get("program_name"),
            "institution": program_to_save.get("institution")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving program recommendation {program_id} for goal {goal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save program recommendation: {str(e)}"
        )

@router.get("/career-goal/{goal_id}/saved")
async def get_saved_program_recommendations(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get previously saved program recommendations for a career goal.
    
    Args:
        goal_id: Career goal ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of saved program recommendations
    """
    try:
        # Initialize the program matching service
        program_service = ProgramMatchingService(db)
        
        # Get saved recommendations
        saved_recommendations = await program_service.get_saved_recommendations(goal_id)
        
        logger.info(f"Retrieved {len(saved_recommendations)} saved recommendations for goal {goal_id}")
        
        return {
            "saved_recommendations": saved_recommendations,
            "total": len(saved_recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error getting saved recommendations for goal {goal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get saved recommendations: {str(e)}"
        )

@router.get("/institutions")
async def get_available_institutions(
    institution_type: str = None,
    region: str = "Quebec",
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available educational institutions.
    
    Args:
        institution_type: Filter by type (cegep, university)
        region: Filter by region (default: Quebec)
        current_user: Current authenticated user
        
    Returns:
        List of institutions with basic information
    """
    try:
        # Mock data for now - would be replaced with real database query
        institutions = [
            {
                "id": "dawson",
                "name": "Dawson College",
                "type": "cegep",
                "city": "Montreal",
                "province": "Quebec",
                "website": "https://www.dawsoncollege.qc.ca/",
                "programs_count": 25
            },
            {
                "id": "maisonneuve",
                "name": "Collège de Maisonneuve",
                "type": "cegep",
                "city": "Montreal", 
                "province": "Quebec",
                "website": "https://www.cmaisonneuve.qc.ca/",
                "programs_count": 30
            },
            {
                "id": "mcgill",
                "name": "McGill University",
                "type": "university",
                "city": "Montreal",
                "province": "Quebec",
                "website": "https://www.mcgill.ca/",
                "programs_count": 200
            },
            {
                "id": "concordia",
                "name": "Concordia University",
                "type": "university",
                "city": "Montreal",
                "province": "Quebec",
                "website": "https://www.concordia.ca/",
                "programs_count": 180
            }
        ]
        
        # Filter by type if specified
        if institution_type:
            institutions = [inst for inst in institutions if inst["type"] == institution_type.lower()]
        
        logger.info(f"Retrieved {len(institutions)} institutions (type: {institution_type}, region: {region})")
        
        return {
            "institutions": institutions,
            "total": len(institutions),
            "filters": {
                "type": institution_type,
                "region": region
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get institutions: {str(e)}"
        )