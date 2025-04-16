from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Skill fields
    creativity = Column(Float, nullable=True)
    leadership = Column(Float, nullable=True)
    digital_literacy = Column(Float, nullable=True)
    critical_thinking = Column(Float, nullable=True)
    problem_solving = Column(Float, nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    saved_recommendations = relationship("SavedRecommendation", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("UserNote", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", uselist=False) 