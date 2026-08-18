import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_debug_travel_data_endpoint():
    """
    Verifies developer diagnostic endpoint GET /debug/travel-data.
    """
    res = client.get("/debug/travel-data")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "counts" in data
    counts = data["counts"]
    assert counts["world_cities"] >= 18
    assert counts["countries"] == 195
    assert counts["destinations"] >= 190
    assert counts["places"] >= 200
    assert counts["stays"] >= 200
    assert counts["food_spots"] >= 200
    assert counts["transports"] >= 200


def test_dynamic_country_and_city_queries():
    """
    Verifies dynamic country and city queries without hardcoded limits.
    """
    res = client.get("/travel/countries")
    assert res.status_code == 200
    countries = res.json()
    assert len(countries) == 195

    res_loc = client.get("/locations/search?q=Hyderabad")
    assert res_loc.status_code == 200
    assert len(res_loc.json()) > 0


def test_no_hardcoded_country_count_in_chatbot():
    """
    Verifies chatbot returns dynamic country lists calculated from SQLite.
    """
    from app.database.database import SessionLocal
    from app.database.models import Country
    db = SessionLocal()
    try:
        cnt = db.query(Country).count()
    finally:
        db.close()

    res = client.post("/ai/chat", json={"message": "What countries do you have?"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert f"{cnt} Countries" in text
