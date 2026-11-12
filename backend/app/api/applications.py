from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from ..database import get_db
from ..models.user import User, UserRole
from ..models.application import LoanApplication, ApplicationStatus
from ..schemas.application import LoanApplicationCreate, LoanApplicationResponse
from ..core.dependencies import get_current_user, log_audit_event

router = APIRouter(prefix="/applications", tags=["Loan Applications"])

def generate_app_number() -> str:
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"CRX-2026-{short_uuid}"

@router.post("/", response_model=LoanApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_in: LoanApplicationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    loan_pct_income = round(app_in.loan_amnt / app_in.person_income, 4)
    app_num = generate_app_number()
    
    application = LoanApplication(
        application_number=app_num,
        applicant_name=app_in.applicant_name,
        applicant_email=app_in.applicant_email,
        applicant_phone=app_in.applicant_phone,
        person_age=app_in.person_age,
        person_income=app_in.person_income,
        person_emp_length=app_in.person_emp_length,
        person_home_ownership=app_in.person_home_ownership.upper(),
        loan_intent=app_in.loan_intent.upper(),
        loan_grade=app_in.loan_grade.upper(),
        loan_amnt=app_in.loan_amnt,
        loan_int_rate=app_in.loan_int_rate,
        loan_percent_income=loan_pct_income,
        credit_score=app_in.credit_score,
        debt_to_income_ratio=app_in.debt_to_income_ratio,
        revolving_utilization=app_in.revolving_utilization,
        delinq_2yrs=app_in.delinq_2yrs,
        cb_person_default_on_file=app_in.cb_person_default_on_file.upper(),
        cb_person_cred_hist_length=app_in.cb_person_cred_hist_length,
        status=ApplicationStatus.SUBMITTED,
        created_by_user_id=current_user.id
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    log_audit_event(
        db,
        action="APPLICATION_CREATED",
        entity_type="LoanApplication",
        entity_id=str(application.id),
        user=current_user,
        details={
            "application_number": application.application_number,
            "applicant_name": application.applicant_name,
            "loan_amnt": application.loan_amnt
        },
        request=request
    )
    
    res = LoanApplicationResponse.model_validate(application)
    res.has_assessment = False
    return res

@router.get("/", response_model=List[LoanApplicationResponse])
def list_applications(
    status_filter: Optional[ApplicationStatus] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(LoanApplication)
    if status_filter:
        query = query.filter(LoanApplication.status == status_filter)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (LoanApplication.applicant_name.ilike(search_pattern)) |
            (LoanApplication.application_number.ilike(search_pattern)) |
            (LoanApplication.applicant_email.ilike(search_pattern))
        )
        
    apps = query.order_by(LoanApplication.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for a in apps:
        r = LoanApplicationResponse.model_validate(a)
        r.has_assessment = a.assessment is not None
        results.append(r)
    return results

@router.get("/{application_id}", response_model=LoanApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    r = LoanApplicationResponse.model_validate(app)
    r.has_assessment = app.assessment is not None
    return r
