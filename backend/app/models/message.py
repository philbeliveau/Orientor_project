from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Sequence
from sqlalchemy.sql import func
from ..utils.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, Sequence("message_id_seq"), primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    body = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships can be added later if needed
    # sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    # recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages") 