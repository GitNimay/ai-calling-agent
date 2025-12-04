"""
Basic tests for the AI Calling Agent API.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-calling-agent"


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


@pytest.mark.asyncio
async def test_chat_endpoint():
    """Test the chat endpoint."""
    response = client.post(
        "/chat",
        json={
            "message": "Hello, how are you?"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "model" in data
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0


@pytest.mark.asyncio
async def test_chat_with_history():
    """Test the chat endpoint with conversation history."""
    response = client.post(
        "/chat",
        json={
            "message": "What was my previous question?",
            "history": [
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "model", "content": "I'm doing great! How can I help you today?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
