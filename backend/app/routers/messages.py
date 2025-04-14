from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..utils.database import get_db
from ..models import User, UserProfile
from ..routes.user import get_current_user
from ..utils.messaging import send_message, get_conversation, get_user_suggested_peers, MessageResponse
import logging
from sqlalchemy import text

router = APIRouter(prefix="/messages", tags=["messages"])
logger = logging.getLogger(__name__)

class MessageRequest(BaseModel):
    recipient_id: int
    body: str = Field(..., min_length=1, max_length=5000)

class ConversationPreview(BaseModel):
    peer_id: int
    peer_name: Optional[str] = None
    last_message: str
    timestamp: datetime
    unread_count: int = 0

@router.post("", response_model=MessageResponse)
def create_message(
    message: MessageRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to another user."""
    try:
        result = send_message(db, current_user.id, message.recipient_id, message.body)
        
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Failed to send message. Please check the recipient ID and message content."
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message: {str(e)}"
        )

@router.get("/conversation/{peer_id}", response_model=List[MessageResponse])
def read_conversation(
    peer_id: int,
    limit: int = Query(20, gt=0, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation between current user and another user."""
    try:
        messages = get_conversation(db, current_user.id, peer_id, limit)
        return messages
        
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )

@router.get("/conversations", response_model=List[ConversationPreview])
def read_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active conversations for the current user."""
    try:
        # Find all users the current user has exchanged messages with
        conversation_partners = db.execute(
            text("""
                SELECT DISTINCT 
                    CASE 
                        WHEN sender_id = :user_id THEN recipient_id 
                        ELSE sender_id 
                    END AS peer_id
                FROM messages
                WHERE sender_id = :user_id OR recipient_id = :user_id
            """),
            {"user_id": current_user.id}
        ).fetchall()
        
        # If no conversations found, return empty list
        if not conversation_partners:
            return []
        
        result = []
        
        for (peer_id,) in conversation_partners:
            # Get the most recent message
            latest_message = db.execute(
                text("""
                    SELECT 
                        message_id, 
                        sender_id, 
                        body, 
                        timestamp
                    FROM messages
                    WHERE (sender_id = :user_id AND recipient_id = :peer_id)
                       OR (sender_id = :peer_id AND recipient_id = :user_id)
                    ORDER BY timestamp DESC
                    LIMIT 1
                """),
                {"user_id": current_user.id, "peer_id": peer_id}
            ).fetchone()
            
            if not latest_message:
                continue
            
            # Get peer profile info
            peer_profile = db.query(UserProfile).filter(UserProfile.user_id == peer_id).first()
            peer_name = peer_profile.name if peer_profile and peer_profile.name else f"User {peer_id}"
            
            # Count unread messages (messages sent by peer that weren't read yet)
            # This is a placeholder - in a real implementation you'd have a read_at field
            unread_count = 0
            
            result.append(ConversationPreview(
                peer_id=peer_id,
                peer_name=peer_name,
                last_message=latest_message.body,
                timestamp=latest_message.timestamp,
                unread_count=unread_count
            ))
        
        # Sort by most recent message
        result.sort(key=lambda x: x.timestamp, reverse=True)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving conversations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversations: {str(e)}"
        )

@router.get("/suggested-peers", response_model=List[dict])
def read_suggested_peers(
    limit: int = Query(5, gt=0, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suggested peers for the current user."""
    try:
        peers = get_user_suggested_peers(db, current_user.id, limit)
        return peers
        
    except Exception as e:
        logger.error(f"Error retrieving suggested peers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve suggested peers: {str(e)}"
        ) 