from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["no_external_api_keys_required"] is True


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Travel Planner" in response.text


def test_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200
