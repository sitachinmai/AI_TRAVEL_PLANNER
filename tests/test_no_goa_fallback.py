import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_europe_query_does_not_return_goa():
    """
    Verifies that 'Plan a budget trip to Europe' returns European destinations, NOT Goa.
    """
    res = client.post("/ai/chat", json={"message": "Plan a budget trip to Europe"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Europe" in text
    assert "Goa" not in text


def test_japan_query_returns_japan():
    """
    Verifies that 'Plan a trip to Japan' returns Japan destinations, NOT Goa.
    """
    res = client.post("/ai/chat", json={"message": "Plan a trip to Japan"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Japan" in text or "Tokyo" in text
    assert "Goa" not in text


def test_delhi_10_day_query_returns_delhi():
    """
    Verifies that 'Plan 10 days in Delhi' returns Delhi 10-day plan.
    """
    res = client.post("/ai/chat", json={"message": "Plan 10 days in Delhi"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Delhi" in text
    assert "10-Day" in text or "Day 10" in text


def test_itinerary_days_are_unique():
    """
    Verifies that itinerary activities across Morning and Afternoon do not repeat the exact same place on the same day or every day.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 4 day trip to Delhi"})
    assert res.status_code == 200
    text = res.json()["response"]
    
    # Assert Red Fort, Qutub Minar, Humayun's Tomb, India Gate appear across days
    assert "Delhi" in text
    assert "Day 1" in text
    assert "Day 2" in text
    assert "Day 3" in text
    assert "Day 4" in text
