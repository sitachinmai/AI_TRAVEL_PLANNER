import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ai_chat_returns_structured_rich_trip_data():
    """
    Verifies that POST /ai/chat returns structured trip_data containing images and highlights.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 3 day trip to Tokyo"})
    assert res.status_code == 200
    data = res.json()
    assert "trip_data" in data
    td = data["trip_data"]
    assert td is not None
    assert "destination_name" in td
    assert "image" in td
    assert "highlights" in td
    assert isinstance(td["highlights"], list)
    assert len(td["highlights"]) > 0
    assert "image" in td["highlights"][0]

    # Verify morning, afternoon, evening activities have images
    assert "itinerary" in td
    assert len(td["itinerary"]) >= 3
    day1 = td["itinerary"][0]
    assert "morning" in day1 and "image" in day1["morning"]
    assert "afternoon" in day1 and "image" in day1["afternoon"]
    assert "evening" in day1 and "image" in day1["evening"]


def test_destination_detail_page_rich_content():
    """
    Verifies /destination/1 returns images and multi-item stays, places, food, transport.
    """
    res = client.get("/destination/1")
    assert res.status_code == 200
    assert "Places to Visit" in res.text
    assert "Stays" in res.text
    assert "onerror=" in res.text


def test_dashboard_and_chat_pages_load():
    """
    Verifies /dashboard and /chat pages load cleanly.
    """
    for route in ["/dashboard", "/chat", "/explore"]:
        res = client.get(route)
        assert res.status_code == 200
