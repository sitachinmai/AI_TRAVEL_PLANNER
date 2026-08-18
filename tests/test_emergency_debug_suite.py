import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_1_greetings():
    res = client.post("/ai/chat", json={"message": "Hi"})
    assert res.status_code == 200
    assert "AI Travel Buddy" in res.json()["response"] or "Hello" in res.json()["response"]


def test_2_plan_5_day_trip_to_agra():
    res = client.post("/ai/chat", json={"message": "Plan a 5 day trip to Agra"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Agra" in text
    assert "Delhi" not in text or "Agra (India)" in text
    assert "Taj Mahal" in text or "5-Day" in text


def test_3_plan_7_day_trip_to_japan():
    res = client.post("/ai/chat", json={"message": "Plan a 7 day trip to Japan"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Japan" in text or "Tokyo" in text


def test_4_show_mountain_destinations():
    res = client.post("/ai/chat", json={"message": "Show me mountain destinations"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Nature" in text or "Mountain" in text or "Zurich" in text or "Manali" in text or "Rishikesh" in text


def test_5_food_in_hyderabad():
    res = client.post("/ai/chat", json={"message": "What food should I try in Hyderabad?"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Hyderabad" in text
    assert "Biryani" in text or "Haleem" in text or "Popular Dishes" in text


def test_6_tell_me_about_kakinada():
    res = client.post("/ai/chat", json={"message": "Tell me about Kakinada"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Kakinada" in text or "currently limited" in text or "database" in text


def test_7_plan_10_day_trip_to_tirupati():
    res = client.post("/ai/chat", json={"message": "Plan a 10 day trip to Tirupati"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Tirupati" in text


def test_8_make_day_2_cheaper():
    # First establish trip context
    client.post("/ai/chat", json={"message": "Plan a 7 day trip to Japan"})
    res = client.post("/ai/chat", json={"message": "Make Day 2 cheaper"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Day 2" in text
    assert "modified" in text or "cheaper" in text or "Free" in text


def test_9_plan_budget_trip_to_europe():
    res = client.post("/ai/chat", json={"message": "Plan a budget trip to Europe"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Europe" in text
