from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    favorite_movie = Column(String(255))
    favorite_book = Column(String(255))
    favorite_celebrities = Column(Text)  # Stored as comma-separated values
    learning_style = Column(String(50))  # Visual, Auditory, Reading/Writing, Kinesthetic
    interests = Column(Text)  # Stored as comma-separated values
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="profile") 