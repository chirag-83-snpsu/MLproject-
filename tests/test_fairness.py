import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_auth_token(role="compliance"):
    if role == "compliance":
        email = "elena.compliance@credx.ai"
        pwd = "Compliance@123"
    else:
        email = "sarah.officer@credx.ai"
        pwd = "Officer@123"
        
    res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    return res.json()["access_token"]

def test_fairness_audit_endpoint():
    token = get_auth_token("compliance")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/fairness/audit-report", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "fairness_audit" in data
    assert "Young (< 25)" in data["fairness_audit"]
    assert "Core Workforce (25-60)" in data["fairness_audit"]
    assert "Senior (> 60)" in data["fairness_audit"]
    
    # Verify DIR and 4/5ths rule
    assert "disparate_impact_summary" in data
    assert data["disparate_impact_summary"]["overall_fair_lending_compliance"] is True
    
    # Verify drift analysis
    assert "drift_analysis" in data
    assert "psi_metric" in data["drift_analysis"]
    assert data["drift_analysis"]["status"] == "STABLE"

def test_underwriter_decision_override():
    token = get_auth_token("officer")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Record underwriter decision on application 3
    payload = {
        "final_decision": "APPROVED",
        "is_override": True,
        "override_reason": "Approved with senior loan committee authorization based on verified cash deposit.",
        "notes": "Co-signer liquid assets confirmed via verified bureau bank connect."
    }
    
    response = client.post("/api/v1/underwriting/3/decide", json=payload, headers=headers)
    assert response.status_code == 200
    dec = response.json()
    assert dec["final_decision"] == "APPROVED"
    assert dec["is_override"] is True

