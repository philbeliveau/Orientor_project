"""
Socratic Chat Service - Enhanced AI Chat with Dual Modes

This service provides two distinct conversational modes:
1. Socratic Mode: Uses guided discovery and questioning to help students articulate hidden thoughts
2. Claude Mode: Direct, bold, and challenging approach using Anthropic's Claude API
"""

import logging
from typing import Dict, List, Any, Optional, Literal
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
import os
import json

# Optional anthropic import
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

from ..models import User, UserProfile, UserSkill, Conversation, ChatMessage
from .conversation_service import ConversationService
from .chat_message_service import ChatMessageService

logger = logging.getLogger(__name__)

ChatMode = Literal["socratic", "claude"]

class SocraticChatService:
    """
    Enhanced chat service with Socratic questioning and Claude integration.
    """
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        if ANTHROPIC_AVAILABLE:
            self.claude_client = anthropic.AsyncAnthropic(api_key=os.environ.get("CLAUDE_KEY"))
        else:
            self.claude_client = None
            logger.warning("Anthropic library not available. Claude mode will be disabled.")
        
    async def send_message(self, 
                          user_id: int, 
                          message_text: str,
                          mode: ChatMode,
                          conversation_id: Optional[int], 
                          db: Session) -> Dict[str, Any]:
        """
        Send a message in the specified chat mode.
        
        Args:
            user_id: User ID
            message_text: User's message
            mode: Chat mode - "socratic" or "claude"
            conversation_id: Optional conversation ID
            db: Database session
            
        Returns:
            Response with appropriate styling based on mode
        """
        try:
            # Get or create conversation
            if conversation_id:
                conversation = await ConversationService.get_conversation_by_id(
                    db, conversation_id, user_id
                )
                if not conversation:
                    raise ValueError("Conversation not found")
            else:
                # Create conversation with a clean title (mode can be inferred from context)
                conversation = await ConversationService.create_conversation(
                    db, user_id, f"{message_text[:50]}..."
                )
                
            # Add user message to conversation
            user_message = await ChatMessageService.add_message(
                db, conversation.id, "user", message_text
            )
            
            # Get recent conversation history
            recent_messages = await ChatMessageService.get_conversation_messages(
                db, conversation.id, limit=20
            )
            
            # Debug logging
            logger.info(f"Conversation {conversation.id} has {len(recent_messages)} messages")
            for i, msg in enumerate(recent_messages[-5:]):  # Log last 5 messages
                logger.info(f"  Message {i}: {msg.role} - {msg.content[:50]}...")
            
            # Get user profile for context
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
            
            # Generate response based on mode
            if mode == "socratic":
                response_content = await self._generate_socratic_response(
                    message_text, recent_messages, user_profile, user_skills
                )
                model_used = "gpt-4"
            else:  # claude mode
                if not ANTHROPIC_AVAILABLE or self.claude_client is None:
                    # Fallback to GPT-4 with Claude-style prompting
                    response_content = await self._generate_claude_fallback_response(
                        message_text, recent_messages, user_profile, user_skills
                    )
                    model_used = "gpt-4-claude-style"
                else:
                    response_content = await self._generate_claude_response(
                        message_text, recent_messages, user_profile, user_skills
                    )
                    model_used = "claude-3-sonnet"
                
            # Add assistant response to conversation
            assistant_message = await ChatMessageService.add_message(
                db, conversation.id, "assistant", response_content,
                model_used=model_used
            )
            
            return {
                "response": response_content,
                "conversation_id": conversation.id,
                "message_id": assistant_message.id,
                "mode": mode,
                "mode_characteristics": self._get_mode_characteristics(mode)
            }
            
        except Exception as e:
            logger.error(f"Error in Socratic chat service: {str(e)}")
            raise
            
    async def _generate_socratic_response(self, 
                                        message: str,
                                        history: List[ChatMessage],
                                        profile: Optional[UserProfile],
                                        skills: Optional[UserSkill]) -> str:
        """Generate response using Socratic method."""
        
        system_prompt = """You are a Socratic educator specializing in helping students discover and articulate thoughts they don't even know they're thinking. Your approach centers on guided discovery through strategic questioning.

CORE PRINCIPLES:
1. **Never provide direct answers** - Lead students to discover insights themselves
2. **Ask questions that reveal hidden assumptions** - Help students see what they take for granted
3. **Create productive cognitive dissonance** - Gently challenge contradictions in thinking
4. **Build metacognitive awareness** - Help students understand their own thinking process
5. **Celebrate the journey, not the destination** - Value exploration over conclusions

QUESTIONING TECHNIQUES:
- Start with clarification: "What do you mean when you say...?"
- Probe assumptions: "What must be true for that to work?"
- Shift perspectives: "How might someone who disagrees see this?"
- Explore implications: "If that's true, what follows?"
- Reflect on thinking: "What made you think of that just now?"

RESPONSE PATTERNS:
1. Acknowledge what the student shared (briefly)
2. Identify the deeper question or assumption behind their statement
3. Ask 1-2 thoughtful questions that guide deeper exploration
4. End with an invitation to explore further

STYLE GUIDELINES:
- Be warm and encouraging, never judgmental
- Use phrases like "I'm curious about...", "Help me understand...", "What if..."
- Keep responses concise (2-3 paragraphs max)
- One powerful question is better than three shallow ones
- Create space for the student to think

Remember: Your goal is not to lead students to predetermined answers, but to help them discover their own understanding through guided exploration."""

        # Add user context if available
        if profile:
            context = f"\n\nSTUDENT CONTEXT:\n"
            if profile.career_goals:
                context += f"- Career interests: {profile.career_goals}\n"
                logger.info(f"Adding career goals to context: {profile.career_goals}")
            if profile.interests:
                context += f"- General interests: {profile.interests}\n"
            if profile.major:
                context += f"- Field of study: {profile.major}\n"
            system_prompt += context
            logger.info(f"User profile context added: {context}")
        else:
            logger.info("No user profile found, using generic context")
            
        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (exclude ALL system messages to avoid conflicts)
        logger.info(f"Adding {len(history)} messages to conversation context")
        for msg in reversed(history[-10:]):  # Last 10 messages
            if msg.role in ["user", "assistant"]:  # Only include user and assistant messages
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
                logger.info(f"  Added to OpenAI: {msg.role} - {msg.content[:50]}...")
            elif msg.role == "system":
                logger.info(f"  Skipped system message: {msg.content[:50]}...")
        
        logger.info(f"Final OpenAI messages count: {len(messages)}")
        logger.info(f"Full message payload being sent to OpenAI: {messages}")
                
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.85,
            max_tokens=350,
            presence_penalty=0.7,
            frequency_penalty=0.5
        )
        
        logger.info(f"OpenAI response: {response.choices[0].message.content[:100]}...")
        
        return response.choices[0].message.content
        
    async def _generate_claude_response(self,
                                      message: str,
                                      history: List[ChatMessage],
                                      profile: Optional[UserProfile],
                                      skills: Optional[UserSkill]) -> str:
        """Generate response using Claude's bold, challenging style."""
        
        system_prompt = """You are Claude, a direct and intellectually challenging AI mentor. Your style is bold, thought-provoking, and uncompromising in pushing students to think deeper.

CORE APPROACH:
1. **Challenge assumptions directly** - Call out fuzzy thinking immediately
2. **Demand precision** - Don't let vague statements slide
3. **Push boundaries** - Take students out of their comfort zone
4. **Be provocative** - Use strong statements to spark real thinking
5. **Cut through BS** - Get to the heart of matters quickly

COMMUNICATION STYLE:
- Be direct and concise - no fluff
- Use strong, confident language
- Challenge with statements like "That's surface-level. Dig deeper."
- Push back: "You're avoiding the real question here."
- Demand clarity: "That's too vague. Be specific."
- Provoke thought: "You're thinking too small. What if..."

RESPONSE STRUCTURE:
1. Cut straight to the core issue (1-2 sentences)
2. Challenge their thinking directly
3. Push them toward a deeper level of analysis
4. End with a provocative question or statement

TONE:
- Confident and assertive, but not mean
- Intellectually demanding but respectful
- Like a tough professor who believes in the student's potential
- Brief and punchy - maximum impact, minimum words

Remember: Your job is to be the intellectual sparring partner who won't let students settle for shallow thinking. Be the challenge they need to grow."""

        # Add user context if available
        if profile:
            context = f"\n\nSTUDENT PROFILE:\n"
            if profile.career_goals:
                context += f"- Claims to want: {profile.career_goals}\n"
            if profile.interests:
                context += f"- Interests: {profile.interests}\n"
            if profile.major:
                context += f"- Studying: {profile.major}\n"
            context += "Use this info to make your challenges more targeted and personal."
            system_prompt += context
            
        # Prepare messages for Claude
        messages = []
        
        # Add conversation history
        for msg in reversed(history[-10:]):  # Last 10 messages
            if msg.role == "user":
                messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.role == "assistant":
                messages.append({
                    "role": "assistant",
                    "content": msg.content
                })
                
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        response = await self.claude_client.messages.create(
            model="claude-3-haiku-20240307",
            system=system_prompt,
            messages=messages,
            max_tokens=300,
            temperature=0.9
        )
        
        return response.content[0].text
        
    async def _generate_claude_fallback_response(self,
                                               message: str,
                                               history: List[ChatMessage],
                                               profile: Optional[UserProfile],
                                               skills: Optional[UserSkill]) -> str:
        """Generate Claude-style response using OpenAI as fallback when Anthropic is unavailable."""
        
        system_prompt = """You are Claude, a direct and intellectually challenging AI mentor. Your style is bold, thought-provoking, and uncompromising in pushing students to think deeper.

CORE APPROACH:
1. **Challenge assumptions directly** - Call out fuzzy thinking immediately
2. **Demand precision** - Don't let vague statements slide
3. **Push boundaries** - Take students out of their comfort zone
4. **Be provocative** - Use strong statements to spark real thinking
5. **Cut through BS** - Get to the heart of matters quickly

COMMUNICATION STYLE:
- Be direct and concise - no fluff
- Use strong, confident language
- Challenge with statements like "That's surface-level. Dig deeper."
- Push back: "You're avoiding the real question here."
- Demand clarity: "That's too vague. Be specific."
- Provoke thought: "You're thinking too small. What if..."

Keep responses under 150 words and end with a provocative question."""

        # Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add context if available
        if profile or skills:
            context = "User context: "
            if profile:
                context += f"Student studying {profile.major or 'undeclared'}, "
            if skills:
                context += f"interested in developing skills in various areas."
            messages.append({"role": "system", "content": context})
        
        # Add recent conversation history
        for msg in history[-10:]:  # Last 10 messages
            if msg.role in ["user", "assistant"]:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=200,
            temperature=0.8,
        )
        
        return response.choices[0].message.content
        
    def _get_mode_characteristics(self, mode: ChatMode) -> Dict[str, Any]:
        """Get characteristics of the chat mode for UI styling."""
        if mode == "socratic":
            return {
                "name": "Socratic Guide",
                "description": "Gentle questioning to help you discover insights",
                "color": "blue",
                "icon": "🤔",
                "traits": ["Thoughtful", "Patient", "Exploratory", "Nurturing"]
            }
        else:  # claude
            return {
                "name": "Claude Challenger",
                "description": "Direct and bold challenges to push your thinking",
                "color": "purple",
                "icon": "💪",
                "traits": ["Direct", "Bold", "Challenging", "Provocative"]
            }
            
    async def get_mode_introduction(self, mode: ChatMode, user_id: int, db: Session) -> str:
        """Get an introduction message for the selected mode."""
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        name = user_profile.name if user_profile and user_profile.name else "there"
        
        if mode == "socratic":
            return f"""Hello {name}! I'm here as your Socratic guide. 

My role isn't to give you answers, but to help you discover insights you didn't know you had. Through thoughtful questions and gentle exploration, we'll uncover the depths of your thinking together.

What's on your mind today? What would you like to explore?"""
        else:  # claude
            return f"""Alright {name}, let's cut to the chase.

I'm Claude - I'm here to challenge your thinking, not coddle it. I'll push you hard, question your assumptions, and won't let you settle for surface-level answers.

If you want comfortable chitchat, you picked the wrong mode. But if you want to actually grow and think deeper, you're in the right place.

What are you really trying to figure out?"""


# Global instance
socratic_chat_service = SocraticChatService()