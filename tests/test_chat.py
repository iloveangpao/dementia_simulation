"""Tests for chat module - mock LLM to test flow."""

import pytest
import time
from unittest.mock import Mock, patch

from dementia_simulation.chat import ChatFlow, ChatMessage, MockLLM
from dementia_simulation.persona import Persona, MoodState
from dementia_simulation.retriever import MemoryRetriever, Document


class TestMockLLM:
    """Test MockLLM functionality."""
    
    def test_mock_llm_default_responses(self):
        """Test MockLLM with default responses."""
        llm = MockLLM()
        
        response1 = llm.generate_response("Hello")
        response2 = llm.generate_response("How are you?")
        
        assert isinstance(response1, str)
        assert isinstance(response2, str)
        assert response1 != response2  # Should cycle through responses
        assert llm.call_count == 2
    
    def test_mock_llm_custom_responses(self):
        """Test MockLLM with custom responses."""
        custom_responses = ["Response A", "Response B", "Response C"]
        llm = MockLLM(responses=custom_responses)
        
        responses = []
        for i in range(5):
            response = llm.generate_response(f"Query {i}")
            responses.append(response)
        
        # Should cycle through custom responses
        # Note: call_count starts at 0, so first call gives responses[1 % 3] = responses[1]
        assert responses[0] == "Response B"  # call_count=1, 1%3=1
        assert responses[1] == "Response C"  # call_count=2, 2%3=2
        assert responses[2] == "Response A"  # call_count=3, 3%3=0
        assert responses[3] == "Response B"  # call_count=4, 4%3=1
        assert responses[4] == "Response C"  # call_count=5, 5%3=2
    
    def test_mock_llm_single_response(self):
        """Test MockLLM with single response."""
        llm = MockLLM(responses=["Only response"])
        
        response1 = llm.generate_response("Query 1")
        response2 = llm.generate_response("Query 2")
        
        assert response1 == "Only response"
        assert response2 == "Only response"


class TestChatMessage:
    """Test ChatMessage class."""
    
    def test_chat_message_creation(self):
        """Test basic chat message creation."""
        timestamp = time.time()
        msg = ChatMessage("Hello world", "user", timestamp)
        
        assert msg.content == "Hello world"
        assert msg.sender == "user"
        assert msg.timestamp == timestamp
        assert msg.metadata == {}
    
    def test_chat_message_with_metadata(self):
        """Test chat message with metadata."""
        metadata = {"mood": "happy", "confidence": 0.8}
        msg = ChatMessage("Hello", "persona", time.time(), metadata=metadata)
        
        assert msg.metadata == metadata


class TestChatFlow:
    """Test ChatFlow functionality."""
    
    def test_chat_flow_initialization(self):
        """Test ChatFlow initialization."""
        persona = Persona("Alice")
        llm = MockLLM(["Test response"])
        retriever = MemoryRetriever()
        
        chat_flow = ChatFlow(persona, llm, retriever)
        
        assert chat_flow.persona == persona
        assert chat_flow.llm_provider == llm
        assert chat_flow.memory_retriever == retriever
        assert chat_flow.conversation_history == []
        assert chat_flow.context_window == 5
    
    def test_chat_flow_default_retriever(self):
        """Test ChatFlow with default retriever."""
        persona = Persona("Bob")
        llm = MockLLM()
        
        chat_flow = ChatFlow(persona, llm)
        
        assert isinstance(chat_flow.memory_retriever, MemoryRetriever)
    
    def test_build_context_prompt_basic(self):
        """Test context prompt building."""
        persona = Persona("Charlie", dementia_severity=0.6)
        persona.current_mood = MoodState.CONFUSED
        llm = MockLLM()
        
        chat_flow = ChatFlow(persona, llm)
        
        prompt = chat_flow._build_context_prompt("How are you today?")
        
        assert "Charlie" in prompt
        assert "dementia (severity: 0.6)" in prompt
        assert "confused" in prompt
        assert "How are you today?" in prompt
        assert "lose track of conversations" in prompt  # Confused behavior
    
    def test_build_context_prompt_with_history(self):
        """Test context prompt with conversation history."""
        persona = Persona("Diana")
        llm = MockLLM()
        chat_flow = ChatFlow(persona, llm)
        
        # Add conversation history
        chat_flow.conversation_history = [
            ChatMessage("Hello", "user", time.time()),
            ChatMessage("Hi there", "persona", time.time()),
            ChatMessage("How are you?", "user", time.time())
        ]
        
        prompt = chat_flow._build_context_prompt("What's your name?")
        
        assert "Recent conversation:" in prompt
        assert "user: Hello" in prompt
        assert "persona: Hi there" in prompt
        assert "user: How are you?" in prompt
    
    def test_build_context_prompt_with_memories(self):
        """Test context prompt with accessible memories."""
        persona = Persona("Eve", dementia_severity=0.3)
        persona.add_memory("I love reading books", importance=0.8)
        persona.add_memory("Books are fascinating", importance=0.9)
        
        llm = MockLLM()
        chat_flow = ChatFlow(persona, llm)
        
        # Simulate some time passing to ensure memories are accessible
        for memory in persona.memories:
            memory.timestamp = time.time() - 1800  # 30 minutes ago
        
        # Use a query that matches the memory content
        prompt = chat_flow._build_context_prompt("books")
        
        # The memories should be accessible and query should match
        accessible_memories = persona.get_accessible_memories("books")
        assert len(accessible_memories) > 0, "Memories should be accessible for this test"
        
        # Since we have accessible memories that match the query, they should be in prompt
        assert "Relevant memories you can access:" in prompt
        assert "reading books" in prompt or "Books are fascinating" in prompt
    
    @patch('time.time')
    def test_process_user_message(self, mock_time):
        """Test processing user message."""
        mock_time.return_value = 1234567890
        
        persona = Persona("Frank")
        llm = MockLLM(["I understand what you're saying."])
        chat_flow = ChatFlow(persona, llm)
        
        response = chat_flow.process_user_message("Hello, how are you?")
        
        # Check response
        assert response == "I understand what you're saying."
        
        # Check conversation history
        assert len(chat_flow.conversation_history) == 2
        assert chat_flow.conversation_history[0].content == "Hello, how are you?"
        assert chat_flow.conversation_history[0].sender == "user"
        assert chat_flow.conversation_history[1].content == "I understand what you're saying."
        assert chat_flow.conversation_history[1].sender == "persona"
        
        # Check memories were created
        assert len(persona.memories) == 2
        user_memory = next((m for m in persona.memories if "User said:" in m.content), None)
        response_memory = next((m for m in persona.memories if "I responded:" in m.content), None)
        assert user_memory is not None
        assert response_memory is not None
    
    @patch('random.random')
    def test_process_user_message_memory_forgetting(self, mock_random):
        """Test memory forgetting during conversation."""
        mock_random.return_value = 0.05  # Below 0.1 threshold for forgetting
        
        persona = Persona("Grace", dementia_severity=0.8)
        persona.add_memory("Old memory", importance=0.3)
        
        llm = MockLLM(["I see."])
        chat_flow = ChatFlow(persona, llm)
        
        initial_memory_count = len(persona.memories)
        
        with patch.object(persona, 'forget_memories', return_value=[persona.memories[0]]) as mock_forget:
            chat_flow.process_user_message("Hello")
            mock_forget.assert_called_once()
    
    def test_get_conversation_summary(self):
        """Test conversation summary generation."""
        persona = Persona("Henry", dementia_severity=0.4)
        persona.add_memory("Some memory", importance=0.7)
        persona.current_mood = MoodState.HAPPY
        
        llm = MockLLM()
        chat_flow = ChatFlow(persona, llm)
        
        # Add some conversation
        chat_flow.conversation_history = [
            ChatMessage("Hello", "user", time.time()),
            ChatMessage("Hi", "persona", time.time())
        ]
        
        summary = chat_flow.get_conversation_summary()
        
        assert summary["message_count"] == 2
        assert summary["persona_mood"] == "happy"
        assert summary["dementia_severity"] == 0.4
        assert "accessible_memories" in summary
        assert "total_memories" in summary
    
    def test_reset_conversation(self):
        """Test conversation reset."""
        persona = Persona("Iris")
        llm = MockLLM()
        chat_flow = ChatFlow(persona, llm)
        
        # Add conversation history
        chat_flow.conversation_history = [
            ChatMessage("Hello", "user", time.time()),
            ChatMessage("Hi", "persona", time.time())
        ]
        
        assert len(chat_flow.conversation_history) == 2
        
        chat_flow.reset_conversation()
        
        assert len(chat_flow.conversation_history) == 0
    
    def test_add_memory_context(self):
        """Test adding memory context documents."""
        persona = Persona("Jack")
        llm = MockLLM()
        chat_flow = ChatFlow(persona, llm)
        
        docs = [
            Document("Memory document 1"),
            Document("Memory document 2")
        ]
        
        initial_count = chat_flow.memory_retriever.get_document_count()
        chat_flow.add_memory_context(docs)
        
        assert chat_flow.memory_retriever.get_document_count() == initial_count + 2
    
    def test_simulate_memory_degradation(self):
        """Test memory degradation simulation."""
        persona = Persona("Kate", dementia_severity=0.7)
        
        # Add old memories
        old_time = time.time() - 3600  # 1 hour ago
        for i in range(5):
            persona.add_memory(f"Memory {i}", importance=0.3)
            persona.memories[-1].timestamp = old_time
        
        llm = MockLLM()
        chat_flow = ChatFlow(persona, llm)
        
        forgotten_count = chat_flow.simulate_memory_degradation()
        
        assert isinstance(forgotten_count, int)
        assert forgotten_count >= 0


class TestChatFlowMoodIntegration:
    """Test ChatFlow integration with mood system."""
    
    def test_mood_affects_context_prompt(self):
        """Test that different moods affect context prompt."""
        persona = Persona("Luna")
        llm = MockLLM()
        chat_flow = ChatFlow(persona, llm)
        
        # Test different moods
        mood_behaviors = {
            MoodState.CONFUSED: "lose track of conversations",
            MoodState.AGITATED: "frustrated or upset",
            MoodState.ANXIOUS: "worried and seek reassurance",
            MoodState.SAD: "down and may not be very responsive",
            MoodState.HAPPY: "cheerful and engaged",
            MoodState.CALM: "peaceful and speak thoughtfully"
        }
        
        for mood, expected_behavior in mood_behaviors.items():
            persona.current_mood = mood
            prompt = chat_flow._build_context_prompt("Test message")
            assert expected_behavior in prompt
    
    @patch('random.random')
    def test_conversation_triggers_mood_update(self, mock_random):
        """Test that conversation can trigger mood updates."""
        mock_random.return_value = 0.1  # Low value to force mood change
        
        persona = Persona("Max", mood_stability=0.5)
        initial_mood = persona.current_mood
        
        llm = MockLLM(["I understand."])
        chat_flow = ChatFlow(persona, llm)
        
        with patch.object(persona, 'update_mood', wraps=persona.update_mood) as mock_update:
            chat_flow.process_user_message("How are you feeling?")
            mock_update.assert_called_with(trigger_event="conversation")


class TestChatFlowIntegration:
    """Integration tests for ChatFlow."""
    
    def test_full_conversation_flow(self):
        """Test complete conversation flow."""
        persona = Persona("Nina", dementia_severity=0.5, mood_stability=0.6)
        responses = [
            "Hello there!",
            "I'm doing well, thank you.",
            "That's interesting.",
            "I need to think about that."
        ]
        llm = MockLLM(responses)
        chat_flow = ChatFlow(persona, llm)
        
        # Have a conversation
        messages = [
            "Hello, how are you?",
            "What did you do today?",
            "Do you remember your childhood?",
            "What's your favorite memory?"
        ]
        
        responses_received = []
        for message in messages:
            response = chat_flow.process_user_message(message)
            responses_received.append(response)
        
        # Verify conversation
        assert len(responses_received) == 4
        assert len(chat_flow.conversation_history) == 8  # 4 user + 4 persona messages
        assert persona.memories  # Should have created memories
        
        # Verify message alternation
        for i, msg in enumerate(chat_flow.conversation_history):
            if i % 2 == 0:
                assert msg.sender == "user"
            else:
                assert msg.sender == "persona"
                assert "mood" in msg.metadata
    
    def test_context_window_limitation(self):
        """Test that context window limits history included in prompts."""
        persona = Persona("Oscar")
        llm = MockLLM(["Response"])
        chat_flow = ChatFlow(persona, llm)
        chat_flow.context_window = 3
        
        # Add more messages than context window
        for i in range(10):
            chat_flow.conversation_history.append(
                ChatMessage(f"User message {i}", "user", time.time())
            )
            chat_flow.conversation_history.append(
                ChatMessage(f"Persona response {i}", "persona", time.time())
            )
        
        prompt = chat_flow._build_context_prompt("Current message")
        
        # Should only include last 3 messages in context (messages 17, 18, 19 from total 20)
        # Since we have 20 messages total (0-19), last 3 are indices 17, 18, 19
        # These correspond to: "Persona response 8", "User message 9", "Persona response 9"
        assert "Persona response 8" in prompt  # 2nd to last persona message  
        assert "User message 9" in prompt     # Last user message
        assert "Persona response 9" in prompt # Last persona message
        assert "User message 0" not in prompt  # Old messages excluded
        assert "User message 1" not in prompt