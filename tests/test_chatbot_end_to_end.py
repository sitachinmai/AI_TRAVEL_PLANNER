import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ACCEPTANCE_QUERIES = [
    ("Hello", "Hello"),
    ("Plan a 3 day trip to Goa", "Goa"),
    ("What food should I try in Hyderabad?", "Hyderabad"),
    ("Best places in India", "India"),
    ("Best places in Japan", "Japan"),
    ("Plan a 7 day trip to Japan", "Japan"),
    ("Best time to visit Paris", "Paris"),
    ("Make Day 2 cheaper", "Day"),
    ("Add more nature activities", "Nature")
]


@pytest.mark.parametrize("query,expected_keyword", ACCEPTANCE_QUERIES)
def test_chatbot_acceptance_queries(query, expected_keyword):
    """
    Verifies that POST /ai/chat processes all required natural language queries
    and returns valid 200 OK JSON with expected keywords.
    """
    res = client.post("/ai/chat", json={"message": query})
    assert res.status_code == 200, f"Query '{query}' failed with {res.status_code}"
    data = res.json()
    assert "response" in data
    assert len(data["response"]) > 20
    assert expected_keyword.lower() in data["response"].lower()


def test_chat_page_renders_unauthenticated():
    """
    Verifies that GET /chat loads cleanly with 200 OK without authentication headers.
    """
    res = client.get("/chat")
    assert res.status_code == 200
    assert "AI Travel Assistant" in res.text or "AI Travel Buddy" in res.text
