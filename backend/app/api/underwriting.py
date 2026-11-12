from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models.user import User, UserRole
from ..models.application import LoanApplication, ApplicationStatus
from ..models.underwriter import UnderwriterDecision, UnderwriterFinalDecision
from ..schemas.underwriter import UnderwriterDecisionCreate, UnderwriterDecisionResponse
from ..core.dependencies import get_current_user, require_role, log_audit_event

router = APIRouter(prefix="/underwriting", tags=["Human-in-the-Loop Decisioning"])

@router.post("/{application_id}/decide", response_model=UnderwriterDecisionResponse)
def submit_underwriter_decision(
    application_id: int,
    decision_in: UnderwriterDecisionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.LOAN_OFFICER, UserRole.RISK_ANALYST, UserRole.ADMIN))
):
    app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Loan application not found")
        
    if not app.assessment:
        raise HTTPException(
            status_code=400,
            detail="Application must be assessed by credit risk model before underwriter decision can be recorded."
        )
        
    rec = app.assessment.system_recommendation.value
    final_dec = decision_in.final_decision.value
    
    # Auto-detect if this is an override
    is_override = decision_in.is_override
    if (rec == "REJECT" and final_dec == "APPROVED") or (rec == "APPROVE" and final_dec == "REJECTED"):
        is_override = True
        if not decision_in.override_reason or len(decision_in.override_reason.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="A detailed override reason (min 10 characters) is legally required when departing from system recommendation."
            )

    # Check if prior decision exists, update or create
    existing_dec = db.query(UnderwriterDecision).filter(UnderwriterDecision.application_id == application_id).first()
    if existing_dec:
        existing_dec.decided_by_user_id = current_user.id
        existing_dec.final_decision = decision_in.final_decision
        existing_dec.is_override = is_override
        existing_dec.override_reason = decision_in.override_reason
        existing_dec.notes = decision_in.notes
        existing_dec.decided_at = datetime.utcnow()
        decision = existing_dec
    else:
        decision = UnderwriterDecision(
            application_id=app.id,
            decided_by_user_id=current_user.id,
            final_decision=decision_in.final_decision,
            is_override=is_override,
            override_reason=decision_in.override_reason,
            notes=decision_in.notes
        )
        db.add(decision)
        
    # Update application status
    if decision_in.final_decision == UnderwriterFinalDecision.APPROVED:
        app.status = ApplicationStatus.APPROVED
    elif decision_in.final_decision == UnderwriterFinalDecision.REJECTED:
        app.status = ApplicationStatus.REJECTED
    elif decision_in.final_decision == UnderwriterFinalDecision.ESCALATED:
        app.status = ApplicationStatus.ESCALATED
        
    db.commit()
    db.refresh(decision)
    
    log_audit_event(
        db,
        action="UNDERWRITER_DECISION_RECORDED",
        entity_type="UnderwriterDecision",
        entity_id=str(decision.id),
        user=current_user,
        details={
            "application_id": app.id,
            "final_decision": decision.final_decision.value,
            "is_override": is_override,
            "override_reason": decision.override_reason
        },
        request=request
    )
    
    res = UnderwriterDecisionResponse.model_validate(decision)
    res.decided_by_name = current_user.full_name
    return res

@router.get("/{application_id}", response_model=UnderwriterDecisionResponse)
def get_underwriter_decision(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(UnderwriterDecision).filter(UnderwriterDecision.application_id == application_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="No underwriter decision recorded yet")
    res = UnderwriterDecisionResponse.model_validate(decision)
    res.decided_by_name = decision.decided_by.full_name if decision.decided_by else None
    return res
