from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from ..models.underwriter import UnderwriterFinalDecision

class UnderwriterDecisionCreate(BaseModel):
    final_decision: UnderwriterFinalDecision
    is_override: bool = False
    override_reason: Optional[str] = None
    notes: Optional[str] = None

class UnderwriterDecisionResponse(BaseModel):
    id: int
    application_id: int
    decided_by_user_id: int
    decided_by_name: Optional[str] = None
    final_decision: UnderwriterFinalDecision
    is_override: bool
    override_reason: Optional[str]
    notes: Optional[str]
    decided_at: datetime

    model_config = ConfigDict(from_attributes=True)
