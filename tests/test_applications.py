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

def test_list_applications():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/applications/", headers=headers)
    assert response.status_code == 200
    apps = response.json()
    assert isinstance(apps, list)
    assert len(apps) >= 8

def test_create_and_fetch_application():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "applicant_name": "Jessica Albright",
        "applicant_email": "jessica.a@sampledomain.com",
        "applicant_phone": "+1-555-019-9988",
        "person_age": 34,
        "person_income": 82000.0,
        "person_emp_length": 5.0,
        "person_home_ownership": "OWN",
        "loan_intent": "HOMEIMPROVEMENT",
        "loan_grade": "B",
        "loan_amnt": 14000.0,
        "loan_int_rate": 8.9,
        "credit_score": 735,
        "debt_to_income_ratio": 0.22,
        "revolving_utilization": 24.5,
        "delinq_2yrs": 0,
        "cb_person_default_on_file": "N",
        "cb_person_cred_hist_length": 10
    }
    
    create_res = client.post("/api/v1/applications/", json=payload, headers=headers)
    assert create_res.status_code == 201
    created_app = create_res.json()
    assert created_app["applicant_name"] == "Jessica Albright"
    assert created_app["application_number"].startswith("CRX-2026-")
    
    # Fetch by ID
    get_res = client.get(f"/api/v1/applications/{created_app['id']}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == created_app["id"]

