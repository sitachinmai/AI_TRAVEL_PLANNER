import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal, init_db
from app.database.models import User, Trip, Favorite, TravelHistory
from app.core.security import hash_password, hash_otp

init_db()
client = TestClient(app)


def setup_authenticated_user(email: str = "settings_test_user@example.com", mobile: str = "+919999988888"):
    db: Session = SessionLocal()
    db.query(User).filter(User.email == email).delete()
    db.commit()

    user = User(
        email=email,
        mobile_number=mobile,
        full_name="Settings Test User",
        hashed_password=hash_password("OldPassword123"),
        is_active=True,
        is_verified=True,
        is_mobile_verified=True,
        preferred_language="en"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    login_res = client.post("/auth/login/json", json={"email": email, "password": "OldPassword123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    return email, headers


def test_change_password():
    email, headers = setup_authenticated_user("change_pass_user@example.com")
    res = client.put("/auth/change-password", json={
        "current_password": "OldPassword123",
        "new_password": "NewPassword456",
        "confirm_new_password": "NewPassword456"
    }, headers=headers)
    assert res.status_code == 200
    assert "updated" in res.json()["message"].lower()


def test_language_update():
    email, headers = setup_authenticated_user("lang_user@example.com")
    res = client.put("/auth/language", json={"language": "hi"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["preferred_language"] == "hi"


def test_change_phone_number_with_otp():
    email, headers = setup_authenticated_user("change_phone_user@example.com", "+919876500001")

    # Request phone change
    new_phone = "+919876500002"
    req_res = client.post("/auth/change-phone", json={"new_mobile_number": new_phone}, headers=headers)
    assert req_res.status_code == 200

    # Set known OTP hash in DB
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.pending_mobile_otp_hash = hash_otp("55555")
    db.commit()
    db.close()

    # Verify phone change
    ver_res = client.post("/auth/verify-phone-change", json={"new_mobile_number": new_phone, "otp": "55555"}, headers=headers)
    assert ver_res.status_code == 200

    # Verify DB state
    db = SessionLocal()
    user_updated = db.query(User).filter(User.email == email).first()
    assert user_updated.mobile_number == new_phone
    assert user_updated.is_mobile_verified is True
    db.close()


def test_trips_favorites_history_isolation():
    email1, headers1 = setup_authenticated_user("user1_trips@example.com")
    email2, headers2 = setup_authenticated_user("user2_trips@example.com")

    # User 1 creates trip
    trip_res = client.post("/trips", json={
        "destination_name": "Delhi",
        "number_of_days": 3,
        "trip_type": "Solo",
        "travel_style": "Budget"
    }, headers=headers1)
    assert trip_res.status_code == 201
    trip_id = trip_res.json()["id"]

    # User 1 adds favorite
    fav_res = client.post("/favorites", json={
        "item_type": "destination",
        "item_id": 1,
        "title": "Delhi Heritage"
    }, headers=headers1)
    assert fav_res.status_code == 201

    # User 2 lists trips and favorites
    user2_trips = client.get("/trips", headers=headers2).json()
    user2_favs = client.get("/favorites", headers=headers2).json()

    assert all(t["id"] != trip_id for t in user2_trips)
    assert len(user2_favs) == 0

    # User 2 cannot read User 1's trip details (404 Unauthorized)
    unauth_trip = client.get(f"/trips/{trip_id}", headers=headers2)
    assert unauth_trip.status_code == 404


def test_ai_chat_endpoint():
    email, headers = setup_authenticated_user("ai_chat_user@example.com")
    res = client.post("/ai/chat", json={"message": "Plan a 3-day budget trip to Japan"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert "Tokyo" in data["response"] or "Japan" in data["response"]
