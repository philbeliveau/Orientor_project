from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional, Literal
import logging
import os
import time
from sqlalchemy.orm import Session
from openai import OpenAI
from pydantic import BaseModel

from app.utils.auth import get_current_user_unified as get_current_user
from app.models import User, UserProfile
from app.utils.database import get_db
from app.services.conversation_service import ConversationService
from app.services.category_service import CategoryService
from app.services.chat_message_service import ChatMessageService
from app.services.analytics_service import AnalyticsService
from app.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationListResponse, ConversationFilters
)
from app.schemas.chat_message import ExportRequest, MessageStats

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SendMessageRequest(BaseModel):
    message: str
    mode: Optional[Literal["default", "socratic", "claude"]] = "default"

class SendMessageResponse(BaseModel):
    response: str
    user_message_id: int
    assistant_message_id: int
    tokens_used: int

DEFAULT_SYSTEM_PROMPT = """
You are a helpful AI assistant supporting students in their educational and career journey. 
Provide clear, informative responses while being encouraging and supportive.
"""

SOCRATIC_SYSTEM_PROMPT = """
You are a Socratic educator specializing in helping students discover and articulate thoughts they don't even know they're thinking.

CORE PRINCIPLES:
- Never provide direct answers - Lead students to discover insights themselves
- Ask questions that reveal hidden assumptions
- Create productive cognitive dissonance
- Build metacognitive awareness
- Value exploration over conclusions

QUESTIONING TECHNIQUES:
- "What do you mean when you say...?"
- "What must be true for that to work?"
- "How might someone who disagrees see this?"
- "If that's true, what follows?"

STYLE: Be warm, encouraging, concise (2-3 paragraphs max)
"""

CLAUDE_SYSTEM_PROMPT = """
You are Claude, a direct and intellectually challenging AI mentor.

APPROACH:
- Challenge assumptions directly
- Demand precision - no vague statements
- Push boundaries and comfort zones
- Be provocative to spark real thinking
- Get to the heart of matters quickly

STYLE:
- Direct and concise - no fluff
- "That's surface-level. Dig deeper."
- "You're avoiding the real question."
- "Too vague. Be specific."

Brief and punchy - maximum impact, minimum words.
"""

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat/conversations",
    tags=["conversations"]
)

@router.get("", response_model=ConversationListResponse)
async def get_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    is_favorite: Optional[bool] = None,
    is_archived: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations with optional filters"""
    try:
        from app.schemas.conversation import ConversationFilters
        
        filters = ConversationFilters(
            is_favorite=is_favorite,
            is_archived=is_archived
        )
        
        conversations = await ConversationService.get_user_conversations(
            db, current_user.id, filters, limit, offset
        )
        
        total = await ConversationService.get_conversation_count(
            db, current_user.id, filters
        )
        
        return ConversationListResponse(
            conversations=[ConversationResponse.from_orm(conv) for conv in conversations],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    try:
        new_conversation = await ConversationService.create_conversation(
            db, current_user.id, conversation.initial_message, conversation.title
        )
        return ConversationResponse.from_orm(new_conversation)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation"""
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return ConversationResponse.from_orm(conversation)

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    updates: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation properties"""
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Apply updates
    if updates.title is not None:
        await ConversationService.update_conversation_title(
            db, conversation_id, updates.title, current_user.id
        )
    if updates.category_id is not None:
        await ConversationService.set_category(
            db, conversation_id, updates.category_id, current_user.id
        )
    if updates.is_favorite is not None:
        conversation.is_favorite = updates.is_favorite
    if updates.is_archived is not None:
        conversation.is_archived = updates.is_archived
    
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse.from_orm(conversation)

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation permanently"""
    success = await ConversationService.delete_conversation(
        db, conversation_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"message": "Conversation deleted successfully"}

@router.post("/{conversation_id}/favorite")
async def toggle_favorite(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle favorite status of a conversation"""
    is_favorite = await ConversationService.toggle_favorite(
        db, conversation_id, current_user.id
    )
    if is_favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"is_favorite": is_favorite}

@router.post("/{conversation_id}/archive")
async def toggle_archive(
    conversation_id: int,
    archive: bool = Body(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive or unarchive a conversation"""
    success = await ConversationService.archive_conversation(
        db, conversation_id, current_user.id, archive
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"archived": archive}

@router.post("/{conversation_id}/generate-title")
async def generate_title(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an automatic title for the conversation"""
    title = await ConversationService.auto_generate_title(
        db, conversation_id, current_user.id
    )
    if not title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or unable to generate title"
        )
    return {"title": title}

@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a conversation with unified response format"""
    try:
        # Verify conversation belongs to user
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, current_user.id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        messages = await ChatMessageService.get_conversation_messages(
            db, conversation_id, limit, offset
        )
        
        # Serialize messages in chronological order with consistent format
        serialized_messages = []
        for msg in reversed(messages):  # Chronological order for display
            serialized_messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "tokens_used": msg.tokens_used
            })
        
        return {
            "messages": serialized_messages,
            "total": len(serialized_messages),
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )

@router.get("/{conversation_id}/statistics", response_model=MessageStats)
async def get_conversation_statistics(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a conversation"""
    # Verify conversation belongs to user
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    stats = await ChatMessageService.get_message_statistics(db, conversation_id)
    return stats

@router.post("/{conversation_id}/export")
async def export_conversation(
    conversation_id: int,
    export_request: ExportRequest = Body(ExportRequest()),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export conversation in various formats"""
    # Verify conversation belongs to user
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    try:
        export_data = await ChatMessageService.export_conversation(
            db, conversation_id, export_request.format
        )
        
        # Set appropriate content type based on format
        content_types = {
            "json": "application/json",
            "txt": "text/plain",
            "pdf": "application/pdf"
        }
        
        from fastapi.responses import Response
        
        return Response(
            content=export_data,
            media_type=content_types.get(export_request.format, "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename=conversation_{conversation_id}.{export_request.format}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export conversation"
        )

@router.post("/send/{conversation_id}", response_model=SendMessageResponse)
async def send_message_to_conversation(
    conversation_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to an existing conversation"""
    try:
        start_time = time.time()
        
        # Verify conversation belongs to user
        conversation = await ConversationService.get_conversation_by_id(
            db, conversation_id, current_user.id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get conversation history for context
        messages = await ChatMessageService.get_conversation_messages(db, conversation_id, limit=100)
        
        # Select appropriate system prompt based on mode
        if request.mode == "socratic":
            system_prompt = SOCRATIC_SYSTEM_PROMPT
        elif request.mode == "claude":
            system_prompt = CLAUDE_SYSTEM_PROMPT
        else:
            system_prompt = DEFAULT_SYSTEM_PROMPT
            
        # Build OpenAI messages
        openai_messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add new user message
        openai_messages.append({
            "role": "user", 
            "content": request.message
        })
        
        # Save user message first
        user_message = await ChatMessageService.add_message(
            db, conversation_id, "user", request.message
        )
        
        # Get AI response with appropriate parameters based on mode
        if request.mode == "socratic":
            response = client.chat.completions.create(
                model="gpt-4",
                messages=openai_messages,
                max_tokens=350,
                temperature=0.85,
                presence_penalty=0.7,
                frequency_penalty=0.5
            )
        elif request.mode == "claude":
            response = client.chat.completions.create(
                model="gpt-4",
                messages=openai_messages,
                max_tokens=200,
                temperature=0.8,
                presence_penalty=0.6
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=openai_messages,
                max_tokens=500,
                temperature=0.8
            )
        
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Save AI message
        ai_message = await ChatMessageService.add_message(
            db, conversation_id, "assistant", ai_response, tokens_used=tokens_used
        )
        
        # Update conversation stats
        await ConversationService.update_conversation_stats(
            db, conversation_id, tokens_used
        )
        
        # Record analytics
        await AnalyticsService.record_message_sent(
            db, current_user.id, tokens_used, response_time_ms, conversation.category_id
        )
        
        return SendMessageResponse(
            response=ai_response,
            user_message_id=user_message.id,
            assistant_message_id=ai_message.id,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )