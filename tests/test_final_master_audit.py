import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_city_resolution_exact_and_partial():
    """
    Verifies that resolve_destination extracts cities accurately from natural language.
    """
    for prompt, expected_city in [
        ("Plan a 10 day trip to Hyderabad", "Hyderabad"),
        ("Plan 7 days in Japan", "Tokyo"),
        ("Plan a trip to Amalapuram", "Amalapuram"),
        ("Plan a 5 day trip to Paris", "Paris"),
        ("Plan 4 days in Goa", "Goa")
    ]:
        res = client.post("/ai/chat", json={"message": prompt})
        assert res.status_code == 200
        text = res.json()["response"]
        assert expected_city in text, f"Expected {expected_city} in response for '{prompt}', got: {text}"


def test_stateful_day_2_cheaper():
    """
    Verifies stateful day 2 re-planning modifies Day 2 specifically.
    """
    res = client.post("/ai/chat", json={"message": "Make Day 2 cheaper"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Day 2" in text
    assert "Modified" in text or "Switched" in text or "Cost Reduced" in text


def test_explore_country_filtering():
    """
    Verifies that /explore?country=India returns Indian cities.
    """
    res = client.get("/explore?country=India")
    assert res.status_code == 200
    assert "Hyderabad" in res.text or "Delhi" in res.text or "Goa" in res.text


def test_explore_search_query():
    """
    Verifies that /explore?q=Amalapuram returns Amalapuram card.
    """
    res = client.get("/explore?q=Amalapuram")
    assert res.status_code == 200
    assert "Amalapuram" in res.text
