import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_auth_token():
    res = client.post("/api/v1/auth/login", json={
        "email": "sarah.officer@credx.ai",
        "password": "Officer@123"
    })
    return res.json()["access_token"]

def test_assessment_execution_and_shap():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Assess application 1
    response = client.post("/api/v1/assessment/1/assess", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "probability_of_default" in data
    assert 0.0 <= data["probability_of_default"] <= 1.0
    assert "credit_risk_score" in data
    assert 300 <= data["credit_risk_score"] <= 850
    assert data["risk_tier"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert data["system_recommendation"] in ["APPROVE", "MANUAL_REVIEW", "REJECT"]
    
    # Verify SHAP explanations
    assert "feature_attributions" in data
    assert len(data["feature_attributions"]) > 0
    assert "top_risk_drivers" in data
    assert "top_protective_factors" in data
    assert "narrative_summary" in data
    assert len(data["narrative_summary"]) > 0
    assert "counterfactual_scenarios" in data

def test_what_if_simulation():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    sim_payload = {
        "application_id": 1,
        "revolving_utilization": 15.0,
        "debt_to_income_ratio": 0.15
    }
    
    response = client.post("/api/v1/assessment/simulate-what-if", json=sim_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "baseline_pd" in data
    assert "simulated_pd" in data
    assert "score_delta" in data

