from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String(255))
    age = Column(Integer)
    sex = Column(String(50))
    major = Column(String(255))
    year = Column(Integer)
    gpa = Column(Float)
    hobbies = Column(Text)
    country = Column(String(255))
    state_province = Column(String(255))
    unique_quality = Column(Text)
    story = Column(Text)
    favorite_movie = Column(String(255))
    favorite_book = Column(String(255))
    favorite_celebrities = Column(Text)  # Stored as comma-separated values
    learning_style = Column(String(50))  # Visual, Auditory, Reading/Writing, Kinesthetic
    interests = Column(Text)  # Stored as comma-separated values
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="profile") 