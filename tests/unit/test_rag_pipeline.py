"""
Tests for the dementia_simulation.rag.pipeline module
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from dementia_simulation.rag.pipeline import (
    DementiaRAGPipeline,
    RAGResponse,
    generate_response
)
from dementia_simulation.persona.models import (
    DementiaPersona,
    DementiaStage,
    MoodState
)


class TestDementiaRAGPipeline:
    """Test DementiaRAGPipeline class."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization with default settings."""
        pipeline = DementiaRAGPipeline()
        
        assert pipeline is not None
        assert pipeline.model_name == "microsoft/DialoGPT-medium"
        assert pipeline.temperature == 0.7
        assert pipeline.max_context_length == 2048
    
    def test_pipeline_initialization_with_params(self):
        """Test pipeline initialization with custom parameters."""
        pipeline = DementiaRAGPipeline(
            model_name="test-model",
            temperature=0.5,
            max_context_length=1024
        )
        
        assert pipeline.model_name == "test-model"
        assert pipeline.temperature == 0.5
        assert pipeline.max_context_length == 1024
    
    def test_retrieve_context(self):
        """Test context retrieval functionality."""
        pipeline = DementiaRAGPipeline()
        persona = DementiaPersona("Test", 75, DementiaStage.MILD)
        
        # Mock the retriever
        pipeline.retriever.search = Mock(return_value=[
            ({"text": "Dementia care tip 1", "severity": ["mild"]}, 0.9),
            ({"text": "Dementia care tip 2", "severity": ["mild"]}, 0.8)
        ])
        
        docs = pipeline.retrieve_context("How are you?", persona, k=2)
        
        assert isinstance(docs, list)
        assert len(docs) <= 2
    
    def test_build_prompt(self):
        """Test prompt building functionality."""
        pipeline = DementiaRAGPipeline()
        persona = DementiaPersona(
            "Mary",
            75,
            DementiaStage.MILD,
            personality="gentle and caring"
        )
        
        context_docs = [
            {"text": "Dementia patients may forget recent events."}
        ]
        
        history = [
            {"speaker": "caregiver", "message": "Hello Mary", "timestamp": datetime.now().isoformat()}
        ]
        
        prompt = pipeline.build_prompt(
            "How are you feeling?",
            persona,
            context_docs,
            history
        )
        
        assert isinstance(prompt, str)
        assert "Mary" in prompt
        assert "How are you feeling?" in prompt
    
    def test_generate_mock_response(self):
        """Test mock response generation."""
        pipeline = DementiaRAGPipeline()
        persona = DementiaPersona("Test", 75, DementiaStage.MILD)
        
        response = pipeline.generate_mock_response(persona, "How are you?")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_mock_response_by_mood(self):
        """Test mock response generation based on mood."""
        pipeline = DementiaRAGPipeline()
        
        # Test agitated mood
        persona = DementiaPersona("Test", 75, DementiaStage.MILD)
        persona.current_mood = MoodState.AGITATED
        response = pipeline.generate_mock_response(persona, "Hello")
        assert "don't want" in response.lower() or "leave me alone" in response.lower()
        
        # Test anxious mood
        persona.current_mood = MoodState.ANXIOUS
        response = pipeline.generate_mock_response(persona, "Hello")
        assert "worried" in response.lower() or "anxious" in response.lower()
    
    @pytest.mark.asyncio
    async def test_generate_response_mock(self):
        """Test full response generation with mock responses."""
        pipeline = DementiaRAGPipeline()
        persona = DementiaPersona("Mary", 75, DementiaStage.MILD)
        
        # Mock the retriever
        pipeline.retriever.search = Mock(return_value=[])
        
        response = await pipeline.generate_response(
            "How are you feeling?",
            persona,
            None
        )
        
        assert isinstance(response, RAGResponse)
        assert isinstance(response.response_text, str)
        assert len(response.response_text) > 0
        assert response.model_used == "mock"
        assert isinstance(response.confidence_score, float)
        assert isinstance(response.processing_time, float)
    
    @pytest.mark.asyncio
    async def test_generate_response_with_history(self):
        """Test response generation with conversation history."""
        pipeline = DementiaRAGPipeline()
        persona = DementiaPersona("Mary", 75, DementiaStage.MILD)
        
        history = [
            {"speaker": "caregiver", "message": "Good morning", "timestamp": datetime.now().isoformat()},
            {"speaker": "patient", "message": "Hello", "timestamp": datetime.now().isoformat()}
        ]
        
        # Mock the retriever
        pipeline.retriever.search = Mock(return_value=[])
        
        response = await pipeline.generate_response(
            "How are you today?",
            persona,
            history
        )
        
        assert isinstance(response, RAGResponse)
        assert len(response.response_text) > 0
    
    def test_get_pipeline_stats(self):
        """Test getting pipeline statistics."""
        pipeline = DementiaRAGPipeline()
        
        stats = pipeline.get_pipeline_stats()
        
        assert isinstance(stats, dict)
        assert "model_name" in stats
        assert "use_openai" in stats
        assert "model_loaded" in stats


class TestGenerateResponseFunction:
    """Test the convenience generate_response function."""
    
    def test_generate_response_with_dict_persona(self):
        """Test generate_response with dictionary persona."""
        persona = {
            "name": "Mary",
            "age": "75",
            "condition": "mild dementia",
            "personality": "gentle and caring"
        }
        
        history = [
            {"user": "Hello", "assistant": "Hi there"}
        ]
        
        response = generate_response("How are you?", persona, history)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_response_with_persona_object(self):
        """Test generate_response with DementiaPersona object."""
        persona = DementiaPersona("Mary", 75, DementiaStage.MILD)
        
        response = generate_response("How are you?", persona, None)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_response_empty_history(self):
        """Test generate_response with no history."""
        persona = {
            "name": "John",
            "age": "80",
            "condition": "moderate dementia"
        }
        
        response = generate_response("Good morning", persona, None)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_response_stage_mapping(self):
        """Test that condition strings map to correct dementia stages."""
        # Test severe
        persona_severe = {
            "name": "Test",
            "age": "85",
            "condition": "severe dementia"
        }
        response = generate_response("Hello", persona_severe, None)
        assert isinstance(response, str)
        
        # Test moderate
        persona_moderate = {
            "name": "Test",
            "age": "80",
            "condition": "moderate dementia"
        }
        response = generate_response("Hello", persona_moderate, None)
        assert isinstance(response, str)
        
        # Test mild (default)
        persona_mild = {
            "name": "Test",
            "age": "75",
            "condition": "early stage"
        }
        response = generate_response("Hello", persona_mild, None)
        assert isinstance(response, str)


class TestRAGResponse:
    """Test RAGResponse dataclass."""
    
    def test_rag_response_creation(self):
        """Test creating a RAGResponse object."""
        response = RAGResponse(
            response_text="Hello, how are you?",
            retrieved_documents=[],
            confidence_score=0.8,
            persona_mood="calm",
            processing_time=0.5,
            model_used="mock"
        )
        
        assert response.response_text == "Hello, how are you?"
        assert response.confidence_score == 0.8
        assert response.persona_mood == "calm"
        assert response.processing_time == 0.5
        assert response.model_used == "mock"
        assert isinstance(response.retrieved_documents, list)


class TestIntegration:
    """Integration tests for the complete RAG pipeline."""
    
    def test_full_conversation_flow(self):
        """Test a complete conversation flow."""
        persona = {
            "name": "Margaret",
            "age": "78",
            "condition": "mild dementia",
            "personality": "kind and gentle"
        }
        
        history = []
        
        # First interaction
        response1 = generate_response("Good morning Margaret!", persona, history)
        assert isinstance(response1, str)
        
        # Add to history
        history.append({"user": "Good morning Margaret!", "assistant": response1})
        
        # Second interaction
        response2 = generate_response("How did you sleep?", persona, history)
        assert isinstance(response2, str)
    
    @pytest.mark.asyncio
    async def test_pipeline_with_persona_characteristics(self):
        """Test that pipeline respects persona characteristics."""
        pipeline = DementiaRAGPipeline()
        
        # Create persona with specific characteristics
        persona = DementiaPersona(
            "William",
            80,
            DementiaStage.MODERATE,
            personality="former musician"
        )
        
        # Mock retriever
        pipeline.retriever.search = Mock(return_value=[])
        
        response = await pipeline.generate_response(
            "Do you remember playing music?",
            persona,
            None
        )
        
        assert isinstance(response, RAGResponse)
        assert response.persona_mood in [m.value for m in MoodState]
