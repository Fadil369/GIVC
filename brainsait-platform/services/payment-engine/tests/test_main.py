import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "paymentlinc"
    assert data["oid"] == "1.3.6.1.4.1.61026.5.1"

def test_validate_card():
    validation = {
        "card_number": "4111111111111111",  # Test Visa card
        "exp_month": 12,
        "exp_year": 25,
        "cvv": "123"
    }
    response = client.post("/api/v1/payments/validate", json=validation)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert data["card_type"] == "visa"

def test_create_payment():
    payment_intent = {
        "amount": 100.00,
        "currency": "SAR",
        "gateway": "stripe",
        "description": "Test payment"
    }
    response = client.post("/api/v1/payments/charge", json=payment_intent)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_list_payments():
    response = client.get("/api/v1/payments")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "payments" in data

def test_payment_stats():
    response = client.get("/api/v1/payments/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_payments" in data
    assert "by_gateway" in data
