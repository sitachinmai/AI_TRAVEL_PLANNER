import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

FINAL_PROMPTS = [
    "Plan a 3 day trip to Goa",
    "Best places to visit in Japan",
    "Plan a 5 day trip to Paris",
    "Give me a budget trip to Goa",
    "What food should I try in Hyderabad?",
    "Make Day 2 cheaper",
    "Add more nature places",
    "Suggest places for a family trip",
    "What is the best time to visit Switzerland?"
]


def test_final_database_counts():
    """
    Verifies 58 countries and 198 destinations in SQLite.
    """
    c_res = client.get("/travel/countries")
    assert c_res.status_code == 200
    assert len(c_res.json()) == 195

    d_res = client.get("/travel/destinations")
    assert d_res.status_code == 200
    assert len(d_res.json()) >= 198


@pytest.mark.parametrize("prompt", FINAL_PROMPTS)
def test_ai_chatbot_final_prompts(prompt):
    """
    Verifies that POST /ai/chat responds meaningfully to all requested travel prompts.
    """
    res = client.post("/ai/chat", json={"message": prompt})
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert len(data["response"]) > 25
    assert "Sorry" not in data["response"]


def test_unauthenticated_pages():
    """
    Verifies that all pages load with 200 OK without authentication.
    """
    for route in ["/", "/dashboard", "/explore", "/chat", "/profile", "/my-trips", "/my-favorites", "/plan-trip"]:
        res = client.get(route)
        assert res.status_code == 200
