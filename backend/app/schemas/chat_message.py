from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class SearchFilters(BaseModel):
    """Filters for searching messages"""
    conversation_id: Optional[int] = None
    role: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    category_id: Optional[int] = None


class MessageStats(BaseModel):
    """Statistics for messages in a conversation"""
    total_messages: int
    messages_by_role: Dict[str, int]
    total_tokens: int
    avg_response_time_ms: float
    first_message_at: Optional[datetime]
    last_message_at: Optional[datetime]


class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    role: str
    content: str


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response"""
    id: int
    conversation_id: int
    created_at: datetime
    tokens_used: Optional[int]
    model_used: Optional[str]
    response_time_ms: Optional[int]
    message_metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True
        protected_namespaces = ()


class SearchResult(BaseModel):
    """Schema for message search result"""
    id: int
    conversation_id: int
    conversation_title: str
    role: str
    content: str
    highlighted_content: str
    created_at: datetime
    rank: float


class ExportRequest(BaseModel):
    """Schema for export request"""
    format: str = "json"  # json, txt, pdf