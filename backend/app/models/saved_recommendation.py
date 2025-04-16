from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class SavedRecommendation(Base):
    __tablename__ = "saved_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    oasis_code = Column(String, nullable=False)
    label = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    main_duties = Column(Text, nullable=True)
    role_creativity = Column(Float, nullable=True)
    role_leadership = Column(Float, nullable=True)
    role_digital_literacy = Column(Float, nullable=True)
    role_critical_thinking = Column(Float, nullable=True)
    role_problem_solving = Column(Float, nullable=True)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Define unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('user_id', 'oasis_code', name='uq_user_oasis_code'),
    )
    
    # Relationships
    user = relationship("User", back_populates="saved_recommendations")
    notes = relationship("UserNote", back_populates="recommendation", cascade="all, delete-orphan") 