import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal, init_db
from app.database.models import User, Trip
from app.core.security import hash_password

init_db()
client = TestClient(app)


def setup_user(email: str, mobile: str = "+919999988888"):
    db: Session = SessionLocal()
    db.query(User).filter(User.email == email).delete()
    db.commit()

    user = User(
        email=email,
        mobile_number=mobile,
        full_name="Phase 8 Tester",
        hashed_password=hash_password("Password123"),
        is_active=True,
        is_verified=True,
        is_mobile_verified=True,
        travel_style="Comfort",
        food_preference="Vegetarian",
        interests="Nature, History, Food"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    login_res = client.post("/auth/login/json", json={"email": email, "password": "Password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    return email, headers, user.id


def test_plan_my_trip_and_itinerary_generation():
    email, headers, user_id = setup_user("phase8_trip_user@example.com")

    # Create trip via Plan My Trip
    payload = {
        "destination_name": "Tokyo",
        "number_of_days": 4,
        "number_of_travelers": 2,
        "trip_type": "Friends",
        "travel_style": "Comfort",
        "interests": ["Nature", "Photography", "Food"],
        "food_preferences": "Vegetarian",
        "special_requirements": "Relaxed schedule"
    }

    res = client.post("/trips", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()

    assert data["destination_name"] == "Tokyo"
    assert data["number_of_days"] == 4
    assert data["number_of_travelers"] == 2
    assert data["trip_type"] == "Friends"
    assert data["travel_style"] == "Comfort"

    trip_id = data["id"]

    # Read trip details
    read_res = client.get(f"/trips/{trip_id}", headers=headers)
    assert read_res.status_code == 200
    trip_data = read_res.json()

    assert len(trip_data["itinerary"]) == 4
    assert "morning" in trip_data["itinerary"][0]
    assert "afternoon" in trip_data["itinerary"][0]
    assert "evening" in trip_data["itinerary"][0]
    assert len(trip_data["packing_list"]) > 0


def test_expense_tracking():
    email, headers, user_id = setup_user("phase8_expense_user@example.com")

    trip_res = client.post("/trips", json={
        "destination_name": "Delhi",
        "number_of_days": 3,
        "trip_type": "Solo",
        "travel_style": "Budget"
    }, headers=headers)
    trip_id = trip_res.json()["id"]

    # Update actual expenses
    expense_payload = {
        "accommodation": 3500.0,
        "food": 1800.0,
        "local_transportation": 600.0,
        "intercity_transportation": 1200.0,
        "activities": 300.0,
        "shopping": 500.0,
        "misc": 200.0
    }

    put_res = client.put(f"/trips/{trip_id}/expenses", json=expense_payload, headers=headers)
    assert put_res.status_code == 200
    assert put_res.json()["actual_expenses"]["accommodation"] == 3500.0

    read_res = client.get(f"/trips/{trip_id}", headers=headers)
    assert read_res.json()["actual_expenses"]["food"] == 1800.0


def test_packing_checklist_update():
    email, headers, user_id = setup_user("phase8_packing_user@example.com")

    trip_res = client.post("/trips", json={
        "destination_name": "Paris",
        "number_of_days": 3,
        "trip_type": "Solo"
    }, headers=headers)
    trip_id = trip_res.json()["id"]

    updated_items = [
        {"item": "Comfortable Walking Shoes", "category": "Footwear", "checked": True},
        {"item": "Passport & Tickets", "category": "Documents", "checked": True},
        {"item": "Camera", "category": "Electronics", "checked": False}
    ]

    put_res = client.put(f"/trips/{trip_id}/packing-list", json={"items": updated_items}, headers=headers)
    assert put_res.status_code == 200

    read_res = client.get(f"/trips/{trip_id}", headers=headers)
    assert read_res.json()["packing_list"][0]["checked"] is True


def test_stateful_replanning():
    email, headers, user_id = setup_user("phase8_replan_user@example.com")

    trip_res = client.post("/trips", json={
        "destination_name": "Kyoto",
        "number_of_days": 3,
        "travel_style": "Premium"
    }, headers=headers)
    trip_id = trip_res.json()["id"]

    replan_res = client.post(f"/trips/{trip_id}/replan?travel_style=Budget", headers=headers)
    assert replan_res.status_code == 200
    assert replan_res.json()["trip"]["travel_style"] == "Budget"


def test_personalized_recommendations_and_emergency():
    email, headers, user_id = setup_user("phase8_rec_user@example.com")

    rec_res = client.get("/travel/recommendations", headers=headers)
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert len(recs) > 0
    assert "recommendation_reason" in recs[0]

    emergency_res = client.get("/travel/emergency/1")
    assert emergency_res.status_code == 200
    em_data = emergency_res.json()
    assert "emergency_contacts" in em_data
    assert "police" in em_data["emergency_contacts"]
