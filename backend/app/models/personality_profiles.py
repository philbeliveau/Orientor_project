"""
Personality assessment and profile models.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..utils.database import Base
import uuid

class PersonalityAssessment(Base):
    """Model for personality assessment sessions."""
    __tablename__ = "personality_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_type = Column(String(50), nullable=False)
    assessment_version = Column(String(20), nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    status = Column(String(20), nullable=False, default="in_progress")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    total_items = Column(Integer)
    completed_items = Column(Integer, default=0)
    validity_flags = Column(JSON, default=dict)
    assessment_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="personality_assessments")
    responses = relationship("PersonalityResponse", back_populates="assessment", cascade="all, delete-orphan")
    profiles = relationship("PersonalityProfile", back_populates="assessment")

class PersonalityResponse(Base):
    """Model for individual personality assessment responses."""
    __tablename__ = "personality_responses"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("personality_assessments.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(100), nullable=False)
    item_type = Column(String(50), nullable=False)
    response_value = Column(JSON, nullable=False)
    response_time_ms = Column(Integer)
    revision_count = Column(Integer, default=0)
    confidence_level = Column(Integer)
    behavioral_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    assessment = relationship("PersonalityAssessment", back_populates="responses")

class PersonalityProfile(Base):
    """Model for computed personality profiles."""
    __tablename__ = "personality_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("personality_assessments.id", ondelete="SET NULL"))
    profile_type = Column(String(50), nullable=False)
    language = Column(String(10))
    scores = Column(JSON, nullable=False)
    confidence_intervals = Column(JSON)
    reliability_estimates = Column(JSON)
    percentile_ranks = Column(JSON)
    narrative_description = Column(Text)
    assessment_version = Column(String(20), nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="personality_profiles")
    assessment = relationship("PersonalityAssessment", back_populates="profiles")