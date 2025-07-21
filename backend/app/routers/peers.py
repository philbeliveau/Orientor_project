from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..utils.database import get_db
from ..models import User, UserProfile, SuggestedPeers
from ..utils.auth import get_current_user_unified as get_current_user
from ..services.peer_matching_service import find_compatible_peers, generate_enhanced_peer_suggestions
import logging
import asyncio

router = APIRouter(prefix="/peers", tags=["peers"])
logger = logging.getLogger(__name__)

class PeerResponse(BaseModel):
    user_id: int
    name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    similarity: float
    hobbies: Optional[str] = None
    interests: Optional[str] = None
    
    class Config:
        orm_mode = True

class EnhancedPeerResponse(BaseModel):
    user_id: int
    name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    compatibility_score: float
    explanation: str
    score_details: Dict[str, Any]
    
    class Config:
        orm_mode = True

class HomepagePeerResponse(BaseModel):
    user_id: int
    name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    compatibility_score: float
    brief_explanation: str
    avatar_url: Optional[str] = None
    
    class Config:
        orm_mode = True

@router.get("/suggested", response_model=List[PeerResponse])
def get_suggested_peers(
    limit: int = Query(5, gt=0, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suggested peers for the current user."""
    try:
        # Find the user's suggested peers with their profiles
        suggested_peers_query = (
            db.query(
                SuggestedPeers.suggested_id.label("user_id"),
                SuggestedPeers.similarity,
                UserProfile.name,
                UserProfile.major,
                UserProfile.year,
                UserProfile.hobbies,
                UserProfile.interests
            )
            .join(
                UserProfile,
                UserProfile.user_id == SuggestedPeers.suggested_id
            )
            .filter(SuggestedPeers.user_id == current_user.id)
            .order_by(SuggestedPeers.similarity.desc())
            .limit(limit)
        )
        
        suggested_peers = suggested_peers_query.all()
        
        if not suggested_peers:
            # If no suggestions found, return empty list
            logger.info(f"No suggested peers found for user {current_user.id}")
            return []
        
        # Convert to list of PeerResponse objects
        result = []
        for peer in suggested_peers:
            # Convert interests to string if it's a list
            interests = peer.interests
            if isinstance(interests, list):
                interests = " ".join(interests)
            
            result.append({
                "user_id": peer.user_id,
                "name": peer.name,
                "major": peer.major,
                "year": peer.year,
                "similarity": peer.similarity,
                "hobbies": peer.hobbies,
                "interests": interests
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting suggested peers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get suggested peers: {str(e)}"
        )

@router.get("/compatible", response_model=List[EnhancedPeerResponse])
async def get_compatible_peers(
    limit: int = Query(3, gt=0, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get compatible peers with detailed explanations."""
    try:
        # Find compatible peers using enhanced algorithm
        compatible_peers = await find_compatible_peers(db, current_user.id, limit)
        
        if not compatible_peers:
            logger.info(f"No compatible peers found for user {current_user.id}")
            return []
        
        # Convert to response format
        result = []
        for peer_id, score, explanation_data in compatible_peers:
            result.append(EnhancedPeerResponse(
                user_id=peer_id,
                name=explanation_data.get("name"),
                major=explanation_data.get("major"),
                year=explanation_data.get("year"),
                job_title=explanation_data.get("job_title"),
                industry=explanation_data.get("industry"),
                compatibility_score=score,
                explanation=explanation_data.get("explanation", ""),
                score_details=explanation_data.get("score_details", {})
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting compatible peers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get compatible peers: {str(e)}"
        )

@router.get("/homepage", response_model=List[HomepagePeerResponse])
async def get_homepage_peers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get peer suggestions for homepage display."""
    try:
        # Find top 3 compatible peers for homepage
        compatible_peers = await find_compatible_peers(db, current_user.id, 3)
        
        if not compatible_peers:
            logger.info(f"No compatible peers found for homepage for user {current_user.id}")
            return []
        
        # Convert to homepage format with brief explanations
        result = []
        for peer_id, score, explanation_data in compatible_peers:
            # Create brief explanation (first sentence)
            full_explanation = explanation_data.get("explanation", "")
            brief_explanation = full_explanation.split(".")[0] + "." if full_explanation else "Great potential for collaboration."
            
            result.append(HomepagePeerResponse(
                user_id=peer_id,
                name=explanation_data.get("name"),
                major=explanation_data.get("major"),
                year=explanation_data.get("year"),
                compatibility_score=score,
                brief_explanation=brief_explanation,
                avatar_url=None  # TODO: Implement avatar URLs
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting homepage peers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get homepage peers: {str(e)}"
        )

@router.post("/refresh")
async def refresh_peer_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh peer suggestions for the current user."""
    try:
        # Generate enhanced peer suggestions
        success = await generate_enhanced_peer_suggestions(db, current_user.id, 5)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to refresh peer suggestions"
            )
        
        return {"message": "Peer suggestions refreshed successfully"}
        
    except Exception as e:
        logger.error(f"Error refreshing peer suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh peer suggestions: {str(e)}"
        ) 