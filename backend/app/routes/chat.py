from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
import os
import logging
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from app.routes.user import get_current_user
from app.models import User, UserProfile
from sqlalchemy.orm import Session
from app.utils.database import get_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

# Initialize OpenAI client with base configuration
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

logger.info(f"OpenAI API Key exists and starts with: {api_key[:5]}...")

client = OpenAI(
    api_key=api_key,
)

# In-memory conversation history (in a production app, this should be stored in a database)
conversation_history: Dict[int, List[Dict[str, str]]] = {}

class MessageRequest(BaseModel):
    text: str

class MessageResponse(BaseModel):
    text: str
    is_user: bool = False

class ClearHistoryResponse(BaseModel):
    success: bool
    message: str

SYSTEM_PROMPT = """You are a Socratic mentor engaging the student in a "game" of problem-solving. Your role is to:

1. Ask clarifying, guiding questions to help the student reflect, articulate their thoughts, and explore what truly motivates them.
2. Encourage them to discover their own goals and values through questioning and gentle nudges, rather than providing direct answers upfront.
3. Ensure the student thinks deeply and reflects on their options.
4. Help them progress toward self-defined objectives while feeling supported and validated.
5. Use the Socratic method: ask open-ended questions that challenge assumptions and promote critical thinking.
6. Acknowledge and validate their thoughts and feelings while gently pushing them to explore deeper.
7. When they express a goal or interest, ask them to elaborate on why it matters to them.
8. Help them identify patterns in their thinking and interests.
9. Use their personal preferences (favorite movies, books, celebrities) to create relatable examples and analogies.
10. Consider their learning style when suggesting approaches or activities.

Remember: Your goal is not to give answers, but to help them discover their own path through thoughtful questioning."""

@router.post("/send", response_model=MessageResponse)
async def send_message(
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received message from user {current_user.id}: {message.text}")
        
        # Get user's profile information
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        # Initialize conversation history for this user if it doesn't exist yet
        user_id = current_user.id
        if user_id not in conversation_history:
            logger.info(f"Initializing conversation history for user {user_id}")
            
            # Create initial system message with user profile context
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
            
            conversation_history[user_id] = [
                {"role": "system", "content": system_message}
            ]
        
        # Add the new user message to history
        conversation_history[user_id].append({"role": "user", "content": message.text})
        
        logger.info("Calling OpenAI API...")
        try:
            # Call OpenAI API with the entire conversation history
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_history[user_id],
                max_tokens=30,
                temperature=0.8,  # Slightly higher temperature for more creative responses
                presence_penalty=0.6,  # Encourage more diverse responses
                frequency_penalty=0.3,  # Reduce repetition while maintaining coherence
            )
            
            # Extract the assistant's response
            assistant_response = response.choices[0].message.content
            logger.info(f"Received response from OpenAI: {assistant_response[:50]}...")
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {str(openai_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OpenAI API error: {str(openai_error)}"
            )
        
        # Add assistant response to history
        conversation_history[user_id].append({"role": "assistant", "content": assistant_response})
        
        # Limit conversation history to the last 10 messages to avoid token limits
        if len(conversation_history[user_id]) > 11:  # 1 system message + 10 conversation messages
            conversation_history[user_id] = [
                conversation_history[user_id][0],  # Keep the system message
                *conversation_history[user_id][-10:]  # Keep the 10 most recent messages
            ]
        
        return MessageResponse(text=assistant_response)
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get response from AI service: {str(e)}"
        )

@router.post("/clear", response_model=ClearHistoryResponse)
async def clear_history(current_user: User = Depends(get_current_user)):
    try:
        user_id = current_user.id
        logger.info(f"Clearing chat history for user {user_id}")
        if user_id in conversation_history:
            # Reset to just the system message
            conversation_history[user_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        
        return ClearHistoryResponse(
            success=True,
            message="Conversation history cleared successfully"
        )
    except Exception as e:
        logger.error(f"Error in clear_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation history: {str(e)}"
        ) 