from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from ..models.application import ApplicationStatus

class LoanApplicationBase(BaseModel):
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: Optional[str] = None
    
    person_age: int = Field(..., ge=18, le=100)
    person_income: float = Field(..., gt=0)
    person_emp_length: float = Field(..., ge=0)
    person_home_ownership: str  # RENT, MORTGAGE, OWN, OTHER
    
    loan_intent: str  # PERSONAL, EDUCATION, MEDICAL, VENTURE, HOMEIMPROVEMENT, DEBTCONSOLIDATION
    loan_grade: str = "B"
    loan_amnt: float = Field(..., gt=0)
    loan_int_rate: float = Field(..., ge=1.0, le=40.0)
    
    credit_score: int = Field(..., ge=300, le=850)
    debt_to_income_ratio: float = Field(..., ge=0.01, le=1.0)
    revolving_utilization: float = Field(..., ge=0.0, le=100.0)
    delinq_2yrs: int = Field(default=0, ge=0)
    cb_person_default_on_file: str = "N"  # Y / N
    cb_person_cred_hist_length: int = Field(..., ge=0)

class LoanApplicationCreate(LoanApplicationBase):
    pass

class LoanApplicationResponse(LoanApplicationBase):
    id: int
    application_number: str
    loan_percent_income: float
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
    has_assessment: bool = False

    model_config = ConfigDict(from_attributes=True)
