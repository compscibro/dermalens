"""
ChatMessage model
Stores conversation history with Gemini AI
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, func, Boolean
from sqlalchemy.orm import relationship
from backend.db.session import Base


class ChatMessage(Base):
    """Chat message with AI assistant"""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Message content
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Context at time of message
    current_scan_id = Column(Integer, ForeignKey("scans.id", ondelete="SET NULL"), nullable=True)
    current_plan_id = Column(Integer, ForeignKey("treatment_plans.id", ondelete="SET NULL"), nullable=True)
    
    # User concerns/symptoms reported
    reported_concerns = Column(JSON, nullable=True)  # List of reported issues
    
    # AI metadata
    model_used = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Flagging
    contains_medical_advice = Column(Boolean, default=False)
    requires_follow_up = Column(Boolean, default=False)
    
    # Session management
    session_id = Column(String, nullable=True)  # Group related messages
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")
    scan = relationship("Scan", foreign_keys=[current_scan_id])
    treatment_plan = relationship("TreatmentPlan", foreign_keys=[current_plan_id])
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role})>"
