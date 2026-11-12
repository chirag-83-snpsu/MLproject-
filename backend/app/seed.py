"""
CredX AI Database Seeder
Populates initial RBAC users and realistic demonstration loan applications.
"""

from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta

from .database import engine, Base, SessionLocal
from .models.user import User, UserRole
from .models.application import LoanApplication, ApplicationStatus
from .models.assessment import CreditAssessment, RiskTier, SystemRecommendation
from .models.underwriter import UnderwriterDecision, UnderwriterFinalDecision
from .models.audit import AuditLog
from .core.security import get_password_hash
from ml.xai.shap_explainer import CreditRiskExplainer
from ml.xai.counterfactual import CounterfactualEngine

def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    # Check if admin already exists
    if db.query(User).filter(User.email == "admin@credx.ai").first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("Seeding standard RBAC users...")
    users = [
        User(
            email="admin@credx.ai",
            hashed_password=get_password_hash("Admin@123"),
            full_name="Alexandra Chen (Platform Admin)",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            email="sarah.officer@credx.ai",
            hashed_password=get_password_hash("Officer@123"),
            full_name="Sarah Jenkins (Senior Underwriter)",
            role=UserRole.LOAN_OFFICER,
            is_active=True
        ),
        User(
            email="david.analyst@credx.ai",
            hashed_password=get_password_hash("Analyst@123"),
            full_name="David Vance (Quantitative Risk Lead)",
            role=UserRole.RISK_ANALYST,
            is_active=True
        ),
        User(
            email="elena.compliance@credx.ai",
            hashed_password=get_password_hash("Compliance@123"),
            full_name="Elena Rostova (Chief Compliance Officer)",
            role=UserRole.COMPLIANCE_OFFICER,
            is_active=True
        )
    ]
    for u in users:
        db.add(u)
    db.commit()

    officer_user = db.query(User).filter(User.email == "sarah.officer@credx.ai").first()

    print("Seeding demonstration loan applications across risk spectrum...")
    demo_apps = [
        {
            "num": "CRX-2026-A101",
            "name": "Marcus Sterling",
            "email": "m.sterling@enterprise.io",
            "phone": "+1-555-019-8812",
            "age": 42,
            "income": 145000.0,
            "emp_length": 8.5,
            "home": "MORTGAGE",
            "intent": "HOMEIMPROVEMENT",
            "grade": "A",
            "amnt": 25000.0,
            "rate": 6.8,
            "credit_score": 795,
            "dti": 0.18,
            "util": 14.5,
            "delinq": 0,
            "def_on_file": "N",
            "hist_len": 18
        },
        {
            "num": "CRX-2026-A102",
            "name": "Sophia Rodriguez",
            "email": "sophia.r@techcorp.com",
            "phone": "+1-555-019-3321",
            "age": 28,
            "income": 92000.0,
            "emp_length": 4.0,
            "home": "RENT",
            "intent": "VENTURE",
            "grade": "B",
            "amnt": 15000.0,
            "rate": 9.5,
            "credit_score": 725,
            "dti": 0.24,
            "util": 28.0,
            "delinq": 0,
            "def_on_file": "N",
            "hist_len": 8
        },
        {
            "num": "CRX-2026-A103",
            "name": "Evelyn Reed",
            "email": "evelyn.reed@biocare.org",
            "phone": "+1-555-019-4490",
            "age": 35,
            "income": 58000.0,
            "emp_length": 3.0,
            "home": "RENT",
            "intent": "DEBTCONSOLIDATION",
            "grade": "C",
            "amnt": 18000.0,
            "rate": 13.8,
            "credit_score": 648,
            "dti": 0.39,
            "util": 68.2,
            "delinq": 1,
            "def_on_file": "N",
            "hist_len": 9
        },
        {
            "num": "CRX-2026-A104",
            "name": "Brandon Taylor",
            "email": "btaylor88@gmail.com",
            "phone": "+1-555-019-7711",
            "age": 24,
            "income": 36000.0,
            "emp_length": 1.5,
            "home": "RENT",
            "intent": "PERSONAL",
            "grade": "E",
            "amnt": 12000.0,
            "rate": 19.5,
            "credit_score": 575,
            "dti": 0.52,
            "util": 84.0,
            "delinq": 2,
            "def_on_file": "N",
            "hist_len": 3
        },
        {
            "num": "CRX-2026-A105",
            "name": "Raymond Vance",
            "email": "rvance@logistics-sys.net",
            "phone": "+1-555-019-9943",
            "age": 51,
            "income": 72000.0,
            "emp_length": 6.0,
            "home": "OWN",
            "intent": "MEDICAL",
            "grade": "D",
            "amnt": 22000.0,
            "rate": 16.2,
            "credit_score": 615,
            "dti": 0.44,
            "util": 72.5,
            "delinq": 1,
            "def_on_file": "Y",
            "hist_len": 16
        },
        {
            "num": "CRX-2026-A106",
            "name": "Clara Zhao",
            "email": "clara.zhao@finconsult.com",
            "phone": "+1-555-019-1123",
            "age": 31,
            "income": 115000.0,
            "emp_length": 6.0,
            "home": "MORTGAGE",
            "intent": "EDUCATION",
            "grade": "A",
            "amnt": 20000.0,
            "rate": 7.2,
            "credit_score": 780,
            "dti": 0.20,
            "util": 19.5,
            "delinq": 0,
            "def_on_file": "N",
            "hist_len": 11
        },
        {
            "num": "CRX-2026-A107",
            "name": "Derrick Owens",
            "email": "dowens@freightcorp.com",
            "phone": "+1-555-019-5567",
            "age": 46,
            "income": 64000.0,
            "emp_length": 5.0,
            "home": "RENT",
            "intent": "DEBTCONSOLIDATION",
            "grade": "C",
            "amnt": 16000.0,
            "rate": 14.1,
            "credit_score": 660,
            "dti": 0.35,
            "util": 55.0,
            "delinq": 0,
            "def_on_file": "N",
            "hist_len": 14
        },
        {
            "num": "CRX-2026-A108",
            "name": "Liam Gallagher",
            "email": "liam.g@sounddesign.com",
            "phone": "+1-555-019-6632",
            "age": 22,
            "income": 31000.0,
            "emp_length": 1.0,
            "home": "RENT",
            "intent": "PERSONAL",
            "grade": "F",
            "amnt": 10000.0,
            "rate": 22.5,
            "credit_score": 520,
            "dti": 0.58,
            "util": 92.0,
            "delinq": 3,
            "def_on_file": "Y",
            "hist_len": 2
        }
    ]

    explainer = CreditRiskExplainer()
    cf_engine = CounterfactualEngine(explainer=explainer)

    for item in demo_apps:
        loan_pct = round(item['amnt'] / item['income'], 3)
        app = LoanApplication(
            application_number=item['num'],
            applicant_name=item['name'],
            applicant_email=item['email'],
            applicant_phone=item['phone'],
            person_age=item['age'],
            person_income=item['income'],
            person_emp_length=item['emp_length'],
            person_home_ownership=item['home'],
            loan_intent=item['intent'],
            loan_grade=item['grade'],
            loan_amnt=item['amnt'],
            loan_int_rate=item['rate'],
            loan_percent_income=loan_pct,
            credit_score=item['credit_score'],
            debt_to_income_ratio=item['dti'],
            revolving_utilization=item['util'],
            delinq_2yrs=item['delinq'],
            cb_person_default_on_file=item['def_on_file'],
            cb_person_cred_hist_length=item['hist_len'],
            status=ApplicationStatus.ASSESSED,
            created_by_user_id=officer_user.id
        )
        db.add(app)
        db.commit()
        db.refresh(app)

        # Run automated assessment
        eval_data = {
            'person_age': item['age'],
            'person_income': item['income'],
            'person_emp_length': item['emp_length'],
            'person_home_ownership': item['home'],
            'loan_intent': item['intent'],
            'loan_grade': item['grade'],
            'loan_amnt': item['amnt'],
            'loan_int_rate': item['rate'],
            'loan_percent_income': loan_pct,
            'credit_score': item['credit_score'],
            'debt_to_income_ratio': item['dti'],
            'revolving_utilization': item['util'],
            'delinq_2yrs': item['delinq'],
            'cb_person_default_on_file': item['def_on_file'],
            'cb_person_cred_hist_length': item['hist_len']
        }
        xai_res = explainer.predict_and_explain(eval_data)
        cf_res = cf_engine.generate_counterfactuals(eval_data)

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
        
        # Add decisions for first two to populate approval/override states
        if item['num'] == "CRX-2026-A101":
            app.status = ApplicationStatus.APPROVED
            dec = UnderwriterDecision(
                application_id=app.id,
                decided_by_user_id=officer_user.id,
                final_decision=UnderwriterFinalDecision.APPROVED,
                is_override=False,
                notes="Prime application automatically cleared under low-risk straight-through parameters."
            )
            db.add(dec)
        elif item['num'] == "CRX-2026-A104":
            app.status = ApplicationStatus.REJECTED
            dec = UnderwriterDecision(
                application_id=app.id,
                decided_by_user_id=officer_user.id,
                final_decision=UnderwriterFinalDecision.REJECTED,
                is_override=False,
                notes="Credit risk exceeds threshold. Formal Adverse Action notice dispatched."
            )
            db.add(dec)
            
        db.commit()

    print("Initial demonstration records seeded successfully!")
    db.close()

if __name__ == '__main__':
    seed_database()

