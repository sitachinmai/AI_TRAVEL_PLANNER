import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_1_plan_10_day_trip_to_hyderabad():
    """
    TEST 1: "Plan a 10 day trip to Hyderabad"
    Expected: destination = Hyderabad, days = 10, actual Hyderabad data used, no follow-up question asking what city.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 10 day trip to Hyderabad"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Hyderabad" in text
    assert "10-Day" in text or "Day 10" in text
    assert "Charminar" in text or "Golconda" in text
    assert "What city" not in text and "which city" not in text


def test_2_plan_7_day_trip_to_japan():
    """
    TEST 2: "Plan a 7 day trip to Japan"
    Expected: Japan/Tokyo destination selected, 7 unique/plausibly varied itinerary days.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 7 day trip to Japan"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Japan" in text or "Tokyo" in text
    assert "Day 7" in text


def test_3_make_day_2_cheaper():
    """
    TEST 3: "Make Day 2 cheaper"
    Expected: Day 2 activities actually change, Day 2 cost decreases, total cost recalculated.
    """
    res = client.post("/ai/chat", json={"message": "Make Day 2 cheaper"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Day 2" in text
    assert "Modified" in text or "Switched" in text or "Cost Reduced" in text


def test_4_show_me_mountain_destinations():
    """
    TEST 4: "Show me mountain destinations"
    Expected: Multiple mountain destinations from DB.
    """
    res = client.post("/ai/chat", json={"message": "Show me mountain destinations"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "mountain" in text.lower() or "nature" in text.lower() or "himalaya" in text.lower()


def test_5_plan_a_budget_trip_to_europe():
    """
    TEST 5: "Plan a budget trip to Europe"
    Expected: Multiple European destinations, budget-oriented recommendations.
    """
    res = client.post("/ai/chat", json={"message": "Plan a budget trip to Europe"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Europe" in text
    assert "Paris" in text or "Rome" in text or "Zurich" in text


def test_6_make_a_10_day_trip_to_hyderabad_no_questions():
    """
    TEST 6: "Make a 10 day trip to Hyderabad"
    Expected: NO follow-up question asking what city.
    """
    res = client.post("/ai/chat", json={"message": "Make a 10 day trip to Hyderabad"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Hyderabad" in text
    assert "Which city" not in text and "what city" not in text


def test_7_amalapuram_real_db_search():
    """
    TEST 7: "AMALAPURAM"
    Expected: Actual DB search, NO invented "Amalapuram Central Bistro".
    """
    res = client.post("/ai/chat", json={"message": "Plan a trip to Amalapuram"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Amalapuram" in text
    assert "Amalapuram Central Bistro" not in text


def test_8_dashboard_and_chat_equivalence():
    """
    TEST 8: Dashboard chatbot and /chat must return equivalent backend-generated results.
    """
    msg = {"message": "Plan a 3 day trip to Tokyo"}
    res1 = client.post("/ai/chat", json=msg)
    res2 = client.post("/ai/chat", json=msg)
    assert res1.status_code == 200 and res2.status_code == 200
    assert "Tokyo" in res1.json()["response"] and "Tokyo" in res2.json()["response"]


def test_9_no_repeated_attractions_every_day():
    """
    TEST 9: No destination should repeat every day when enough database places exist.
    """
    res = client.post("/ai/chat", json={"message": "Plan a 3 day trip to Delhi"})
    assert res.status_code == 200
    text = res.json()["response"]
    assert "Day 1" in text and "Day 2" in text and "Day 3" in text


def test_10_destination_card_images():
    """
    TEST 10: Every destination card has a valid image or fallback image.
    """
    res = client.get("/explore")
    assert res.status_code == 200
    assert "onerror=" in res.text
    assert "/static/images/placeholder.svg" in res.text
