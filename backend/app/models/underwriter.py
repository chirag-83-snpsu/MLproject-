import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class UnderwriterFinalDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

class UnderwriterDecision(Base):
    __tablename__ = "underwriter_decisions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), unique=True, nullable=False)
    decided_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    final_decision = Column(Enum(UnderwriterFinalDecision), nullable=False)
    is_override = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("LoanApplication", back_populates="decision")
    decided_by = relationship("User", back_populates="decisions")

