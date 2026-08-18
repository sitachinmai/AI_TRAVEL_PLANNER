import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal, init_db
from app.database.models import Destination, Place, Stay, FoodSpot, LocalFood, Transport
from app.database.seed import seed_data

# Ensure tables are initialized and seeded
init_db()
db_init = SessionLocal()
seed_data(db_init)
db_init.close()

client = TestClient(app)


def test_get_destinations_with_region_filter():
    """
    Tests GET /travel/destinations filtering by region.
    """
    res_north = client.get("/travel/destinations?region=North")
    assert res_north.status_code == 200
    data_north = res_north.json()
    assert len(data_north) >= 3
    assert all(d["region"] == "North" for d in data_north)

    res_south = client.get("/travel/destinations?region=South")
    assert res_south.status_code == 200
    data_south = res_south.json()
    assert len(data_south) >= 3
    assert all(d["region"] == "South" for d in data_south)


def test_get_destinations_with_category_filter():
    """
    Tests GET /travel/destinations filtering by category keyword.
    """
    res = client.get("/travel/destinations?category=Monument")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1


def test_destination_detail_endpoint():
    """
    Tests GET /travel/destinations/{id} returns rich nested data.
    """
    res = client.get("/travel/destinations/1")
    assert res.status_code == 200
    dest = res.json()
    assert dest["id"] == 1
    assert "name" in dest
    assert "places" in dest
    assert "stays" in dest
    assert "food_spots" in dest
    assert "local_foods" in dest
    assert "transports" in dest


def test_places_stays_food_transport_endpoints():
    """
    Tests individual travel search endpoints: /travel/places, /travel/stays, /travel/food, /travel/transport.
    """
    res_places = client.get("/travel/places")
    assert res_places.status_code == 200
    assert len(res_places.json()) >= 10

    res_stays = client.get("/travel/stays?category=Premium")
    assert res_stays.status_code == 200
    assert len(res_stays.json()) >= 3

    res_food = client.get("/travel/food?q=Biryani")
    assert res_food.status_code == 200
    food_data = res_food.json()
    assert "food_spots" in food_data
    assert "local_foods" in food_data

    res_transport = client.get("/travel/transport")
    assert res_transport.status_code == 200
    assert len(res_transport.json()) >= 5


def test_global_unified_search_endpoint():
    """
    Tests GET /travel/search returning multi-entity search results.
    """
    res = client.get("/travel/search?q=Delhi")
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "Delhi"
    assert len(data["destinations"]) >= 1
    assert "places" in data
    assert "stays" in data
    assert "food_spots" in data
