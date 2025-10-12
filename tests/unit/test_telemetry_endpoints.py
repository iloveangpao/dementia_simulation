"""Tests for telemetry-related API endpoints."""

import json

import pytest
from fastapi.testclient import TestClient

from src.dementia_simulation.api.server import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_reset_endpoint(client):
    """Test the /reset endpoint."""
    # First create some sessions by chatting
    response1 = client.post(
        "/chat",
        json={
            "message": "Hello",
            "session_id": "test_session_1",
            "persona_id": "persona_1",
        },
    )
    assert response1.status_code == 200

    response2 = client.post(
        "/chat",
        json={
            "message": "Hello",
            "session_id": "test_session_2",
            "persona_id": "persona_1",
        },
    )
    assert response2.status_code == 200

    # Now reset all sessions
    reset_response = client.post("/reset")
    assert reset_response.status_code == 200
    data = reset_response.json()
    assert "sessions_cleared" in data
    assert data["sessions_cleared"] >= 0

    # Verify sessions are gone
    session_response = client.get("/sessions/test_session_1")
    assert session_response.status_code == 404


def test_export_endpoint(client):
    """Test the /export endpoint."""
    # Create a session with some messages
    client.post(
        "/chat",
        json={
            "message": "Hello there",
            "session_id": "export_test",
            "persona_id": "persona_1",
        },
    )
    client.post(
        "/chat",
        json={
            "message": "How are you?",
            "session_id": "export_test",
            "persona_id": "persona_1",
        },
    )

    # Export the transcript
    export_response = client.get("/export?session_id=export_test")
    assert export_response.status_code == 200

    # Verify JSONL format
    lines = export_response.text.strip().split("\n")
    assert len(lines) >= 2  # At least 2 messages (user + response for each turn)

    # Verify each line is valid JSON
    for line in lines:
        message = json.loads(line)
        assert "speaker" in message
        assert "message" in message
        assert "timestamp" in message


def test_export_nonexistent_session(client):
    """Test exporting a nonexistent session."""
    response = client.get("/export?session_id=nonexistent")
    assert response.status_code == 404


def test_metrics_quick_endpoint(client):
    """Test the /metrics/quick endpoint."""
    response = client.get("/metrics/quick")
    assert response.status_code == 200

    data = response.json()
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert "counters" in data
    assert "flags" in data

    # Verify counters structure
    counters = data["counters"]
    assert "total_turns" in counters
    assert "total_sessions" in counters
    assert "active_sessions" in counters
    assert "total_errors" in counters

    # Verify all counter values are integers
    for key, value in counters.items():
        assert isinstance(value, int)


def test_metrics_after_chat(client):
    """Test that metrics are updated after chat."""
    # Get initial metrics
    initial_response = client.get("/metrics/quick")
    initial_data = initial_response.json()
    initial_turns = initial_data["counters"]["total_turns"]

    # Perform a chat
    client.post(
        "/chat",
        json={
            "message": "Test message",
            "session_id": "metrics_test",
            "persona_id": "persona_1",
        },
    )

    # Get updated metrics
    updated_response = client.get("/metrics/quick")
    updated_data = updated_response.json()
    updated_turns = updated_data["counters"]["total_turns"]

    # Verify turns increased
    assert updated_turns > initial_turns


def test_session_lifecycle_telemetry(client):
    """Test complete session lifecycle with telemetry."""
    session_id = "lifecycle_test"

    # Create session via chat
    chat_response = client.post(
        "/chat",
        json={
            "message": "Start conversation",
            "session_id": session_id,
            "persona_id": "persona_1",
        },
    )
    assert chat_response.status_code == 200

    # Verify session exists
    session_response = client.get(f"/sessions/{session_id}")
    assert session_response.status_code == 200

    # Export transcript
    export_response = client.get(f"/export?session_id={session_id}")
    assert export_response.status_code == 200

    # Delete session
    delete_response = client.delete(f"/sessions/{session_id}")
    assert delete_response.status_code == 200

    # Verify session is gone
    session_response_after = client.get(f"/sessions/{session_id}")
    assert session_response_after.status_code == 404


def test_reset_clears_all_sessions(client):
    """Test that reset clears all sessions."""
    # Create multiple sessions
    for i in range(3):
        client.post(
            "/chat",
            json={
                "message": f"Message {i}",
                "session_id": f"reset_test_{i}",
                "persona_id": "persona_1",
            },
        )

    # Reset all
    reset_response = client.post("/reset")
    assert reset_response.status_code == 200
    data = reset_response.json()
    assert data["sessions_cleared"] >= 3

    # Verify all sessions are gone
    for i in range(3):
        session_response = client.get(f"/sessions/reset_test_{i}")
        assert session_response.status_code == 404


def test_export_empty_session(client):
    """Test exporting a session with no messages (should not exist)."""
    response = client.get("/export?session_id=empty_session")
    assert response.status_code == 404


def test_metrics_counters_increment(client):
    """Test that various counters increment correctly."""
    # Get initial state
    initial = client.get("/metrics/quick").json()

    # Perform operations
    client.post(
        "/chat",
        json={
            "message": "Test",
            "session_id": "counter_test_1",
            "persona_id": "persona_1",
        },
    )
    client.post(
        "/chat",
        json={
            "message": "Test",
            "session_id": "counter_test_2",
            "persona_id": "persona_1",
        },
    )

    # Check updated metrics
    final = client.get("/metrics/quick").json()

    # Total turns should increase
    assert final["counters"]["total_turns"] > initial["counters"]["total_turns"]

    # Total sessions should increase
    assert final["counters"]["total_sessions"] > initial["counters"]["total_sessions"]
