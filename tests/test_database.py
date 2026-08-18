import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db, DB_PATH, init_db, SessionLocal
from app.database.models import Destination, Place, Stay, FoodSpot, LocalFood, Transport
from app.database.seed import seed_data

# Ensure tables are initialized before running tests
init_db()
db_init = SessionLocal()
seed_data(db_init)
db_init.close()

client = TestClient(app)


def test_sqlite_database_file_exists():
    """
    Verifies that the SQLite database file data/travel_planner.db exists.
    """
    assert os.path.exists(DB_PATH)


def test_database_status_endpoint():
    """
    Verifies GET /database-status returns correct status and table counts.
    """
    response = client.get("/database-status")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"
    assert data["destinations"] >= 10
    assert data["places"] >= 10
    assert data["stays"] >= 10
    assert data["food_spots"] >= 5
    assert data["local_foods"] >= 10
    assert data["transports"] >= 5


def test_destination_models_and_relationships():
    """
    Tests database models and cascading relationship mappings using an in-memory SQLite DB.
    """
    TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        seed_data(db)

        # Query Delhi
        delhi = db.query(Destination).filter(Destination.name == "Delhi").first()
        assert delhi is not None
        assert delhi.state == "Delhi"
        assert len(delhi.places) >= 2

        # Query Jaipur
        jaipur = db.query(Destination).filter(Destination.name == "Jaipur").first()
        assert jaipur is not None
        assert jaipur.state == "Rajasthan"

        # Query Mumbai
        mumbai = db.query(Destination).filter(Destination.name == "Mumbai").first()
        assert mumbai is not None
        assert mumbai.state == "Maharashtra"

    finally:
        db.close()


def test_existing_phase1_endpoints():
    """
    Ensures Phase 1 endpoints continue working cleanly.
    """
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "AI Travel Planner" in res_root.text

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
