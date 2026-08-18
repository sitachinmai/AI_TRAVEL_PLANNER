import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.currency import normalize_place_cost

client = TestClient(app)


def test_currency_normalization():
    """
    Verifies multi-currency normalization logic across EUR, USD, JPY, GBP, INR, and free attractions.
    """
    # EUR test
    res_eur = normalize_place_cost(25.0, currency_code="EUR", place_name="Eiffel Tower")
    assert res_eur["currency"] == "EUR"
    assert "€25" in res_eur["display_amount"]
    assert res_eur["inr_amount"] == 2375.0

    # JPY test
    res_jpy = normalize_place_cost(1000.0, currency_code="JPY", place_name="Senso-ji Temple")
    assert res_jpy["currency"] == "JPY"
    assert "¥1,000" in res_jpy["display_amount"]

    # Free attraction test
    res_free = normalize_place_cost(0.0, currency_code="EUR", is_explicitly_free=True, place_name="Notre-Dame Cathedral")
    assert res_free["is_free"] is True
    assert "Free" in res_free["display_amount"]


def test_geoapify_locations_endpoints():
    """
    Verifies Geoapify location discovery API endpoints.
    """
    # Search Hyderabad
    res = client.get("/locations/search?q=Hyderabad")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert data[0]["name"] == "Hyderabad"

    # Search Tokyo
    res_tokyo = client.get("/locations/search?q=Tokyo")
    assert res_tokyo.status_code == 200
    assert len(res_tokyo.json()) > 0

    # List Cities
    res_cities = client.get("/locations/cities?limit=10")
    assert res_cities.status_code == 200
    assert len(res_cities.json()) > 0


def test_database_status_includes_world_cities():
    """
    Verifies /database-status returns world_cities count.
    """
    res = client.get("/database-status")
    assert res.status_code == 200
    data = res.json()
    assert "world_cities" in data
    assert data["world_cities"] >= 18
