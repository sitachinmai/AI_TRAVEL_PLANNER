import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import AUTH_ENABLED, DEV_AUTH_BYPASS

client = TestClient(app)


def test_auth_globally_disabled():
    """
    Verifies that AUTH_ENABLED is False and DEV_AUTH_BYPASS is True.
    """
    assert AUTH_ENABLED is False
    assert DEV_AUTH_BYPASS is True


def test_root_and_all_web_routes_open_directly_without_login():
    """
    Verifies that opening / and all main pages load directly with 200 OK without 401/403 or redirects.
    """
    routes = [
        "/",
        "/dashboard",
        "/explore",
        "/chat",
        "/profile",
        "/my-trips",
        "/my-favorites",
        "/plan-trip",
        "/destination/1"
    ]
    for r in routes:
        res = client.get(r)
        assert res.status_code == 200, f"Route {r} failed to load directly (Got {res.status_code})"


def test_all_travel_and_trip_apis_work_without_auth():
    """
    Verifies that all API endpoints return 200 OK without 401 or 403.
    """
    api_routes = [
        "/travel/countries",
        "/travel/destinations",
        "/travel/search?q=India",
        "/trips",
        "/favorites",
        "/history"
    ]
    for api in api_routes:
        res = client.get(api)
        assert res.status_code == 200, f"API {api} returned {res.status_code}"

    # Verify AI Chat API
    chat_res = client.post("/ai/chat", json={"message": "Plan a 5 day trip to Japan"})
    assert chat_res.status_code == 200
    assert "response" in chat_res.json()
