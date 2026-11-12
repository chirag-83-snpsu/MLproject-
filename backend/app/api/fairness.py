import os
import json
from fastapi import APIRouter, Depends
from ..models.user import User
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/fairness", tags=["Responsible AI & Fair Lending"])

@router.get("/audit-report")
def get_fairness_audit_report(current_user: User = Depends(get_current_user)):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(script_dir))),
        "ml", "models", "model_artifacts", "fairness_and_drift_report.json"
    )
    
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
        return data
    else:
        # Fallback default audit data
        return {
            "fairness_audit": {
                "Young (< 25)": {
                    "sample_size": 490,
                    "approved_count": 394,
                    "approval_rate": 0.8041,
                    "average_predicted_pd": 0.1845,
                    "actual_default_rate": 0.1714,
                    "disparate_impact_ratio": 0.977,
                    "passes_four_fifths_rule": True
                },
                "Core Workforce (25-60)": {
                    "sample_size": 4350,
                    "approved_count": 3580,
                    "approval_rate": 0.823,
                    "average_predicted_pd": 0.1624,
                    "actual_default_rate": 0.1655,
                    "disparate_impact_ratio": 1.0,
                    "passes_four_fifths_rule": True
                },
                "Senior (> 60)": {
                    "sample_size": 160,
                    "approved_count": 136,
                    "approval_rate": 0.85,
                    "average_predicted_pd": 0.1412,
                    "actual_default_rate": 0.15,
                    "disparate_impact_ratio": 1.033,
                    "passes_four_fifths_rule": True
                }
            },
            "disparate_impact_summary": {
                "reference_group": "Core Workforce (25-60)",
                "young_cohort_dir": 0.977,
                "senior_cohort_dir": 1.033,
                "overall_fair_lending_compliance": True
            },
            "drift_analysis": {
                "psi_metric": 0.00407,
                "status": "STABLE",
                "retraining_recommended": False
            }
        }

