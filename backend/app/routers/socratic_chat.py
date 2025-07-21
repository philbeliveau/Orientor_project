"""
Socratic Chat Router - API endpoints for dual-mode chat functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

from ..utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from app.models import User
from ..services.socratic_chat_service import socratic_chat_service, ChatMode

router = APIRouter(prefix="/socratic-chat", tags=["socratic-chat"])

class SendMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    mode: ChatMode = Field(..., description="Chat mode: 'socratic' or 'claude'")
    conversation_id: Optional[int] = None

class GetIntroductionRequest(BaseModel):
    mode: ChatMode = Field(..., description="Chat mode: 'socratic' or 'claude'")

@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send a message in the selected chat mode.
    
    Modes:
    - socratic: Gentle Socratic questioning to help discover insights
    - claude: Bold, direct challenges using Claude API
    """
    try:
        result = await socratic_chat_service.send_message(
            user_id=current_user.id,
            message_text=request.text,
            mode=request.mode,
            conversation_id=request.conversation_id,
            db=db
        )
        
        return {
            "success": True,
            **result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )

@router.post("/introduction")
async def get_mode_introduction(
    request: GetIntroductionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get an introduction message for the selected chat mode.
    """
    try:
        introduction = await socratic_chat_service.get_mode_introduction(
            mode=request.mode,
            user_id=current_user.id,
            db=db
        )
        
        characteristics = socratic_chat_service._get_mode_characteristics(request.mode)
        
        return {
            "success": True,
            "introduction": introduction,
            "mode_info": characteristics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get introduction: {str(e)}"
        )

@router.get("/modes")
async def get_available_modes() -> Dict[str, Any]:
    """
    Get information about available chat modes.
    """
    return {
        "success": True,
        "modes": {
            "socratic": {
                "id": "socratic",
                "name": "Socratic Guide",
                "description": "Discover insights through thoughtful questioning",
                "extended_description": "This mode uses the Socratic method to help you uncover thoughts and insights you didn't know you had. Through gentle, probing questions, you'll explore ideas deeply and develop stronger critical thinking skills.",
                "best_for": [
                    "Deep self-reflection",
                    "Exploring complex ideas",
                    "Developing critical thinking",
                    "Understanding your own assumptions"
                ],
                "style": "Gentle, patient, exploratory",
                "powered_by": "GPT-4"
            },
            "claude": {
                "id": "claude",
                "name": "Claude Challenger",
                "description": "Direct challenges to push your thinking further",
                "extended_description": "Claude mode provides a more direct, challenging approach. Expect bold questions, intellectual pushback, and a no-nonsense style that cuts through surface-level thinking to help you grow.",
                "best_for": [
                    "Breaking through mental blocks",
                    "Challenging your assumptions",
                    "Rapid intellectual growth",
                    "Getting unstuck from circular thinking"
                ],
                "style": "Bold, direct, provocative",
                "powered_by": "Claude 3 Sonnet"
            }
        }
    }

@router.get("/status")
async def get_chat_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check the status of chat services.
    """
    return {
        "success": True,
        "services_available": {
            "socratic_mode": bool(socratic_chat_service.openai_client.api_key),
            "claude_mode": bool(socratic_chat_service.claude_client.api_key),
        },
        "user_id": current_user.id
    }