import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal
from app.database.models import User

client = TestClient(app, follow_redirects=False)


def test_public_pages_load():
    """
    Verifies that all public HTML page routes load with 200 OK.
    """
    routes = [
        "/",
        "/explore",
        "/destination/1",
        "/login",
        "/register",
        "/verify-otp",
        "/verify-reset-otp",
        "/forgot-password",
        "/reset-password"
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Failed on route {route}"
        assert "text/html" in response.headers["content-type"]


def test_protected_pages_redirect_unauthenticated_users():
    """
    Verifies page route access behavior. When DEV_AUTH_BYPASS is active, pages load with 200 OK.
    """
    from app.core.dependencies import DEV_AUTH_BYPASS
    protected_routes = [
        "/dashboard",
        "/my-trips",
        "/my-favorites",
        "/profile",
        "/chat"
    ]
    for route in protected_routes:
        response = client.get(route)
        if DEV_AUTH_BYPASS:
            assert response.status_code == 200, f"Expected 200 OK for {route} during dev auth bypass"
        else:
            assert response.status_code == 303, f"Expected 303 redirect for unauthenticated access to {route}"
            assert response.headers["location"] == "/login"


def test_protected_pages_allow_authenticated_users():
    """
    Verifies that authenticated users with valid access_token cookie can access protected pages.
    """
    email = "page_auth_user@example.com"
    db: Session = SessionLocal()
    db.query(User).filter(User.email == email).delete()
    db.commit()
    db.close()

    client.post("/auth/register", json={
        "email": email,
        "full_name": "Page Auth User",
        "password": "password123",
        "confirm_password": "password123"
    })

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.is_verified = True
    db.commit()
    db.close()

    login_res = client.post("/auth/login/json", json={
        "email": email,
        "password": "password123"
    })
    assert login_res.status_code == 200

    cookie = client.cookies.get("access_token")
    dash_res = client.get("/dashboard", cookies={"access_token": cookie})
    assert dash_res.status_code == 200
    assert "Page Auth User" in dash_res.text
