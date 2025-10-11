"""Unit tests configuration and fixtures."""

import asyncio
import tempfile
from unittest.mock import AsyncMock, Mock

import pytest
from dementia_simulation.evaluator.empathy_evaluator import EmpathyEvaluator
from dementia_simulation.persona.models import (
    DementiaPersona,
    DementiaStage,
    create_sample_personas,
)
from dementia_simulation.rag.pipeline import DementiaRAGPipeline
from dementia_simulation.retriever.faiss_retriever import FAISSRetriever


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_personas():
    """Create sample personas for testing."""
    return create_sample_personas()


@pytest.fixture
def mild_dementia_persona():
    """Create a mild dementia persona for testing."""
    return DementiaPersona(
        name="Test Margaret",
        age=78,
        stage=DementiaStage.MILD,
        background={"profession": "Teacher", "family": "Widow"},
    )


@pytest.fixture
def mock_retriever():
    """Create a mock FAISS retriever."""
    retriever = Mock(spec=FAISSRetriever)
    retriever.search.return_value = [
        ({"text": "Test knowledge", "category": "test"}, 0.8)
    ]
    retriever.get_stats.return_value = {
        "total_documents": 10,
        "model_name": "test-model",
    }
    return retriever


@pytest.fixture
def mock_rag_pipeline(mock_retriever):
    """Create a mock RAG pipeline."""
    pipeline = Mock(spec=DementiaRAGPipeline)
    pipeline.retriever = mock_retriever

    async def mock_generate_response(user_input, persona, conversation_history=None):
        from dementia_simulation.rag.pipeline import RAGResponse

        return RAGResponse(
            response_text="Test response",
            retrieved_documents=[],
            confidence_score=0.8,
            persona_mood=persona.current_mood.value,
            processing_time=0.1,
            model_used="test-model",
        )

    pipeline.generate_response = AsyncMock(side_effect=mock_generate_response)
    return pipeline


@pytest.fixture
def sample_conversation_history():
    """Create sample conversation history for testing."""
    return [
        {
            "speaker": "caregiver",
            "message": "How are you feeling today?",
            "timestamp": "2024-01-01T10:00:00",
        },
        {
            "speaker": "patient",
            "message": "I'm confused. Where am I?",
            "timestamp": "2024-01-01T10:00:05",
            "mood": "confused",
        },
        {
            "speaker": "caregiver",
            "message": "You're safe here with me. I understand this is confusing.",
            "timestamp": "2024-01-01T10:00:10",
        },
    ]


@pytest.fixture
def empathy_evaluator():
    """Create an empathy evaluator for testing."""
    return EmpathyEvaluator()


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
