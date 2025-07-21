"""
Enhanced Chat Router with GraphSage Integration

This router provides enhanced chat functionality with GraphSage-based
skill relevance analysis and personalized learning recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
import logging
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.utils.auth import get_current_user_unified as get_current_user
from app.models import User
from app.utils.database import get_db
from app.services.enhanced_chat_service import enhanced_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/enhanced-chat",
    tags=["enhanced-chat"]
)

class EnhancedMessageRequest(BaseModel):
    text: str
    conversation_id: Optional[int] = None

class EnhancedMessageResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int
    graphsage_insights: Dict[str, Any]
    enhanced_features: Dict[str, bool]

class SkillExplanationRequest(BaseModel):
    skill_name: str

class SkillExplanationResponse(BaseModel):
    skill_name: str
    relevance_score: float
    explanation: str
    skill_metadata: Dict[str, Any]
    graphsage_analysis: bool

class LearningRecommendationsResponse(BaseModel):
    high_impact_skills: List[Dict[str, Any]]
    foundational_skills: List[Dict[str, Any]]
    complementary_skills: List[Dict[str, Any]]
    learning_path: List[Dict[str, Any]]

class CareerPathAnalysisRequest(BaseModel):
    career_path: str

class CareerPathAnalysisResponse(BaseModel):
    career_path: str
    compatibility_score: float
    matching_skills: List[Dict[str, Any]]
    skill_gaps: List[Dict[str, Any]]
    recommendations: str

@router.post("/send", response_model=EnhancedMessageResponse)
async def send_enhanced_message(
    message: EnhancedMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message with GraphSage enhancement and get intelligent response.
    """
    try:
        logger.info(f"Enhanced chat message from user {current_user.id}: {message.text}")
        
        result = await enhanced_chat_service.send_enhanced_message(
            current_user.id, message.text, message.conversation_id, db
        )
        
        return EnhancedMessageResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process enhanced chat message: {str(e)}"
        )

@router.post("/skill-explanation", response_model=SkillExplanationResponse)
async def get_skill_explanation(
    request: SkillExplanationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation for why a specific skill is relevant for the user.
    """
    try:
        logger.info(f"Skill explanation request from user {current_user.id}: {request.skill_name}")
        
        result = await enhanced_chat_service.get_skill_explanation(
            current_user.id, request.skill_name, db
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
        return SkillExplanationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting skill explanation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get skill explanation: {str(e)}"
        )

@router.get("/learning-recommendations", response_model=LearningRecommendationsResponse)
async def get_learning_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized learning recommendations based on GraphSage analysis.
    """
    try:
        logger.info(f"Learning recommendations request from user {current_user.id}")
        
        result = await enhanced_chat_service.generate_learning_recommendations(
            current_user.id, db
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
        return LearningRecommendationsResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating learning recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate learning recommendations: {str(e)}"
        )

@router.post("/career-path-analysis", response_model=CareerPathAnalysisResponse)
async def analyze_career_path(
    request: CareerPathAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze how well a career path matches the user's skills using GraphSage.
    """
    try:
        logger.info(f"Career path analysis request from user {current_user.id}: {request.career_path}")
        
        result = await enhanced_chat_service.analyze_career_path_compatibility(
            current_user.id, request.career_path, db
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
        return CareerPathAnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing career path: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze career path: {str(e)}"
        )

@router.get("/graphsage-insights")
async def get_graphsage_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get general GraphSage insights for the current user.
    """
    try:
        logger.info(f"GraphSage insights request from user {current_user.id}")
        
        # Get user's general GraphSage insights
        from app.services.graphsage_llm_integration import graphsage_llm
        
        # Get user profile for context
        from app.models import UserProfile, UserSkill
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
        # Compute general skill relevance
        user_skill_dict = {}
        if user_skills:
            skill_mapping = {
                "creativity": "Creativity",
                "leadership": "Leadership",
                "digital_literacy": "Digital Literacy",
                "critical_thinking": "Critical Thinking",
                "problem_solving": "Problem Solving"
            }
            
            for skill_key, skill_name in skill_mapping.items():
                value = getattr(user_skills, skill_key)
                if value is not None:
                    user_skill_dict[skill_name] = value
                    
        career_goals = []
        if user_profile.career_goals:
            career_goals = [user_profile.career_goals]
        if user_profile.interests:
            career_goals.extend(user_profile.interests.split(","))
            
        relevance_scores = graphsage_llm.compute_skill_relevance_scores(
            user_skill_dict, career_goals
        )
        
        # Get top skills
        top_skills = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        insights = {
            "user_profile_summary": {
                "career_goals": user_profile.career_goals,
                "interests": user_profile.interests,
                "current_skills": user_skill_dict
            },
            "top_relevant_skills": [],
            "graphsage_model_status": {
                "model_loaded": graphsage_llm.gnn_model is not None,
                "nodes_available": len(graphsage_llm.node_metadata),
                "edges_available": graphsage_llm.edge_index.shape[1] if graphsage_llm.edge_index is not None else 0
            }
        }
        
        for skill_id, score in top_skills:
            skill_metadata = graphsage_llm.node_metadata.get(skill_id, {})
            insights["top_relevant_skills"].append({
                "skill_name": skill_metadata.get("label", "Unknown Skill"),
                "relevance_score": score,
                "description": skill_metadata.get("description", "")[:200] + "..." if len(skill_metadata.get("description", "")) > 200 else skill_metadata.get("description", "")
            })
            
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting GraphSage insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get GraphSage insights: {str(e)}"
        )

@router.get("/status")
async def get_enhanced_chat_status():
    """
    Get the status of the enhanced chat system and GraphSage integration.
    """
    try:
        from app.services.graphsage_llm_integration import graphsage_llm
        
        status_info = {
            "enhanced_chat_available": True,
            "graphsage_model_loaded": graphsage_llm.gnn_model is not None,
            "node_metadata_count": len(graphsage_llm.node_metadata),
            "edge_count": graphsage_llm.edge_index.shape[1] if graphsage_llm.edge_index is not None else 0,
            "features": {
                "skill_relevance_analysis": True,
                "personalized_explanations": True,
                "learning_path_generation": True,
                "career_compatibility_analysis": True,
                "conversation_enhancement": True
            }
        }
        
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting enhanced chat status: {str(e)}")
        return {
            "enhanced_chat_available": False,
            "error": str(e),
            "features": {
                "skill_relevance_analysis": False,
                "personalized_explanations": False,
                "learning_path_generation": False,
                "career_compatibility_analysis": False,
                "conversation_enhancement": False
            }
        }