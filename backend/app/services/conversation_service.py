from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models import Conversation, ChatMessage, User
from ..schemas.conversation import ConversationFilters

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations"""
    
    @staticmethod
    async def create_conversation(
        db: Session,
        user_id: int,
        initial_message: str,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation with an initial message"""
        try:
            # Create conversation using raw SQL to ensure sequence default works
            # SQLAlchemy ORM isn't properly applying the sequence default
            from sqlalchemy import text
            
            result = db.execute(text("""
                INSERT INTO conversations (user_id, title, auto_generated_title, 
                                        last_message_at, message_count, total_tokens_used)
                VALUES (:user_id, :title, :auto_generated_title, 
                       :last_message_at, :message_count, :total_tokens_used)
                RETURNING id, created_at, updated_at;
            """), {
                'user_id': user_id,
                'title': title or "New Conversation",
                'auto_generated_title': (title is None),
                'last_message_at': datetime.utcnow(),
                'message_count': 1,
                'total_tokens_used': 0
            })
            
            row = result.fetchone()
            conversation_id, created_at, updated_at = row
            
            # Now fetch the conversation object using the ORM
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            
            if not conversation:
                raise Exception(f"Failed to fetch created conversation with ID {conversation_id}")
            
            # Add the initial system message and user message
            system_message = ChatMessage(
                conversation_id=conversation.id,
                role="system",
                content="You are a helpful AI assistant."
            )
            db.add(system_message)
            
            user_message = ChatMessage(
                conversation_id=conversation.id,
                role="user",
                content=initial_message
            )
            db.add(user_message)
            
            db.commit()
            db.refresh(conversation)
            
            return conversation
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating conversation: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    async def get_user_conversations(
        db: Session,
        user_id: int,
        filters: Optional[ConversationFilters] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """Get conversations for a user with optional filters"""
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        
        if filters:
            if filters.is_favorite is not None:
                query = query.filter(Conversation.is_favorite == filters.is_favorite)
            if filters.is_archived is not None:
                query = query.filter(Conversation.is_archived == filters.is_archived)
            if filters.category_id is not None:
                query = query.filter(Conversation.category_id == filters.category_id)
            if filters.search_query:
                # Search in conversation titles
                query = query.filter(
                    Conversation.title.ilike(f"%{filters.search_query}%")
                )
            if filters.date_from:
                query = query.filter(Conversation.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(Conversation.created_at <= filters.date_to)
        
        # Order by last message time or creation time
        query = query.order_by(
            Conversation.last_message_at.desc().nullslast(),
            Conversation.created_at.desc()
        )
        
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    async def get_conversation_by_id(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """Get a specific conversation if it belongs to the user"""
        return db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
    
    @staticmethod
    async def update_conversation_title(
        db: Session,
        conversation_id: int,
        title: str,
        user_id: int
    ) -> bool:
        """Update conversation title"""
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, user_id
        )
        if not conversation:
            return False
        
        conversation.title = title
        conversation.auto_generated_title = False
        conversation.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating conversation title: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def auto_generate_title(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Optional[str]:
        """Generate a title based on the first few messages"""
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, user_id
        )
        if not conversation:
            return None
        
        # Get the first few messages
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).limit(5).all()
        
        if len(messages) < 2:  # Need at least system and user message
            return None
        
        # Extract user messages for title generation
        user_messages = [msg.content for msg in messages if msg.role == "user"]
        
        if not user_messages:
            return None
        
        # Simple title generation - take first few words of first user message
        # In production, this would use an LLM
        first_message = user_messages[0]
        words = first_message.split()[:6]
        generated_title = " ".join(words)
        if len(first_message) > len(generated_title):
            generated_title += "..."
        
        # Update the conversation
        conversation.title = generated_title
        conversation.auto_generated_title = True
        conversation.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return generated_title
        except SQLAlchemyError as e:
            logger.error(f"Error auto-generating title: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    async def archive_conversation(
        db: Session,
        conversation_id: int,
        user_id: int,
        archive: bool = True
    ) -> bool:
        """Archive or unarchive a conversation"""
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, user_id
        )
        if not conversation:
            return False
        
        conversation.is_archived = archive
        conversation.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error archiving conversation: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def delete_conversation(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Delete a conversation and all its messages"""
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, user_id
        )
        if not conversation:
            return False
        
        try:
            db.delete(conversation)
            db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def toggle_favorite(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Optional[bool]:
        """Toggle favorite status of a conversation"""
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, user_id
        )
        if not conversation:
            return None
        
        conversation.is_favorite = not conversation.is_favorite
        conversation.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return conversation.is_favorite
        except SQLAlchemyError as e:
            logger.error(f"Error toggling favorite: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    async def set_category(
        db: Session,
        conversation_id: int,
        category_id: Optional[int],
        user_id: int
    ) -> bool:
        """Set or remove category for a conversation"""
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, user_id
        )
        if not conversation:
            return False
        
        conversation.category_id = category_id
        conversation.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error setting category: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def get_conversation_count(
        db: Session,
        user_id: int,
        filters: Optional[ConversationFilters] = None
    ) -> int:
        """Get total count of conversations for pagination"""
        query = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == user_id
        )
        
        if filters:
            if filters.is_favorite is not None:
                query = query.filter(Conversation.is_favorite == filters.is_favorite)
            if filters.is_archived is not None:
                query = query.filter(Conversation.is_archived == filters.is_archived)
            if filters.category_id is not None:
                query = query.filter(Conversation.category_id == filters.category_id)
        
        return query.scalar() or 0
    
    @staticmethod
    async def update_conversation_stats(
        db: Session,
        conversation_id: int,
        tokens_used: int
    ) -> bool:
        """Update conversation statistics after adding a message"""
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return False
            
            # Update message count and tokens
            conversation.message_count = conversation.message_count + 2  # user + assistant message
            conversation.total_tokens_used = conversation.total_tokens_used + tokens_used
            conversation.last_message_at = datetime.utcnow()
            
            db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating conversation stats: {str(e)}")
            db.rollback()
            return False