from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.assessment import RiskTier, SystemRecommendation

class FeatureAttribution(BaseModel):
    feature_name: str
    raw_attribution: float
    abs_attribution: float

class AdverseActionReason(BaseModel):
    code: str
    title: str
    description: str

class CounterfactualScenario(BaseModel):
    id: str
    title: str
    action_summary: str
    new_probability_of_default: float
    new_credit_risk_score: int
    new_risk_tier: str
    new_recommendation: str
    pd_reduction: float
    score_increase: int
    feasibility: str

class AssessmentResponse(BaseModel):
    id: int
    application_id: int
    model_version: str
    probability_of_default: float
    credit_risk_score: int
    risk_tier: RiskTier
    system_recommendation: SystemRecommendation
    expected_loss: float
    
    feature_attributions: List[Dict[str, Any]]
    top_risk_drivers: List[Dict[str, Any]]
    top_protective_factors: List[Dict[str, Any]]
    narrative_summary: List[str]
    adverse_action_reasons: List[Dict[str, str]]
    counterfactual_scenarios: List[Dict[str, Any]]
    assessed_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WhatIfSimulationRequest(BaseModel):
    application_id: Optional[int] = None
    person_income: Optional[float] = None
    loan_amnt: Optional[float] = None
    revolving_utilization: Optional[float] = None
    debt_to_income_ratio: Optional[float] = None
    credit_score: Optional[int] = None
    delinq_2yrs: Optional[int] = None

class WhatIfSimulationResponse(BaseModel):
    baseline_pd: float
    baseline_score: int
    baseline_tier: str
    simulated_pd: float
    simulated_score: int
    simulated_tier: str
    simulated_recommendation: str
    pd_delta: float
    score_delta: int
    top_risk_drivers: List[Dict[str, Any]]
