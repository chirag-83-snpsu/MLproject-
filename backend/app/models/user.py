import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from ..database import Base

class UserRole(str, enum.Enum):
    LOAN_OFFICER = "loan_officer"
    RISK_ANALYST = "risk_analyst"
    COMPLIANCE_OFFICER = "compliance_officer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.LOAN_OFFICER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    applications = relationship("LoanApplication", back_populates="created_by")
    decisions = relationship("UnderwriterDecision", back_populates="decided_by")

