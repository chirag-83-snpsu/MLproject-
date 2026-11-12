import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    ASSESSED = "ASSESSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Applicant details
    applicant_name = Column(String(255), nullable=False)
    applicant_email = Column(String(255), nullable=False)
    applicant_phone = Column(String(50), nullable=True)
    
    # Financial & Demographic Risk Features
    person_age = Column(Integer, nullable=False)
    person_income = Column(Float, nullable=False)
    person_emp_length = Column(Float, nullable=False)
    person_home_ownership = Column(String(50), nullable=False)  # RENT, OWN, MORTGAGE, OTHER
    
    # Loan parameters
    loan_intent = Column(String(50), nullable=False)            # PERSONAL, EDUCATION, MEDICAL, etc.
    loan_grade = Column(String(10), nullable=False)             # A, B, C, D, E, F, G
    loan_amnt = Column(Float, nullable=False)
    loan_int_rate = Column(Float, nullable=False)
    loan_percent_income = Column(Float, nullable=False)
    
    # Credit History & Debt Metrics
    credit_score = Column(Integer, nullable=False)              # 300 - 850
    debt_to_income_ratio = Column(Float, nullable=False)        # 0.05 - 0.75
    revolving_utilization = Column(Float, nullable=False)       # 0.0 - 100.0%
    delinq_2yrs = Column(Integer, default=0)                    # count of delinquencies
    cb_person_default_on_file = Column(String(10), default="N") # Y / N
    cb_person_cred_hist_length = Column(Integer, nullable=False) # years
    
    # Status & metadata
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("User", back_populates="applications")
    assessment = relationship("CreditAssessment", back_populates="application", uselist=False, cascade="all, delete-orphan")
    decision = relationship("UnderwriterDecision", back_populates="application", uselist=False, cascade="all, delete-orphan")

