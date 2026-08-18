import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database.models import User
from app.core.dependencies import DEV_AUTH_BYPASS, DEV_USER_EMAIL

client = TestClient(app)


def test_dev_auth_bypass_enabled():
    """
    Verifies that DEV_AUTH_BYPASS is active during development phase.
    """
    assert DEV_AUTH_BYPASS is True


def test_unauthenticated_access_to_main_pages():
    """
    Verifies that all main application pages load with 200 OK without requiring login or session cookies.
    """
    pages = [
        "/",
        "/dashboard",
        "/explore",
        "/plan-trip",
        "/profile",
        "/my-trips",
        "/my-favorites",
        "/chat",
        "/destination/1"
    ]

    for p in pages:
        res = client.get(p)
        assert res.status_code == 200, f"Failed to access page {p} without login"


def test_dev_user_auto_creation_and_persistence():
    """
    Verifies that dev@aitravelplanner.local is automatically created and attached to requests.
    """
    db = SessionLocal()
    dev_user = db.query(User).filter(User.email == DEV_USER_EMAIL).first()
    db.close()

    assert dev_user is not None
    assert dev_user.full_name == "Dev Traveler"
    assert dev_user.is_verified is True
    assert dev_user.is_mobile_verified is True
