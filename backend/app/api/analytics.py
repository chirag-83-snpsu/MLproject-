from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.user import User
from ..models.application import LoanApplication, ApplicationStatus
from ..models.assessment import CreditAssessment, RiskTier
from ..schemas.analytics import PortfolioSummaryResponse
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Portfolio Insights"])

@router.get("/portfolio-summary", response_model=PortfolioSummaryResponse)
def get_portfolio_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_apps = db.query(LoanApplication).count()
    assessed_apps = db.query(CreditAssessment).count()
    pending_apps = total_apps - assessed_apps
    
    approved_count = db.query(LoanApplication).filter(LoanApplication.status == ApplicationStatus.APPROVED).count()
    rejected_count = db.query(LoanApplication).filter(LoanApplication.status == ApplicationStatus.REJECTED).count()
    
    decided_total = approved_count + rejected_count
    approval_rate = round((approved_count / decided_total) * 100, 2) if decided_total > 0 else 0.0
    
    # Financial Aggregations
    total_capital = db.query(func.sum(LoanApplication.loan_amnt)).scalar() or 0.0
    total_expected_loss = db.query(func.sum(CreditAssessment.expected_loss)).scalar() or 0.0
    
    avg_pd = db.query(func.avg(CreditAssessment.probability_of_default)).scalar() or 0.0
    avg_score = db.query(func.avg(CreditAssessment.credit_risk_score)).scalar() or 0.0
    
    # Risk Tier Breakdown
    tier_counts = {tier.value: 0 for tier in RiskTier}
    tier_query = db.query(CreditAssessment.risk_tier, func.count(CreditAssessment.id)).group_by(CreditAssessment.risk_tier).all()
    for tier, count in tier_query:
        tier_counts[tier.value] = count
        
    # Loan Intent Breakdown
    intent_counts = {}
    intent_query = db.query(LoanApplication.loan_intent, func.count(LoanApplication.id)).group_by(LoanApplication.loan_intent).all()
    for intent, count in intent_query:
        intent_counts[intent] = count
        
    # Recent Application Distribution
    recent_apps = db.query(
        LoanApplication.id,
        LoanApplication.applicant_name,
        LoanApplication.loan_amnt,
        LoanApplication.status,
        CreditAssessment.probability_of_default,
        CreditAssessment.credit_risk_score,
        CreditAssessment.risk_tier
    ).outerjoin(CreditAssessment, LoanApplication.id == CreditAssessment.application_id)\
     .order_by(LoanApplication.created_at.desc()).limit(10).all()
     
    recent_list = []
    for app in recent_apps:
        recent_list.append({
            "id": app[0],
            "applicant_name": app[1],
            "loan_amnt": app[2],
            "status": app[3].value if hasattr(app[3], 'value') else str(app[3]),
            "pd": round(app[4] * 100, 1) if app[4] is not None else None,
            "score": app[5],
            "risk_tier": app[6].value if app[6] and hasattr(app[6], 'value') else None
        })
        
    return PortfolioSummaryResponse(
        total_applications=total_apps,
        assessed_applications=assessed_apps,
        pending_applications=pending_apps,
        approved_count=approved_count,
        rejected_count=rejected_count,
        approval_rate=approval_rate,
        average_default_probability=round(avg_pd * 100, 2),
        average_credit_score=round(avg_score, 1),
        total_requested_capital=round(total_capital, 2),
        total_expected_loss=round(total_expected_loss, 2),
        risk_tier_distribution=tier_counts,
        loan_intent_distribution=intent_counts,
        recent_trend=recent_list
    )

