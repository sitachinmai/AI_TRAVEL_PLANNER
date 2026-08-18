import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

PROMPTS = [
    "Plan a 5 day trip to Japan",
    "Best places to visit in India",
    "Plan a budget trip to Europe",
    "What food should I try in Thailand?",
    "Give me places to visit in Paris",
    "Plan a family trip to Singapore",
    "Show me mountain destinations",
    "Make my trip cheaper",
    "Change Day 2",
    "What are the best destinations for nature and photography?"
]


@pytest.mark.parametrize("prompt", PROMPTS)
def test_ai_chatbot_prompts(prompt):
    """
    Verifies that POST /ai/chat responds cleanly and meaningfully to all 10 required test prompts.
    """
    res = client.post("/ai/chat", json={"message": prompt})
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert len(data["response"]) > 30, f"Prompt '{prompt}' returned overly short response"
    assert "Sorry, I don't understand" not in data["response"]
