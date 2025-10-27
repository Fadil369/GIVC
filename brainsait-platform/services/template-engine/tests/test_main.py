import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "templatelinc"
    assert data["oid"] == "1.3.6.1.4.1.61026.6.1"

def test_list_templates():
    response = client.get("/api/v1/templates")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "templates" in data

def test_create_template():
    template = {
        "title": "Test Template",
        "content": "This is a test template",
        "category": "test",
        "tags": ["test", "sample"]
    }
    response = client.post("/api/v1/templates", json=template)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"

def test_search_templates():
    query = {
        "query": "test",
        "limit": 10
    }
    response = client.post("/api/v1/templates/search", json=query)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
