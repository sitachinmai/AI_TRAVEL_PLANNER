import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ACCEPTANCE_TEST_CASES = [
    ("Hello", ["hello", "travel buddy", "ai"]),
    ("Plan a 3 day trip to Goa", ["goa", "day 1", "budget"]),
    ("What food should I try in Hyderabad?", ["hyderabad", "delicac"]),
    ("Best places in India", ["india", "places"]),
    ("Best places in Japan", ["japan", "tokyo"]),
    ("Plan a 7 day trip to Japan", ["japan", "day 1", "day 7"]),
    ("Best time to visit Paris", ["paris", "time"]),
    ("Make Day 2 cheaper", ["day 2", "budget"]),
    ("Add more nature activities", ["nature", "mountain"])
]


@pytest.mark.parametrize("prompt,expected_keywords", ACCEPTANCE_TEST_CASES)
def test_chatbot_acceptance_endpoints(prompt, expected_keywords):
    """
    Verifies that POST /ai/chat works independently and returns valid 200 OK responses with SQLite data.
    """
    response = client.post("/ai/chat", json={"message": prompt})
    assert response.status_code == 200, f"Failed prompt '{prompt}' with status {response.status_code}"
    
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 15
    
    resp_text = data["response"].lower()
    for kw in expected_keywords:
        assert kw.lower() in resp_text, f"Expected keyword '{kw}' missing in response for prompt '{prompt}'. Response: {data['response']}"


def test_chat_page_standalone_route():
    """
    Verifies that GET /chat returns 200 OK and renders the dedicated AI Assistant page.
    """
    response = client.get("/chat")
    assert response.status_code == 200
    assert "AI Travel Buddy" in response.text
    assert "chatForm" in response.text or "chat-form" in response.text
