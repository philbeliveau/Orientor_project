"""
Career Progression API Router

Provides GraphSage-based career progression endpoints for skill extraction
and intelligent career path recommendations.

Endpoints:
- GET /career-progression/{occupation_id}: Get career progression skills
- GET /career-progression/{occupation_id}/personalized: Get personalized progression
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.services.career_progression_service import CareerProgressionService
from app.utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from app.models import User

# Configure logging
logger = logging.getLogger(__name__)

# Request/Response schemas
class CareerProgressionParams(BaseModel):
    depth: int = Field(3, ge=1, le=6, description="Maximum traversal depth (1-6)")
    max_skills_per_tier: int = Field(5, ge=3, le=10, description="Maximum skills per tier (3-10)")
    min_similarity: float = Field(0.4, ge=0.1, le=0.9, description="Minimum GraphSage similarity (0.1-0.9)")
    include_skill_types: list = Field(["technical", "soft", "general"], description="Skill types to include")
    personalized: bool = Field(True, description="Apply user personalization")

router = APIRouter(
    prefix="/career-progression",
    tags=["career-progression"],
    dependencies=[Depends(get_current_user)],
)

# Global service instance for lazy loading
_career_progression_service = None

def get_career_progression_service():
    """Get or initialize the career progression service with lazy loading"""
    global _career_progression_service
    if _career_progression_service is None:
        _career_progression_service = CareerProgressionService()
    return _career_progression_service

@router.get("/{occupation_id}", response_model=Dict[str, Any])
def get_career_progression(
    occupation_id: str = Path(..., description="ESCO occupation ID to analyze"),
    depth: int = Query(3, ge=1, le=6, description="Maximum GraphSage traversal depth"),
    max_skills_per_tier: int = Query(5, ge=3, le=10, description="Maximum skills per tier"),
    min_similarity: float = Query(0.4, ge=0.1, le=0.9, description="Minimum GraphSage similarity threshold"),
    personalized: bool = Query(False, description="Apply user personalization"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PHASE 1 & 2: Extract career progression skills using GraphSage recursive traversal.
    
    This endpoint implements:
    1. Recursive skill extraction from occupation nodes
    2. Tier-based traversal (tier 1: top 5, tier 2: top 5 each, etc.)
    3. GraphSage score-based ranking within tiers
    4. Intelligent skill filtering and deduplication
    5. Optional user profile personalization
    
    Parameters:
    - occupation_id: ESCO occupation ID to start progression from
    - depth: Maximum traversal depth (X parameter) - recommended 3-4
    - max_skills_per_tier: Maximum skills to extract per tier (default 5)
    - min_similarity: Minimum GraphSage similarity threshold (default 0.4)
    - personalized: Whether to apply user-specific personalization
    
    Returns:
    Tiered career progression with GraphSage scores and intelligent filtering.
    """
    logger.info(f"Career progression request for occupation {occupation_id} by user {current_user.id}")
    logger.info(f"Parameters: depth={depth}, max_per_tier={max_skills_per_tier}, "
               f"min_sim={min_similarity}, personalized={personalized}")
    
    try:
        # Validate occupation_id format (basic ESCO ID validation)
        if not occupation_id or len(occupation_id) < 5:
            raise HTTPException(
                status_code=400,
                detail="Invalid occupation_id format. Must be a valid ESCO occupation ID."
            )
        
        # Get career progression service
        service = get_career_progression_service()
        
        # Extract career progression using GraphSage
        user_id_for_personalization = current_user.id if personalized else None
        
        progression_data = service.extract_career_progression(
            occupation_id=occupation_id,
            depth=depth,
            max_skills_per_tier=max_skills_per_tier,
            min_similarity=min_similarity,
            user_id=user_id_for_personalization
        )
        
        # Check if extraction was successful
        if progression_data.get("error"):
            logger.error(f"Career progression extraction failed: {progression_data['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract career progression: {progression_data['error']}"
            )
        
        # Validate results
        tiers = progression_data.get("tiers", [])
        if not tiers:
            logger.warning(f"No career progression found for occupation {occupation_id}")
            return JSONResponse(
                status_code=404,
                content={
                    "occupation_id": occupation_id,
                    "message": "No career progression skills found for this occupation",
                    "tiers": [],
                    "total_skills": 0,
                    "suggestions": [
                        "Verify the occupation ID is correct",
                        "Try a lower min_similarity threshold",
                        "Check if the occupation exists in the ESCO database"
                    ]
                }
            )
        
        # Log successful extraction
        total_skills = progression_data.get("total_skills", 0)
        depth_achieved = progression_data.get("depth_achieved", 0)
        
        logger.info(f"Career progression extracted successfully: {len(tiers)} tiers, "
                   f"{total_skills} skills, depth {depth_achieved}")
        
        # Add request metadata to response
        progression_data.update({
            "request_params": {
                "occupation_id": occupation_id,
                "depth": depth,
                "max_skills_per_tier": max_skills_per_tier,
                "min_similarity": min_similarity,
                "personalized": personalized
            },
            "user_id": current_user.id,
            "success": True
        })
        
        return JSONResponse(content=progression_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in career progression extraction: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during career progression extraction: {str(e)}"
        )

@router.get("/{occupation_id}/personalized", response_model=Dict[str, Any])
def get_personalized_career_progression(
    occupation_id: str = Path(..., description="ESCO occupation ID to analyze"),
    depth: int = Query(4, ge=1, le=6, description="Maximum GraphSage traversal depth"),
    max_skills_per_tier: int = Query(5, ge=3, le=10, description="Maximum skills per tier"),
    min_similarity: float = Query(0.3, ge=0.1, le=0.9, description="Minimum GraphSage similarity threshold"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get fully personalized career progression based on user profile.
    
    This endpoint automatically applies:
    1. User profile personalization
    2. Enhanced GraphSage scoring
    3. Skill type balancing based on user preferences
    4. Cross-tier deduplication
    5. Performance optimization
    
    Returns:
    Fully personalized career progression optimized for the current user.
    """
    logger.info(f"Personalized career progression request for occupation {occupation_id} by user {current_user.id}")
    
    try:
        # Get career progression service
        service = get_career_progression_service()
        
        # Extract personalized career progression
        progression_data = service.extract_career_progression(
            occupation_id=occupation_id,
            depth=depth,
            max_skills_per_tier=max_skills_per_tier,
            min_similarity=min_similarity,
            user_id=current_user.id  # Always personalized
        )
        
        # Check for errors
        if progression_data.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract personalized progression: {progression_data['error']}"
            )
        
        # Add personalization metadata
        progression_data.update({
            "personalization_level": "full",
            "user_id": current_user.id,
            "personalized": True,
            "optimization_applied": True
        })
        
        logger.info(f"Personalized career progression extracted: {len(progression_data.get('tiers', []))} tiers")
        
        return JSONResponse(content=progression_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in personalized career progression: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{occupation_id}/analyze", response_model=Dict[str, Any])
def analyze_career_progression_performance(
    occupation_id: str = Path(..., description="ESCO occupation ID to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze GraphSage performance for career progression extraction.
    
    Provides insights into:
    1. GraphSage model performance metrics
    2. Similarity score distributions
    3. Tier extraction efficiency
    4. Skill type diversity analysis
    5. Optimization recommendations
    
    Returns:
    Performance analysis and optimization insights.
    """
    logger.info(f"Performance analysis request for occupation {occupation_id}")
    
    try:
        service = get_career_progression_service()
        
        # Run extraction with detailed performance tracking
        progression_data = service.extract_career_progression(
            occupation_id=occupation_id,
            depth=3,
            max_skills_per_tier=5,
            min_similarity=0.4,
            user_id=None  # No personalization for analysis
        )
        
        # Analyze performance metrics
        analysis = {
            "occupation_id": occupation_id,
            "extraction_success": not progression_data.get("error"),
            "total_skills_found": progression_data.get("total_skills", 0),
            "depth_achieved": progression_data.get("depth_achieved", 0),
            "extraction_method": progression_data.get("extraction_method", "unknown")
        }
        
        # Analyze tier quality
        tiers = progression_data.get("tiers", [])
        if tiers:
            tier_analysis = []
            for tier in tiers:
                skills = tier.get("skills", [])
                if skills:
                    scores = [s.get("graphsage_score", 0) for s in skills]
                    skill_types = [s.get("skill_type", "unknown") for s in skills]
                    
                    from collections import Counter
                    type_distribution = dict(Counter(skill_types))
                    
                    tier_analysis.append({
                        "tier_number": tier.get("tier_number"),
                        "skill_count": len(skills),
                        "avg_graphsage_score": sum(scores) / len(scores),
                        "score_range": max(scores) - min(scores) if len(scores) > 1 else 0,
                        "skill_type_distribution": type_distribution
                    })
            
            analysis["tier_analysis"] = tier_analysis
        
        # Performance recommendations
        recommendations = []
        if analysis["total_skills_found"] < 10:
            recommendations.append("Consider lowering min_similarity threshold for more skills")
        if analysis["depth_achieved"] < 2:
            recommendations.append("Increase max_depth for deeper career progression")
        if analysis["extraction_method"] == "fallback_pinecone":
            recommendations.append("GraphSage service not available, using fallback method")
        
        analysis["recommendations"] = recommendations
        analysis["analysis_timestamp"] = progression_data.get("generated_at")
        
        return JSONResponse(content=analysis)
        
    except Exception as e:
        logger.error(f"Error in performance analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
