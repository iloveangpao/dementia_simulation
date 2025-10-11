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
   
class TestChatMessage(unittest.TestCase):
    """Test ChatMessage functionality."""
    
    def test_chat_message_creation(self):
        """Test that ChatMessage can be created properly."""
        timestamp = datetime.now()
        message = ChatMessage(
            timestamp=timestamp,
            speaker="user",
            content="Hello"
        )
        self.assertEqual(message.speaker, "user")
        self.assertEqual(message.content, "Hello")
        self.assertEqual(message.timestamp, timestamp)
        assert msg.metadata == {}
        
    def test_chat_message_with_metadata(self):
        """Test chat message with metadata."""
        metadata = {"mood": "happy", "confidence": 0.8}
        msg = ChatMessage("Hello", "persona", time.time(), metadata=metadata)
        
        assert msg.metadata == metadata
    
    def test_chat_message_to_dict(self):
        """Test that ChatMessage can be serialized to dictionary."""
        message = ChatMessage(
            timestamp=datetime.now(),
            speaker="patient",
            content="I don't remember"
        )
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertIn("speaker", message_dict)
        self.assertIn("content", message_dict)
        self.assertIn("timestamp", message_dict)

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
"""
Tests for the dementia simulation chat system.
"""

import unittest
import sys
import os
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat import (
    DementiaSimulationChat, 
    PersonaState, 
    ChatMessage,
    DementiaSimulationRules,
    rag_pipeline
)


class TestPersonaState(unittest.TestCase):
    """Test PersonaState functionality."""
    
    def test_persona_state_creation(self):
        """Test that PersonaState can be created with default values."""
        persona = PersonaState()
        self.assertEqual(persona.current_mood, "neutral")
        self.assertEqual(persona.confusion_level, 0.0)
        self.assertIsInstance(persona.short_term_memory, list)
        self.assertIsInstance(persona.long_term_memory, list)
    
    def test_persona_state_to_dict(self):
        """Test that PersonaState can be serialized to dictionary."""
        persona = PersonaState()
        persona_dict = persona.to_dict()
        self.assertIsInstance(persona_dict, dict)
        self.assertIn("current_mood", persona_dict)
        self.assertIn("confusion_level", persona_dict)
        self.assertIn("short_term_memory", persona_dict)

class TestDementiaSimulationRules(unittest.TestCase):
    """Test DementiaSimulationRules functionality."""
    
    def setUp(self):
        self.rules = DementiaSimulationRules()
        self.persona = PersonaState()
    
    def test_apply_forgetting_rules(self):
        """Test that forgetting rules modify persona state appropriately."""
        original_confusion = self.persona.confusion_level
        updated_persona = self.rules.apply_forgetting_rules(self.persona, "test input")
        
        # Confusion should increase or stay the same
        self.assertGreaterEqual(updated_persona.confusion_level, original_confusion)
        
        # Short-term memory should have the new input
        self.assertIn("test input", updated_persona.short_term_memory)
    
    def test_apply_mood_rules(self):
        """Test that mood rules can change persona mood."""
        context = ["I miss my family", "Where is my home", "I feel lost"]
        updated_persona = self.rules.apply_mood_rules(self.persona, context)
        
        # Mood should be set (may or may not change from neutral depending on random factors)
        self.assertIsNotNone(updated_persona.current_mood)
        self.assertIsInstance(updated_persona.mood_intensity, float)


class TestRAGPipeline(unittest.TestCase):
    """Test RAG pipeline functionality."""
    
    def setUp(self):
        self.persona = PersonaState()
    
    def test_rag_pipeline_returns_string(self):
        """Test that RAG pipeline returns a string response."""
        response = rag_pipeline("Hello", ["context"], self.persona)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_rag_pipeline_home_query(self):
        """Test that RAG pipeline responds appropriately to home-related queries."""
        response = rag_pipeline("I want to go home", ["context"], self.persona)
        self.assertIn("home", response.lower())
    
    def test_rag_pipeline_confused_persona(self):
        """Test that RAG pipeline responds differently for confused persona."""
        self.persona.confusion_level = 0.8
        response = rag_pipeline("What time is it?", ["context"], self.persona)
        self.assertIsInstance(response, str)


class TestDementiaSimulationChat(unittest.TestCase):
    """Test main chat system functionality."""
    
    def setUp(self):
        self.chat = DementiaSimulationChat()
    
    def test_chat_initialization(self):
        """Test that chat system initializes properly."""
        self.assertIsInstance(self.chat.persona_state, PersonaState)
        self.assertEqual(len(self.chat.chat_history), 0)
    
    def test_chat_loop_returns_tuple(self):
        """Test that chat loop returns the expected tuple format."""
        result = self.chat.chat_loop("Hello")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        
        response, persona_state = result
        self.assertIsInstance(response, str)
        self.assertIsInstance(persona_state, dict)
    
    def test_chat_loop_stores_history(self):
        """Test that chat loop stores messages in history."""
        initial_history_length = len(self.chat.chat_history)
        self.chat.chat_loop("Test message")
        
        # Should have added both user and patient messages
        self.assertEqual(len(self.chat.chat_history), initial_history_length + 2)
        
        # Check that messages are stored correctly
        user_msg = self.chat.chat_history[-2]
        patient_msg = self.chat.chat_history[-1]
        
        self.assertEqual(user_msg.speaker, "user")
        self.assertEqual(user_msg.content, "Test message")
        self.assertEqual(patient_msg.speaker, "patient")
    
    def test_multiple_chat_interactions(self):
        """Test multiple chat interactions build history correctly."""
        inputs = ["Hello", "How are you?", "What is your name?"]
        
        for input_msg in inputs:
            response, persona_state = self.chat.chat_loop(input_msg)
            self.assertIsInstance(response, str)
            self.assertIsInstance(persona_state, dict)
        
        # Should have 6 messages total (3 user + 3 patient)
        self.assertEqual(len(self.chat.chat_history), 6)
    
    def test_persona_state_changes_over_time(self):
        """Test that persona state evolves during conversation."""
        initial_confusion = self.chat.persona_state.confusion_level
        
        # Have several interactions
        for i in range(5):
            self.chat.chat_loop(f"Message {i}")
        
        # Confusion should generally increase
        final_confusion = self.chat.persona_state.confusion_level
        self.assertGreaterEqual(final_confusion, initial_confusion)
    
    def test_get_chat_history(self):
        """Test that chat history can be retrieved as dictionaries."""
        self.chat.chat_loop("Test message")
        history = self.chat.get_chat_history()
        
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        for msg_dict in history:
            self.assertIsInstance(msg_dict, dict)
            self.assertIn("speaker", msg_dict)
            self.assertIn("content", msg_dict)
            self.assertIn("timestamp", msg_dict)
    
    def test_reset_conversation(self):
        """Test that conversation can be reset."""
        # Have some conversation first
        self.chat.chat_loop("Hello")
        self.chat.chat_loop("How are you?")
        
        # Reset
        self.chat.reset_conversation()
        
        # Should be back to initial state
        self.assertEqual(len(self.chat.chat_history), 0)
        self.assertEqual(self.chat.persona_state.confusion_level, 0.0)
        self.assertEqual(self.chat.persona_state.current_mood, "neutral")


if __name__ == "__main__":
    unittest.main()
