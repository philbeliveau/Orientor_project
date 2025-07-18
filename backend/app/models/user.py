from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    saved_recommendations = relationship("SavedRecommendation", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("UserNote", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", uselist=False)
    recommendations = relationship("UserRecommendation", back_populates="user", cascade="all, delete-orphan")
    
    # New relationships
    tree_paths = relationship("TreePath", back_populates="user", cascade="all, delete-orphan")
    node_notes = relationship("NodeNote", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skill_trees = relationship("UserSkillTree", back_populates="user", cascade="all, delete-orphan")
    reflection_responses = relationship("StrengthsReflectionResponse", back_populates="user", cascade="all, delete-orphan")
    representations = relationship("UserRepresentation", back_populates="user", cascade="all, delete-orphan")
    
    # Chat persistence relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    conversation_categories = relationship("ConversationCategory", back_populates="user", cascade="all, delete-orphan")
    conversation_shares = relationship("ConversationShare", back_populates="user", cascade="all, delete-orphan")
    chat_analytics = relationship("UserChatAnalytics", back_populates="user", cascade="all, delete-orphan")
    
    # Course analysis relationships
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    psychological_insights = relationship("PsychologicalInsight", back_populates="user", cascade="all, delete-orphan")
    career_signals = relationship("CareerSignal", back_populates="user", cascade="all, delete-orphan")
    conversation_logs = relationship("ConversationLog", back_populates="user", cascade="all, delete-orphan")
    career_profile_aggregates = relationship("CareerProfileAggregate", back_populates="user", cascade="all, delete-orphan")
    career_goals = relationship("CareerGoal", back_populates="user", cascade="all, delete-orphan")
    
    # Orientator AI relationships
    tool_invocations = relationship("ToolInvocation", back_populates="user")
    journey_milestones = relationship("UserJourneyMilestone", back_populates="user", cascade="all, delete-orphan")
    
    # Personality assessment relationships
    personality_assessments = relationship("PersonalityAssessment", cascade="all, delete-orphan")
    personality_profiles = relationship("PersonalityProfile", cascade="all, delete-orphan")