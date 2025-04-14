from sqlalchemy import text, desc
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel
from datetime import datetime
from ..models import Message, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageResponse(BaseModel):
    message_id: int
    sender_id: int
    recipient_id: int
    body: str
    timestamp: datetime

def send_message(db: Session, sender_id: int, recipient_id: int, body: str) -> Optional[MessageResponse]:
    """
    Send a message from one user to another.
    
    Args:
        db: Database session
        sender_id: ID of the user sending the message
        recipient_id: ID of the user receiving the message
        body: Content of the message
        
    Returns:
        MessageResponse object if successful, None otherwise
    """
    try:
        # Validate users exist
        sender = db.query(User).filter(User.id == sender_id).first()
        recipient = db.query(User).filter(User.id == recipient_id).first()
        
        if not sender or not recipient:
            logger.error(f"Invalid user IDs: sender={sender_id}, recipient={recipient_id}")
            return None
        
        # Sanitize and validate message body
        if not body or not body.strip():
            logger.error("Message body cannot be empty")
            return None
            
        # Create new message
        new_message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            body=body
        )
        
        # Add to database
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        logger.info(f"Message sent from user {sender_id} to user {recipient_id}")
        
        return MessageResponse(
            message_id=new_message.message_id,
            sender_id=new_message.sender_id,
            recipient_id=new_message.recipient_id,
            body=new_message.body,
            timestamp=new_message.timestamp
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error sending message: {str(e)}")
        return None

def get_conversation(db: Session, user_id: int, peer_id: int, limit: int = 20) -> List[MessageResponse]:
    """
    Retrieve the conversation between two users.
    
    Args:
        db: Database session
        user_id: ID of the first user
        peer_id: ID of the second user
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of MessageResponse objects
    """
    try:
        # Validate users exist
        user = db.query(User).filter(User.id == user_id).first()
        peer = db.query(User).filter(User.id == peer_id).first()
        
        if not user or not peer:
            logger.error(f"Invalid user IDs: user={user_id}, peer={peer_id}")
            return []
        
        # Get messages between the two users
        messages = db.query(Message).filter(
            ((Message.sender_id == user_id) & (Message.recipient_id == peer_id)) |
            ((Message.sender_id == peer_id) & (Message.recipient_id == user_id))
        ).order_by(desc(Message.timestamp)).limit(limit).all()
        
        # Convert to response objects
        result = []
        for msg in messages:
            result.append(MessageResponse(
                message_id=msg.message_id,
                sender_id=msg.sender_id,
                recipient_id=msg.recipient_id,
                body=msg.body,
                timestamp=msg.timestamp
            ))
        
        logger.info(f"Retrieved {len(result)} messages between users {user_id} and {peer_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        return []

def get_user_suggested_peers(db: Session, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the top suggested peers for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of peers to retrieve
        
    Returns:
        List of suggested peer IDs with similarity scores
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.error(f"Invalid user ID: {user_id}")
            return []
        
        # Get suggested peers
        suggested_peers = db.execute(
            text("""
                SELECT suggested_id, similarity 
                FROM suggested_peers 
                WHERE user_id = :user_id 
                ORDER BY similarity DESC 
                LIMIT :limit
            """),
            {"user_id": user_id, "limit": limit}
        ).fetchall()
        
        # Convert to list of dicts
        result = []
        for peer_id, similarity in suggested_peers:
            result.append({
                "peer_id": peer_id,
                "similarity": similarity
            })
        
        logger.info(f"Retrieved {len(result)} suggested peers for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving suggested peers: {str(e)}")
        return [] 