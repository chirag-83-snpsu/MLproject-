from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import json
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.application import LoanApplication, ApplicationStatus
from ..models.assessment import CreditAssessment, RiskTier, SystemRecommendation
from ..schemas.assessment import AssessmentResponse, WhatIfSimulationRequest, WhatIfSimulationResponse
from ..core.dependencies import get_current_user, log_audit_event
from ml.xai.shap_explainer import CreditRiskExplainer
from ml.xai.counterfactual import CounterfactualEngine

router = APIRouter(prefix="/assessment", tags=["Credit Risk Assessment & XAI"])

# Lazy singleton explainer & counterfactual engine
_explainer = None
_cf_engine = None

def get_xai_engines():
    global _explainer, _cf_engine
    if _explainer is None:
        _explainer = CreditRiskExplainer()
        _cf_engine = CounterfactualEngine(explainer=_explainer)
    return _explainer, _cf_engine

@router.post("/{application_id}/assess", response_model=AssessmentResponse)
def assess_application(
    application_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
        
    explainer, cf_engine = get_xai_engines()
    
    applicant_data = {
        'person_age': app.person_age,
        'person_income': app.person_income,
        'person_emp_length': app.person_emp_length,
        'person_home_ownership': app.person_home_ownership,
        'loan_intent': app.loan_intent,
        'loan_grade': app.loan_grade,
        'loan_amnt': app.loan_amnt,
        'loan_int_rate': app.loan_int_rate,
        'loan_percent_income': app.loan_percent_income,
        'credit_score': app.credit_score,
        'debt_to_income_ratio': app.debt_to_income_ratio,
        'revolving_utilization': app.revolving_utilization,
        'delinq_2yrs': app.delinq_2yrs,
        'cb_person_default_on_file': app.cb_person_default_on_file,
        'cb_person_cred_hist_length': app.cb_person_cred_hist_length
    }
    
    # 1. Run ML & SHAP inference
    xai_res = explainer.predict_and_explain(applicant_data)
    
    # 2. Run Counterfactual Analysis
    cf_res = cf_engine.generate_counterfactuals(applicant_data)
    
    # 3. Check if existing assessment exists, update or create
    existing_assessment = db.query(CreditAssessment).filter(CreditAssessment.application_id == application_id).first()
    
    if existing_assessment:
        existing_assessment.model_version = "1.0.0"
        existing_assessment.probability_of_default = xai_res['probability_of_default']
        existing_assessment.credit_risk_score = xai_res['credit_risk_score']
        existing_assessment.risk_tier = RiskTier(xai_res['risk_tier'])
        existing_assessment.system_recommendation = SystemRecommendation(xai_res['system_recommendation'])
        existing_assessment.expected_loss = xai_res['expected_loss_usd']
        existing_assessment.shap_values_json = json.dumps(xai_res['feature_attributions'])
        existing_assessment.top_risk_drivers_json = json.dumps(xai_res['top_risk_drivers'])
        existing_assessment.top_protective_factors_json = json.dumps(xai_res['top_protective_factors'])
        existing_assessment.adverse_action_reasons_json = json.dumps(xai_res['adverse_action_reasons'])
        existing_assessment.counterfactual_json = json.dumps(cf_res['scenarios'])
        existing_assessment.assessed_at = datetime.utcnow()
        assessment = existing_assessment
    else:
        assessment = CreditAssessment(
            application_id=app.id,
            model_version="1.0.0",
            probability_of_default=xai_res['probability_of_default'],
            credit_risk_score=xai_res['credit_risk_score'],
            risk_tier=RiskTier(xai_res['risk_tier']),
            system_recommendation=SystemRecommendation(xai_res['system_recommendation']),
            expected_loss=xai_res['expected_loss_usd'],
            shap_values_json=json.dumps(xai_res['feature_attributions']),
            top_risk_drivers_json=json.dumps(xai_res['top_risk_drivers']),
            top_protective_factors_json=json.dumps(xai_res['top_protective_factors']),
            adverse_action_reasons_json=json.dumps(xai_res['adverse_action_reasons']),
            counterfactual_json=json.dumps(cf_res['scenarios'])
        )
        db.add(assessment)
        
    app.status = ApplicationStatus.ASSESSED
    db.commit()
    db.refresh(assessment)
    
    log_audit_event(
        db,
        action="CREDIT_RISK_ASSESSMENT_EXECUTED",
        entity_type="CreditAssessment",
        entity_id=str(assessment.id),
        user=current_user,
        details={
            "application_id": app.id,
            "application_number": app.application_number,
            "pd": assessment.probability_of_default,
            "score": assessment.credit_risk_score,
            "tier": assessment.risk_tier.value
        },
        request=request
    )
    
    return AssessmentResponse(
        id=assessment.id,
        application_id=assessment.application_id,
        model_version=assessment.model_version,
        probability_of_default=assessment.probability_of_default,
        credit_risk_score=assessment.credit_risk_score,
        risk_tier=assessment.risk_tier,
        system_recommendation=assessment.system_recommendation,
        expected_loss=assessment.expected_loss,
        feature_attributions=json.loads(assessment.shap_values_json),
        top_risk_drivers=json.loads(assessment.top_risk_drivers_json),
        top_protective_factors=json.loads(assessment.top_protective_factors_json),
        narrative_summary=xai_res['narrative_summary'],
        adverse_action_reasons=json.loads(assessment.adverse_action_reasons_json or "[]"),
        counterfactual_scenarios=json.loads(assessment.counterfactual_json or "[]"),
        assessed_at=assessment.assessed_at
    )

@router.get("/{application_id}", response_model=AssessmentResponse)
def get_assessment(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assessment = db.query(CreditAssessment).filter(CreditAssessment.application_id == application_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found for this application")
        
    explainer, _ = get_xai_engines()
    app = assessment.application
    
    applicant_data = {
        'person_age': app.person_age,
        'person_income': app.person_income,
        'person_emp_length': app.person_emp_length,
        'person_home_ownership': app.person_home_ownership,
        'loan_intent': app.loan_intent,
        'loan_grade': app.loan_grade,
        'loan_amnt': app.loan_amnt,
        'loan_int_rate': app.loan_int_rate,
        'loan_percent_income': app.loan_percent_income,
        'credit_score': app.credit_score,
        'debt_to_income_ratio': app.debt_to_income_ratio,
        'revolving_utilization': app.revolving_utilization,
        'delinq_2yrs': app.delinq_2yrs,
        'cb_person_default_on_file': app.cb_person_default_on_file,
        'cb_person_cred_hist_length': app.cb_person_cred_hist_length
    }
    
    top_risk = json.loads(assessment.top_risk_drivers_json)
    top_prot = json.loads(assessment.top_protective_factors_json)
    narratives = explainer._generate_narrative(applicant_data, top_risk, top_prot)
    
    return AssessmentResponse(
        id=assessment.id,
        application_id=assessment.application_id,
        model_version=assessment.model_version,
        probability_of_default=assessment.probability_of_default,
        credit_risk_score=assessment.credit_risk_score,
        risk_tier=assessment.risk_tier,
        system_recommendation=assessment.system_recommendation,
        expected_loss=assessment.expected_loss,
        feature_attributions=json.loads(assessment.shap_values_json),
        top_risk_drivers=top_risk,
        top_protective_factors=top_prot,
        narrative_summary=narratives,
        adverse_action_reasons=json.loads(assessment.adverse_action_reasons_json or "[]"),
        counterfactual_scenarios=json.loads(assessment.counterfactual_json or "[]"),
        assessed_at=assessment.assessed_at
    )

@router.post("/simulate-what-if", response_model=WhatIfSimulationResponse)
def simulate_what_if(
    sim_req: WhatIfSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    explainer, _ = get_xai_engines()
    
    # Load base applicant profile
    if sim_req.application_id:
        app = db.query(LoanApplication).filter(LoanApplication.id == sim_req.application_id).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        base_data = {
            'person_age': app.person_age,
            'person_income': app.person_income,
            'person_emp_length': app.person_emp_length,
            'person_home_ownership': app.person_home_ownership,
            'loan_intent': app.loan_intent,
            'loan_grade': app.loan_grade,
            'loan_amnt': app.loan_amnt,
            'loan_int_rate': app.loan_int_rate,
            'loan_percent_income': app.loan_percent_income,
            'credit_score': app.credit_score,
            'debt_to_income_ratio': app.debt_to_income_ratio,
            'revolving_utilization': app.revolving_utilization,
            'delinq_2yrs': app.delinq_2yrs,
            'cb_person_default_on_file': app.cb_person_default_on_file,
            'cb_person_cred_hist_length': app.cb_person_cred_hist_length
        }
    else:
        # Default sample profile
        base_data = {
            'person_age': 30,
            'person_income': 60000.0,
            'person_emp_length': 4.0,
            'person_home_ownership': 'RENT',
            'loan_intent': 'PERSONAL',
            'loan_grade': 'C',
            'loan_amnt': 15000.0,
            'loan_int_rate': 12.5,
            'loan_percent_income': 0.25,
            'credit_score': 650,
            'debt_to_income_ratio': 0.38,
            'revolving_utilization': 60.0,
            'delinq_2yrs': 0,
            'cb_person_default_on_file': 'N',
            'cb_person_cred_hist_length': 8
        }
        
    baseline_eval = explainer.predict_and_explain(base_data)
    
    # Apply modifications
    modified_data = dict(base_data)
    if sim_req.person_income is not None:
        modified_data['person_income'] = sim_req.person_income
    if sim_req.loan_amnt is not None:
        modified_data['loan_amnt'] = sim_req.loan_amnt
    if sim_req.revolving_utilization is not None:
        modified_data['revolving_utilization'] = sim_req.revolving_utilization
    if sim_req.debt_to_income_ratio is not None:
        modified_data['debt_to_income_ratio'] = sim_req.debt_to_income_ratio
    if sim_req.credit_score is not None:
        modified_data['credit_score'] = sim_req.credit_score
    if sim_req.delinq_2yrs is not None:
        modified_data['delinq_2yrs'] = sim_req.delinq_2yrs
        
    modified_data['loan_percent_income'] = round(modified_data['loan_amnt'] / modified_data['person_income'], 3)
    
    sim_eval = explainer.predict_and_explain(modified_data)
    
    pd_delta = round((baseline_eval['probability_of_default'] - sim_eval['probability_of_default']) * 100, 2)
    score_delta = sim_eval['credit_risk_score'] - baseline_eval['credit_risk_score']
    
    return WhatIfSimulationResponse(
        baseline_pd=baseline_eval['probability_of_default'],
        baseline_score=baseline_eval['credit_risk_score'],
        baseline_tier=baseline_eval['risk_tier'],
        simulated_pd=sim_eval['probability_of_default'],
        simulated_score=sim_eval['credit_risk_score'],
        simulated_tier=sim_eval['risk_tier'],
        simulated_recommendation=sim_eval['system_recommendation'],
        pd_delta=pd_delta,
        score_delta=score_delta,
        top_risk_drivers=sim_eval['top_risk_drivers']
    )

