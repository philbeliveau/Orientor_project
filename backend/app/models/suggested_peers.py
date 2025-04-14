from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class SuggestedPeers(Base):
    __tablename__ = "suggested_peers"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    suggested_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    similarity = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships (optional, uncomment if needed)
    # user = relationship("User", foreign_keys=[user_id], back_populates="suggested_peers")
    # suggested_user = relationship("User", foreign_keys=[suggested_id], back_populates="suggested_to") 