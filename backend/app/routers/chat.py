from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import os
import logging
import time
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.utils.auth import get_current_user_unified as get_current_user
from app.models import User, UserProfile, Conversation, ChatMessage
from app.utils.database import get_db
from app.services.conversation_service import ConversationService
from app.services.chat_message_service import ChatMessageService
from app.services.analytics_service import AnalyticsService
from app.schemas.conversation import ConversationResponse, ConversationListResponse
from app.schemas.chat_message import ChatMessageResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# Initialize OpenAI client with base configuration
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

logger.info(f"OpenAI API Key exists and starts with: {api_key[:5]}...")

client = OpenAI(
    api_key=api_key,
)

class MessageRequest(BaseModel):
    text: str
    conversation_id: Optional[int] = None

class MessageResponse(BaseModel):
    text: str
    is_user: bool = False
    conversation_id: int
    message_id: int

class ClearHistoryResponse(BaseModel):
    success: bool
    message: str

SYSTEM_PROMPT = """
You are a Socratic mentor guiding students in a fast-paced game of discovery. Your mission:

- Ask short, punchy questions that make them think. No lectures.
- Keep your tone cool, casual, and encouraging.
- Never give direct answers. Help them unlock their own.
- Acknowledge their thoughts in a few words, then nudge them deeper.
- Build on what they say. Challenge gently. Push for clarity.
- Use quick examples based on their interests (movies, books, hobbies) when needed.
- When they share a goal, ask: "Why that one?" "What about it lights you up?"
- Spot patterns in what they say. Mirror it back simply.
- Respect their energy: stay sharp, curious, and brief.

Your goal: Make them feel smart, seen, and motivated — by making them figure it out themselves.
"""

@router.post("/send", response_model=MessageResponse)
async def send_message(
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received message from user {current_user.id}: {message.text}")
        
        # Get or create conversation
        if message.conversation_id:
            # Verify the conversation belongs to the user
            conversation = await ConversationService.get_conversation_by_id(
                db, message.conversation_id, current_user.id
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create a new conversation
            conversation = await ConversationService.create_conversation(
                db, current_user.id, message.text
            )
            
            # Get user's profile information for system prompt
            profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
            
            # Create personalized system message
            system_message = SYSTEM_PROMPT
            if profile:
                system_message += f"\n\nUser Profile Information:\n"
                if profile.name:
                    system_message += f"- Name: {profile.name}\n"
                if profile.age:
                    system_message += f"- Age: {profile.age}\n"
                if profile.sex:
                    system_message += f"- Sex: {profile.sex}\n"
                if profile.major:
                    system_message += f"- Major: {profile.major}\n"
                if profile.year:
                    system_message += f"- Year: {profile.year}\n"
                if profile.gpa:
                    system_message += f"- GPA: {profile.gpa}\n"
                if profile.hobbies:
                    system_message += f"- Hobbies: {profile.hobbies}\n"
                if profile.country:
                    system_message += f"- Country: {profile.country}\n"
                if profile.state_province:
                    system_message += f"- State/Province: {profile.state_province}\n"
                if profile.unique_quality:
                    system_message += f"- Unique Quality: {profile.unique_quality}\n"
                if profile.story:
                    system_message += f"- Personal Story: {profile.story}\n"
                if profile.favorite_movie:
                    system_message += f"- Favorite Movie: {profile.favorite_movie}\n"
                if profile.favorite_book:
                    system_message += f"- Favorite Book: {profile.favorite_book}\n"
                if profile.favorite_celebrities:
                    system_message += f"- Role Models: {profile.favorite_celebrities}\n"
                if profile.learning_style:
                    system_message += f"- Learning Style: {profile.learning_style}\n"
                if profile.interests:
                    system_message += f"- Interests: {profile.interests}\n"
            
            # Add system message to the conversation
            await ChatMessageService.add_message(
                db, conversation.id, "system", system_message
            )
        
        # Add user message to the database
        user_message = await ChatMessageService.add_message(
            db, conversation.id, "user", message.text
        )
        
        # Get recent conversation history for context
        recent_messages = await ChatMessageService.get_conversation_messages(
            db, conversation.id, limit=20
        )
        
        # Build messages for OpenAI (reverse to get chronological order)
        messages_for_openai = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(recent_messages)
        ]
        
        logger.info("Calling OpenAI API...")
        start_time = time.time()
        
        try:
            # Call OpenAI API with the conversation history
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages_for_openai,
                max_tokens=250,
                temperature=0.8,
                presence_penalty=0.6,
                frequency_penalty=0.3,
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract the assistant's response
            assistant_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            
            logger.info(f"Received response from OpenAI: {assistant_response[:50]}...")
            
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {str(openai_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OpenAI API error: {str(openai_error)}"
            )
        
        # Add assistant response to the database
        assistant_message = await ChatMessageService.add_message(
            db,
            conversation.id,
            "assistant",
            assistant_response,
            tokens_used=tokens_used,
            model_used="gpt-3.5-turbo",
            response_time_ms=response_time_ms
        )
        
        # Record analytics
        await AnalyticsService.record_message_sent(
            db,
            current_user.id,
            tokens_used or 0,
            response_time_ms,
            conversation.category_id
        )
        
        # Record conversation start if this is the first message
        if conversation.message_count == 2:  # System + first user message
            await AnalyticsService.record_conversation_started(
                db, current_user.id, conversation.category_id
            )
        
        # Auto-generate title if this is the first exchange
        if conversation.auto_generated_title and conversation.message_count >= 3:
            await ConversationService.auto_generate_title(
                db, conversation.id, current_user.id
            )
        
        return MessageResponse(
            text=assistant_response,
            conversation_id=conversation.id,
            message_id=assistant_message.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get response from AI service: {str(e)}"
        )

@router.post("/clear", response_model=ClearHistoryResponse)
async def clear_history(
    conversation_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user_id = current_user.id
        logger.info(f"Clearing/archiving chat history for user {user_id}")
        
        if conversation_id:
            # Archive specific conversation
            success = await ConversationService.archive_conversation(
                db, conversation_id, user_id, archive=True
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            message = f"Conversation {conversation_id} archived successfully"
        else:
            # Archive all conversations
            conversations = await ConversationService.get_user_conversations(
                db, user_id
            )
            for conv in conversations:
                await ConversationService.archive_conversation(
                    db, conv.id, user_id, archive=True
                )
            message = f"All {len(conversations)} conversations archived successfully"
        
        return ClearHistoryResponse(
            success=True,
            message=message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in clear_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation history: {str(e)}"
        )

# Note: Conversations endpoint moved to conversations_router to avoid conflicts

# Note: Messages endpoint moved to conversations_router to avoid conflicts and ensure consistent response format