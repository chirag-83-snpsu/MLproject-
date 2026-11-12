from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Any, Optional
from datetime import datetime

class PortfolioSummaryResponse(BaseModel):
    total_applications: int
    assessed_applications: int
    pending_applications: int
    approved_count: int
    rejected_count: int
    approval_rate: float
    average_default_probability: float
    average_credit_score: float
    total_requested_capital: float
    total_expected_loss: float
    risk_tier_distribution: Dict[str, int]
    loan_intent_distribution: Dict[str, int]
    recent_trend: List[Dict[str, Any]]

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_email: Optional[str]
    action: str
    entity_type: str
    entity_id: Optional[str]
    details_json: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
