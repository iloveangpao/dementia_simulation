"""Smoke tests for FastAPI server endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from dementia_simulation.api.server import AppState, app
from dementia_simulation.persona.models import create_sample_personas
from dementia_simulation.rag.pipeline import RAGResponse


@pytest.fixture
def test_client():
    """Create a test client with mocked dependencies."""
    return TestClient(app)


@pytest.fixture
def mock_app_state():
    """Create a mocked app state for testing."""
    state = Mock(spec=AppState)
    state.initialized = True
    state.personas = {}

    # Create sample personas
    personas = create_sample_personas()
    for i, persona in enumerate(personas):
        state.personas[f"persona_{i+1}"] = persona

    state.sessions = {}
    state.evaluator = Mock()
    state.rag_pipeline = Mock()

    # Mock session store
    state.session_store = Mock()
    state.turn_counters = {}

    # Mock telemetry logger
    state.telemetry_logger = Mock()
    state.telemetry_logger.log_turn = Mock()
    state.telemetry_logger.log_event = Mock()

    # Mock metrics collector
    state.metrics = Mock()
    state.metrics.increment = Mock()
    state.metrics.increment_flag = Mock()
    state.metrics.set_counter = Mock()

    # Mock the get_or_create_session method
    def mock_get_or_create_session(session_id):
        if session_id not in state.sessions:
            state.sessions[session_id] = {
                "created_at": "2024-01-01T00:00:00",
                "messages": [],
                "current_persona": None,
            }
        return state.sessions[session_id]

    state.get_or_create_session = mock_get_or_create_session

    # Mock session store set method
    state.session_store.set = Mock()

    # Mock RAG pipeline response
    async def mock_generate_response(user_input, persona, conversation_history):
        return RAGResponse(
            response_text="I'm feeling well, thank you for asking.",
            retrieved_documents=[],
            confidence_score=0.85,
            persona_mood="calm",
            processing_time=0.15,
            model_used="mock-model",
        )

    state.rag_pipeline.generate_response = AsyncMock(side_effect=mock_generate_response)

    # Mock evaluator
    async def mock_evaluate_conversation(conversation_history, caregiver_responses):
        return {
            "overall_score": 0.8,
            "detailed_scores": {
                "validation": 0.8,
                "emotional_support": 0.75,
                "patience": 0.85,
            },
            "feedback": ["Good validation of feelings"],
            "strengths": ["Excellent patience"],
            "improvements": ["Could improve emotional support"],
        }

    state.evaluator.evaluate_conversation = AsyncMock(
        side_effect=mock_evaluate_conversation
    )

    return state


def test_chat_and_evaluate_smoke(test_client, mock_app_state):
    """Test basic chat and evaluate endpoints work."""
    # Patch the app state
    with patch("dementia_simulation.api.server.app_state", mock_app_state):
        # Test chat endpoint with simple schema (text field)
        r = test_client.post("/chat", json={"session_id": "s1", "text": "hello"})
        assert r.status_code == 200
        body = r.json()
        # Check for both new and legacy field names
        assert "reply" in body or "response" in body
        assert "mood" in body or "persona_mood" in body

        # Test evaluate endpoint
        e = test_client.post(
            "/evaluate", json={"transcript": "I understand. It's okay."}
        )
        assert e.status_code == 200
        body = e.json()
        assert "overall_score" in body or "overall_empathy_score" in body
        assert "flags" in body or "detailed_scores" in body


def test_chat_basic(test_client, mock_app_state):
    """Test chat endpoint returns proper response."""
    with patch("dementia_simulation.api.server.app_state", mock_app_state):
        response = test_client.post(
            "/chat",
            json={"message": "How are you today?", "session_id": "test-session"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "reply" in data
        assert "persona_mood" in data or "mood" in data
        assert "session_id" in data


def test_evaluate_basic(test_client, mock_app_state):
    """Test evaluate endpoint returns proper response."""
    with patch("dementia_simulation.api.server.app_state", mock_app_state):
        response = test_client.post(
            "/evaluate",
            json={
                "conversation_history": [
                    {
                        "speaker": "caregiver",
                        "message": "I understand how you feel.",
                    }
                ],
                "caregiver_responses": ["I understand how you feel."],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_empathy_score" in data or "overall_score" in data


def test_health_check(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_root_endpoint(test_client):
    """Test root endpoint returns HTML."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
