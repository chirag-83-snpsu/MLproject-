import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"

def test_login_success():
    response = client.post("/api/v1/auth/login", json={
        "email": "sarah.officer@credx.ai",
        "password": "Officer@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "loan_officer"

def test_login_invalid_password():
    response = client.post("/api/v1/auth/login", json={
        "email": "sarah.officer@credx.ai",
        "password": "WrongPassword999"
    })
    assert response.status_code == 401

