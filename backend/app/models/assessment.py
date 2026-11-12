import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class RiskTier(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SystemRecommendation(str, enum.Enum):
    APPROVE = "APPROVE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    REJECT = "REJECT"

class CreditAssessment(Base):
    __tablename__ = "credit_assessments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), unique=True, nullable=False)
    model_version = Column(String(50), default="1.0.0")
    
    # Core Risk Outputs
    probability_of_default = Column(Float, nullable=False)   # 0.0 to 1.0
    credit_risk_score = Column(Integer, nullable=False)      # 300 to 850
    risk_tier = Column(Enum(RiskTier), nullable=False)
    system_recommendation = Column(Enum(SystemRecommendation), nullable=False)
    expected_loss = Column(Float, nullable=False)            # USD
    
    # Explainable AI JSON stores
    shap_values_json = Column(Text, nullable=False)          # Full feature attributions
    top_risk_drivers_json = Column(Text, nullable=False)     # Negative drivers
    top_protective_factors_json = Column(Text, nullable=False) # Protective drivers
    adverse_action_reasons_json = Column(Text, nullable=True) # FCRA reason codes
    counterfactual_json = Column(Text, nullable=True)        # Actionable remedial scenarios
    
    assessed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("LoanApplication", back_populates="assessment")

