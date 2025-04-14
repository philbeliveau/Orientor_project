from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..utils.database import get_db
from ..models import User, UserProfile, SuggestedPeers
from ..routes.user import get_current_user
import logging

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
            result.append({
                "user_id": peer.user_id,
                "name": peer.name,
                "major": peer.major,
                "year": peer.year,
                "similarity": peer.similarity,
                "hobbies": peer.hobbies,
                "interests": peer.interests
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting suggested peers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get suggested peers: {str(e)}"
        ) 