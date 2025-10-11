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