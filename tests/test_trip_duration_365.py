import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_DURATIONS = [1, 3, 7, 14, 15, 30, 60, 90, 180, 365]
INVALID_DURATIONS = [0, 366, -1, 1000]


@pytest.mark.parametrize("days", VALID_DURATIONS)
def test_valid_trip_durations(days):
    """
    Verifies that trip creation accepts durations from 1 to 365 days.
    """
    payload = {
        "destination_name": "Goa",
        "trip_type": "Solo",
        "travel_style": "Budget",
        "number_of_days": days,
        "number_of_travelers": 1
    }
    res = client.post("/trips", json=payload)
    assert res.status_code == 201, f"Expected 201 Created for {days} days, got {res.status_code}"
    data = res.json()
    assert data["number_of_days"] == days
    assert data["total_budget"] > 0


@pytest.mark.parametrize("days", INVALID_DURATIONS)
def test_invalid_trip_durations(days):
    """
    Verifies that trip creation rejects 0 days, 366 days, or negative days with 422.
    """
    payload = {
        "destination_name": "Goa",
        "trip_type": "Solo",
        "travel_style": "Budget",
        "number_of_days": days,
        "number_of_travelers": 1
    }
    res = client.post("/trips", json=payload)
    assert res.status_code == 422, f"Expected 422 Unprocessable Entity for {days} days, got {res.status_code}"


def test_chatbot_interactive_queries():
    """
    Verifies chatbot API handles 'Hello', 'Plan a 3 day trip to Goa', 'Make Day 2 cheaper'.
    """
    for msg in ["Hello", "Plan a 3 day trip to Goa", "Make Day 2 cheaper"]:
        res = client.post("/ai/chat", json={"message": msg})
        assert res.status_code == 200
        data = res.json()
        assert "response" in data
        assert len(data["response"]) > 10
