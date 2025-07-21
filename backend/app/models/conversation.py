from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..utils.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    auto_generated_title = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("conversation_categories.id"), nullable=True, index=True)
    is_favorite = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", lazy="selectin")
    category = relationship("ConversationCategory", back_populates="conversations", lazy="selectin")
    shares = relationship("ConversationShare", back_populates="conversation", cascade="all, delete-orphan")
    tool_invocations = relationship("ToolInvocation", back_populates="conversation", cascade="all, delete-orphan")
    journey_milestones = relationship("UserJourneyMilestone", back_populates="conversation")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', user_id={self.user_id})>"