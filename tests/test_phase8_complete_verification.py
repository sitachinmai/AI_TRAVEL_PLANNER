import os
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal, DB_PATH
from app.database.models import User, Country, Destination, Trip, Favorite, TravelHistory
from app.core.security import hash_password, hash_otp

client = TestClient(app)


def test_real_database_file_and_connection():
    """
    Verifies that the application uses the real SQLite database file data/travel_planner.db.
    """
    assert os.path.exists(DB_PATH)
    db: Session = SessionLocal()
    
    country_count = db.query(Country).count()
    dest_count = db.query(Destination).count()
    user_count = db.query(User).count()
    
    db.close()
    
    assert country_count >= 14
    assert dest_count >= 100
    assert user_count >= 1


def test_travel_api_returns_complete_dataset():
    """
    Verifies that GET /travel/countries and GET /travel/destinations return the complete dataset.
    """
    res_countries = client.get("/travel/countries")
    assert res_countries.status_code == 200
    countries = res_countries.json()
    assert len(countries) >= 14

    res_dests = client.get("/travel/destinations")
    assert res_dests.status_code == 200
    dests = res_dests.json()
    assert len(dests) >= 100

    # Search query verification
    res_search = client.get("/travel/destinations?q=Hyderabad")
    assert res_search.status_code == 200
    assert any(d["name"] == "Hyderabad" for d in res_search.json())

    res_search_paris = client.get("/travel/destinations?q=Paris")
    assert res_search_paris.status_code == 200
    assert any(d["name"] == "Paris" for d in res_search_paris.json())


def test_phone_change_otp_flow():
    """
    Tests Profile Settings -> Phone Number Change OTP flow.
    """
    db: Session = SessionLocal()
    email = f"phone_change_{datetime.now().timestamp()}@example.com"
    user = User(
        email=email,
        full_name="Phone Change User",
        mobile_number="+919100000001",
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
        is_mobile_verified=True
    )
    db.add(user)
    db.commit()

    # Login to obtain token
    login_res = client.post("/auth/login/json", json={"email": email, "password": "Password123!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Request phone change
    new_mobile = f"+9191{int(datetime.now().timestamp()) % 100000000}"
    req_res = client.post("/auth/change-phone", json={"new_mobile_number": new_mobile}, headers=headers)
    assert req_res.status_code == 200

    # Verify user pending mobile and hash set
    db.refresh(user)
    assert user.pending_mobile_number == new_mobile
    assert user.pending_mobile_otp_hash is not None

    # Verify phone change with OTP
    raw_otp = "99999"
    user.pending_mobile_otp_hash = hash_otp(raw_otp)
    user.pending_mobile_otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    verify_res = client.post("/auth/verify-phone-change", json={"new_mobile_number": new_mobile, "otp": raw_otp}, headers=headers)
    assert verify_res.status_code == 200

    # User mobile number must now be updated
    db.refresh(user)
    assert user.mobile_number == new_mobile
    assert user.pending_mobile_number is None
    db.close()


def test_ai_chat_natural_language_response():
    """
    Verifies that POST /ai/chat responds using the RAG database layer.
    """
    chat_res = client.post("/ai/chat", json={"message": "Suggest budget destinations in India"})
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert "response" in data
    assert len(data["response"]) > 10


def test_user_data_isolation():
    """
    Verifies that User A cannot access User B's trips or favorites.
    """
    db: Session = SessionLocal()
    user_a = User(email=f"user_a_{datetime.now().timestamp()}@example.com", full_name="User A", hashed_password=hash_password("Pass123!"), is_verified=True, is_mobile_verified=True)
    user_b = User(email=f"user_b_{datetime.now().timestamp()}@example.com", full_name="User B", hashed_password=hash_password("Pass123!"), is_verified=True, is_mobile_verified=True)
    db.add_all([user_a, user_b])
    db.commit()

    trip_a = Trip(user_id=user_a.id, title="Goa Beach Trip", destination_name="Goa", start_date="2026-10-01", end_date="2026-10-05")
    db.add(trip_a)
    db.commit()

    # User B tries to replan User A's trip -> Must be rejected (404/403)
    login_b = client.post("/auth/login/json", json={"email": user_b.email, "password": "Pass123!"})
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    replan_res = client.post(f"/trips/{trip_a.id}/replan", json={"prompt": "Make it cheaper"}, headers=headers_b)
    assert replan_res.status_code in [403, 404]

    db.close()
