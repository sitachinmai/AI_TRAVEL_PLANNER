import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal, init_db
from app.database.seed import seed_data
from app.database.models import Country, Destination

# Ensure DB is initialized
init_db()
db_init = SessionLocal()
seed_data(db_init)
db_init.close()

client = TestClient(app)


def test_get_all_countries():
    """
    Tests GET /travel/countries returns international countries list with flags and destination counts.
    """
    res = client.get("/travel/countries")
    assert res.status_code == 200
    countries = res.json()
    assert len(countries) >= 8

    # Verify India and Japan exist
    country_names = [c["name"] for c in countries]
    assert "India" in country_names
    assert "Japan" in country_names
    assert "France" in country_names


def test_get_country_by_id_and_destinations():
    """
    Tests GET /travel/countries/{id} and GET /travel/countries/{id}/destinations.
    """
    res_countries = client.get("/travel/countries")
    countries = res_countries.json()
    japan = next((c for c in countries if c["name"] == "Japan"), None)
    assert japan is not None

    japan_id = japan["id"]
    res_japan = client.get(f"/travel/countries/{japan_id}")
    assert res_japan.status_code == 200
    japan_data = res_japan.json()
    assert japan_data["name"] == "Japan"
    assert len(japan_data["destinations"]) >= 1

    res_japan_dests = client.get(f"/travel/countries/{japan_id}/destinations")
    assert res_japan_dests.status_code == 200
    assert len(res_japan_dests.json()) >= 1


def test_filter_destinations_by_country():
    """
    Tests filtering destinations by country query parameter.
    """
    res = client.get("/travel/destinations?country=Japan")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(d["country"] == "Japan" for d in data)
