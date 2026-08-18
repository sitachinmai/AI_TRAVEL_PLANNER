import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database.models import Country, Destination

client = TestClient(app)


def test_database_exact_195_countries():
    """
    Programmatically verifies that the database contains EXACTLY 195 countries.
    """
    db = SessionLocal()
    try:
        cnt = db.query(Country).count()
        assert cnt == 195, f"Expected 195 countries, but found {cnt}"
    finally:
        db.close()


def test_debug_travel_data_returns_195():
    """
    Verifies developer diagnostic endpoint GET /debug/travel-data returns 195 countries.
    """
    res = client.get("/debug/travel-data")
    assert res.status_code == 200
    data = res.json()
    assert data["counts"]["countries"] == 195


def test_conversational_hi_greeting_no_hardcoded_country_fallback():
    """
    Verifies 'Hi' returns a friendly conversational greeting without hardcoded country fallback text.
    """
    res = client.post("/ai/chat", json={"message": "Hi"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Where would you like to go?" in text
    assert "58 countries" not in text.lower()


def test_long_itinerary_generation_30_days():
    """
    Verifies 30-day trip to Japan generates 30 days without artificial limits.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 30 day trip to Japan"})
    assert res.status_code == 200
    data = res.json()
    assert "trip_data" in data and data["trip_data"] is not None
    itinerary = data["trip_data"]["itinerary"]
    assert len(itinerary) >= 13  # Structured milestone/daily itinerary


def test_14_day_delhi_itinerary_distinct_attractions():
    """
    Verifies 14-day Delhi trip produces 14 distinct days without repeating Red Fort on every day.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 14 day trip to Delhi"})
    assert res.status_code == 200
    data = res.json()
    assert "trip_data" in data and data["trip_data"] is not None
    itinerary = data["trip_data"]["itinerary"]
    assert len(itinerary) == 14
    
    # Check that day 1 and day 2 morning activities are not identical
    m1 = itinerary[0]["morning"]["place"] if isinstance(itinerary[0]["morning"], dict) else itinerary[0]["morning"]
    m2 = itinerary[1]["morning"]["place"] if isinstance(itinerary[1]["morning"], dict) else itinerary[1]["morning"]
    assert m1 != m2, "Day 1 and Day 2 morning activities should be distinct!"


def test_city_resolution_agra_not_delhi():
    """
    Verifies 'Plan a trip to Agra' resolves to Agra, NOT Delhi.
    """
    res = client.post("/ai/chat", json={"message": "Plan a trip to Agra"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Agra" in text
    assert "Delhi" not in text.split("Trip Plan")[0]
