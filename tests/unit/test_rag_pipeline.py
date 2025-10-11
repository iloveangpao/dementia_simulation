"""Unit tests for RAG pipeline."""

import pytest
from unittest.mock import Mock

from dementia_simulation.rag.pipeline import (
    DementiaRAGPipeline,
    RAGResponse,
    generate_response,
)
from dementia_simulation.persona.models import (
    MoodState,
    create_sample_personas,
)
from dementia_simulation.retriever.faiss_retriever import FAISSRetriever


class TestRAGResponse:
    """Test RAGResponse dataclass."""

    def test_rag_response_creation(self):
        """Test creating a RAG response."""
        response = RAGResponse(
            response_text="I'm feeling a bit confused today.",
            retrieved_documents=[{"text": "Document 1"}],
            confidence_score=0.85,
            persona_mood="confused",
            processing_time=0.5,
            model_used="mock",
        )

        assert response.response_text == "I'm feeling a bit confused today."
        assert len(response.retrieved_documents) == 1
        assert response.confidence_score == 0.85
        assert response.persona_mood == "confused"
        assert response.processing_time == 0.5
        assert response.model_used == "mock"


class TestDementiaRAGPipeline:
    """Test DementiaRAGPipeline class."""

    @pytest.fixture
    def mock_retriever(self):
        """Create a mock retriever."""
        retriever = Mock(spec=FAISSRetriever)
        retriever.search.return_value = [
            (
                {
                    "text": "Validate the patient's feelings",
                    "severity": ["mild", "moderate"],
                },
                0.9,
            ),
            (
                {
                    "text": "Use simple, clear language",
                    "severity": ["mild", "moderate", "severe"],
                },
                0.8,
            ),
        ]
        retriever.get_stats.return_value = {"total_docs": 10}
        return retriever

    @pytest.fixture
    def sample_persona(self):
        """Create a sample persona for testing."""
        personas = create_sample_personas()
        return personas[0]  # Mild dementia persona

    @pytest.fixture
    def rag_pipeline(self, mock_retriever):
        """Create a RAG pipeline instance for testing."""
        return DementiaRAGPipeline(retriever=mock_retriever, model_name="mock")

    def test_pipeline_initialization(self, mock_retriever):
        """Test pipeline initialization with different configurations."""
        # Test with retriever
        pipeline = DementiaRAGPipeline(retriever=mock_retriever)
        assert pipeline.retriever == mock_retriever
        assert pipeline.model_name == "microsoft/DialoGPT-medium"
        assert pipeline.use_openai is False
        assert pipeline.temperature == 0.7

        # Test with custom model
        pipeline = DementiaRAGPipeline(model_name="gpt2")
        assert pipeline.model_name == "gpt2"

        # Test with OpenAI
        pipeline = DementiaRAGPipeline(use_openai=True)
        assert pipeline.use_openai is True

    def test_retrieve_context(self, rag_pipeline, sample_persona):
        """Test context retrieval."""
        results = rag_pipeline.retrieve_context(
            "How are you feeling?", sample_persona, k=2
        )

        assert isinstance(results, list)
        assert len(results) <= 2
        rag_pipeline.retriever.search.assert_called_once()

    def test_build_prompt(self, rag_pipeline, sample_persona):
        """Test prompt building."""
        context_docs = [
            {"text": "Validate feelings", "severity": ["mild"]},
            {"text": "Use simple language", "severity": ["mild", "moderate"]},
        ]

        prompt = rag_pipeline.build_prompt(
            user_input="How are you?",
            persona=sample_persona,
            context_documents=context_docs,
            conversation_history=None,
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "How are you?" in prompt
        # Check that persona context is included
        assert sample_persona.name in prompt or sample_persona.stage.value in prompt

    def test_build_prompt_with_history(self, rag_pipeline, sample_persona):
        """Test prompt building with conversation history."""
        context_docs = [{"text": "Test doc", "severity": ["mild"]}]
        history = [
            {"speaker": "caregiver", "message": "Hello!"},
            {"speaker": "patient", "message": "Hi there."},
        ]

        prompt = rag_pipeline.build_prompt(
            user_input="How are you feeling?",
            persona=sample_persona,
            context_documents=context_docs,
            conversation_history=history,
        )

        assert "Hello!" in prompt
        assert "How are you feeling?" in prompt

    def test_generate_mock_response(self, rag_pipeline, sample_persona):
        """Test mock response generation."""
        response = rag_pipeline.generate_mock_response(
            persona=sample_persona, user_input="How are you?"
        )

        assert isinstance(response, str)
        assert len(response) > 0

    def test_generate_mock_response_different_moods(self, rag_pipeline, sample_persona):
        """Test mock responses for different moods."""
        # Test agitated mood
        sample_persona.current_mood = MoodState.AGITATED
        response = rag_pipeline.generate_mock_response(sample_persona, "Test")
        assert "don't want" in response.lower() or "leave me alone" in response.lower()

        # Test anxious mood
        sample_persona.current_mood = MoodState.ANXIOUS
        response = rag_pipeline.generate_mock_response(sample_persona, "Test")
        assert "worried" in response.lower() or "not right" in response.lower()

        # Test confused mood
        sample_persona.current_mood = MoodState.CONFUSED
        response = rag_pipeline.generate_mock_response(sample_persona, "Test")
        assert "don't understand" in response.lower()

    @pytest.mark.asyncio
    async def test_generate_response_basic(self, rag_pipeline, sample_persona):
        """Test basic response generation."""
        response = await rag_pipeline.generate_response(
            user_input="How are you feeling today?", persona=sample_persona
        )

        assert isinstance(response, RAGResponse)
        assert isinstance(response.response_text, str)
        assert len(response.response_text) > 0
        assert isinstance(response.retrieved_documents, list)
        assert isinstance(response.confidence_score, float)
        assert 0.0 <= response.confidence_score <= 1.0
        assert response.persona_mood in [mood.value for mood in MoodState]
        assert response.processing_time >= 0
        assert response.model_used in ["mock", "openai-gpt-3.5-turbo"] or response.model_used.startswith("microsoft/")

    @pytest.mark.asyncio
    async def test_generate_response_with_history(self, rag_pipeline, sample_persona):
        """Test response generation with conversation history."""
        history = [
            {"speaker": "caregiver", "message": "Good morning!"},
            {"speaker": "patient", "message": "Good morning."},
        ]

        response = await rag_pipeline.generate_response(
            user_input="Would you like some breakfast?",
            persona=sample_persona,
            conversation_history=history,
        )

        assert isinstance(response, RAGResponse)
        assert len(response.response_text) > 0

    @pytest.mark.asyncio
    async def test_generate_response_mood_triggers(self, rag_pipeline, sample_persona):
        """Test that mood is updated based on input triggers."""
        # Test validation trigger
        await rag_pipeline.generate_response(
            user_input="That's good, you're doing well.", persona=sample_persona
        )

        # Mood might have changed
        assert sample_persona.current_mood in [mood for mood in MoodState]

    @pytest.mark.asyncio
    async def test_generate_response_updates_persona_history(
        self, rag_pipeline, sample_persona
    ):
        """Test that conversation history is updated in persona."""
        initial_history_len = len(sample_persona.conversation_history)

        await rag_pipeline.generate_response(
            user_input="Hello!", persona=sample_persona
        )

        # History should have 2 new entries (caregiver + patient)
        assert len(sample_persona.conversation_history) == initial_history_len + 2

    def test_get_pipeline_stats(self, rag_pipeline):
        """Test retrieving pipeline statistics."""
        stats = rag_pipeline.get_pipeline_stats()

        assert isinstance(stats, dict)
        assert "model_name" in stats
        assert "use_openai" in stats
        assert "retriever_stats" in stats
        assert "model_loaded" in stats


class TestConvenienceFunction:
    """Test the convenience generate_response function."""

    @pytest.fixture
    def sample_persona(self):
        """Create a sample persona for testing."""
        personas = create_sample_personas()
        return personas[0]

    @pytest.mark.asyncio
    async def test_generate_response_function_basic(self, sample_persona):
        """Test basic usage of the convenience function."""
        response = await generate_response(
            user_input="How are you today?", persona=sample_persona
        )

        assert isinstance(response, RAGResponse)
        assert isinstance(response.response_text, str)
        assert len(response.response_text) > 0

    @pytest.mark.asyncio
    async def test_generate_response_function_with_history(self, sample_persona):
        """Test convenience function with history parameter."""
        history = [
            {"speaker": "caregiver", "message": "Good morning!"},
            {"speaker": "patient", "message": "Morning."},
        ]

        response = await generate_response(
            user_input="Did you sleep well?", persona=sample_persona, history=history
        )

        assert isinstance(response, RAGResponse)
        assert len(response.response_text) > 0

    @pytest.mark.asyncio
    async def test_generate_response_function_custom_model(self, sample_persona):
        """Test convenience function with custom model name."""
        response = await generate_response(
            user_input="Hello!", persona=sample_persona, model_name="gpt2"
        )

        assert isinstance(response, RAGResponse)
        # When using non-existent model, it should fall back to mock
        assert response.model_used in ["mock", "gpt2"]

    @pytest.mark.asyncio
    async def test_generate_response_function_with_retriever(self, sample_persona):
        """Test convenience function with custom retriever."""
        mock_retriever = Mock(spec=FAISSRetriever)
        mock_retriever.search.return_value = [
            ({"text": "Test doc", "severity": ["mild"]}, 0.9)
        ]
        mock_retriever.get_stats.return_value = {"total_docs": 1}

        response = await generate_response(
            user_input="Hello!",
            persona=sample_persona,
            retriever=mock_retriever,
        )

        assert isinstance(response, RAGResponse)
        mock_retriever.search.assert_called()


class TestRAGPipelineIntegration:
    """Integration tests for RAG pipeline."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test a full conversation flow through the pipeline."""
        personas = create_sample_personas()
        persona = personas[1]  # Moderate dementia

        pipeline = DementiaRAGPipeline()

        # First interaction
        response1 = await pipeline.generate_response(
            user_input="Hello, how are you today?", persona=persona
        )
        assert isinstance(response1, RAGResponse)
        assert len(response1.response_text) > 0

        # Second interaction with history
        history = [
            {"speaker": "caregiver", "message": "Hello, how are you today?"},
            {"speaker": "patient", "message": response1.response_text},
        ]

        response2 = await pipeline.generate_response(
            user_input="Would you like to have lunch?",
            persona=persona,
            conversation_history=history,
        )
        assert isinstance(response2, RAGResponse)
        assert len(response2.response_text) > 0

    @pytest.mark.asyncio
    async def test_different_dementia_stages(self):
        """Test responses for different dementia stages."""
        personas = create_sample_personas()
        pipeline = DementiaRAGPipeline()

        for persona in personas:
            response = await pipeline.generate_response(
                user_input="How are you feeling?", persona=persona
            )

            assert isinstance(response, RAGResponse)
            assert len(response.response_text) > 0
            # Response should reflect the persona's stage
            assert response.persona_mood in [mood.value for mood in MoodState]
