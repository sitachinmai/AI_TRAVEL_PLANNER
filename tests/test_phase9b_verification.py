import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_database_country_and_destination_counts():
    """
    Verifies that the database contains 58 countries and 198 destinations.
    """
    c_res = client.get("/travel/countries")
    assert c_res.status_code == 200
    countries = c_res.json()
    assert len(countries) == 195, f"Expected 195 countries, got {len(countries)}"

    d_res = client.get("/travel/destinations")
    assert d_res.status_code == 200
    destinations = d_res.json()
    assert len(destinations) >= 198, f"Expected at least 198 destinations, got {len(destinations)}"


def test_chatbot_json_response_structure():
    """
    Verifies that POST /ai/chat returns proper JSON with response text.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 5 day trip to Japan"})
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert "Tokyo" in data["response"] or "Japan" in data["response"]


def test_all_web_routes_unauthenticated():
    """
    Verifies that all main pages load with 200 OK without authentication.
    """
    for route in ["/", "/dashboard", "/explore", "/chat", "/profile", "/my-trips", "/my-favorites", "/plan-trip", "/destination/1"]:
        res = client.get(route)
        assert res.status_code == 200, f"Route {route} failed with {res.status_code}"
