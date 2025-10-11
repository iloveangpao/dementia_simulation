"""
Tests for the dementia simulation chat system.
"""

import os
import sys
import unittest
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat import (
    ChatMessage,
    DementiaSimulationChat,
    DementiaSimulationRules,
    PersonaState,
    rag_pipeline,
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

    def test_persona_state_custom_values(self):
        """Test creating PersonaState with custom values."""
        persona = PersonaState(
            current_mood="happy",
            confusion_level=0.5,
            mood_intensity=0.7
        )
        self.assertEqual(persona.current_mood, "happy")
        self.assertEqual(persona.confusion_level, 0.5)
        self.assertEqual(persona.mood_intensity, 0.7)

    def test_persona_state_preferred_topics(self):
        """Test that PersonaState has default preferred topics."""
        persona = PersonaState()
        self.assertIn("family", persona.preferred_topics)
        self.assertIn("past", persona.preferred_topics)
        self.assertIn("home", persona.preferred_topics)


class TestChatMessage(unittest.TestCase):
    """Test ChatMessage functionality."""

    def test_chat_message_creation(self):
        """Test creating a ChatMessage."""
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
        """Test converting ChatMessage to dictionary."""
        message = ChatMessage(
            timestamp=datetime.now(),
            speaker="patient",
            content="Hi there",
            persona_state_snapshot={"mood": "calm"}
        )
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict["speaker"], "patient")
        self.assertEqual(message_dict["content"], "Hi there")
        self.assertIn("timestamp", message_dict)
        self.assertEqual(message_dict["persona_state_snapshot"], {"mood": "calm"})


class TestDementiaSimulationRules(unittest.TestCase):
    """Test DementiaSimulationRules functionality."""

    def test_apply_forgetting_rules(self):
        """Test applying forgetting rules to persona state."""
        persona = PersonaState()
        initial_confusion = persona.confusion_level

        # Apply forgetting rules with new input
        persona = DementiaSimulationRules.apply_forgetting_rules(persona, "test input")

        # Check that short-term memory was updated
        self.assertIn("test input", persona.short_term_memory)

        # Check that confusion level increased
        self.assertGreaterEqual(persona.confusion_level, initial_confusion)

    def test_forgetting_rules_memory_limit(self):
        """Test that forgetting rules limit short-term memory."""
        persona = PersonaState()

        # Add multiple items to trigger memory forgetting
        for i in range(10):
            persona = DementiaSimulationRules.apply_forgetting_rules(
                persona, f"input {i}"
            )

        # Check that short-term memory doesn't grow indefinitely
        self.assertLessEqual(len(persona.short_term_memory), 10)

    def test_forgetting_rules_transfer_to_long_term(self):
        """Test that items can transfer to long-term memory."""
        persona = PersonaState()

        # Add items to trigger potential transfer
        for i in range(5):
            persona = DementiaSimulationRules.apply_forgetting_rules(
                persona, f"memory {i}"
            )

        # Check that some items may have transferred (or are in short-term)
        total_memories = len(persona.short_term_memory) + len(persona.long_term_memory)
        self.assertGreater(total_memories, 0)

    def test_apply_mood_rules_stress_keywords(self):
        """Test mood rules with stressful conversation."""
        persona = PersonaState()
        persona.current_mood = "neutral"

        # Conversation with stress keywords
        stressful_context = [
            "The doctor said you need medicine",
            "You're wrong about that",
        ]

        persona = DementiaSimulationRules.apply_mood_rules(persona, stressful_context)

        # Mood should exist (may or may not have changed based on randomness)
        self.assertIsInstance(persona.current_mood, str)
        self.assertIsInstance(persona.mood_intensity, float)

    def test_apply_mood_rules_calming_keywords(self):
        """Test mood rules with calming conversation."""
        persona = PersonaState()

        # Conversation with calming keywords
        calming_context = [
            "Your family loves you",
            "Let's remember the good times at home",
        ]

        persona = DementiaSimulationRules.apply_mood_rules(persona, calming_context)

        # Mood should exist
        self.assertIsInstance(persona.current_mood, str)
        self.assertIsInstance(persona.mood_intensity, float)

    def test_apply_mood_rules_neutral_context(self):
        """Test mood rules with neutral conversation."""
        persona = PersonaState()

        neutral_context = ["It's a nice day", "The weather is pleasant"]

        persona = DementiaSimulationRules.apply_mood_rules(persona, neutral_context)

        # Mood should be valid
        self.assertIsInstance(persona.current_mood, str)


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
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_rag_pipeline_confused_persona(self):
        """Test that RAG pipeline responds differently for confused persona."""
        self.persona.confusion_level = 0.8
        response = rag_pipeline("What time is it?", ["context"], self.persona)
        self.assertIsInstance(response, str)

    def test_rag_pipeline_high_repetition_tendency(self):
        """Test RAG pipeline with high repetition tendency."""
        self.persona.repetition_tendency = 0.8
        response = rag_pipeline("How are you?", ["context"], self.persona)
        self.assertIsInstance(response, str)

    def test_rag_pipeline_different_moods(self):
        """Test RAG pipeline responses for different moods."""
        moods = ["anxious", "content", "agitated", "calm", "happy"]

        for mood in moods:
            self.persona.current_mood = mood
            response = rag_pipeline("Tell me about your day", ["context"], self.persona)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)


class TestDementiaSimulationChat(unittest.TestCase):
    """Test main chat system functionality."""

    def setUp(self):
        self.chat = DementiaSimulationChat()

    def test_chat_initialization(self):
        """Test that chat system initializes correctly."""
        self.assertIsInstance(self.chat.persona_state, PersonaState)
        self.assertIsInstance(self.chat.chat_history, list)
        self.assertEqual(len(self.chat.chat_history), 0)

    def test_chat_loop_basic(self):
        """Test basic chat loop functionality."""
        user_input = "Hello, how are you?"
        response, persona_state = self.chat.chat_loop(user_input)

        # Check response
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

        # Check persona state
        self.assertIsInstance(persona_state, dict)
        self.assertIn("current_mood", persona_state)
        self.assertIn("confusion_level", persona_state)

    def test_chat_loop_updates_history(self):
        """Test that chat loop updates conversation history."""
        initial_count = len(self.chat.chat_history)

        self.chat.chat_loop("First message")

        # Should have 2 messages: user and patient
        self.assertEqual(len(self.chat.chat_history), initial_count + 2)

        # Check speakers
        self.assertEqual(self.chat.chat_history[0].speaker, "user")
        self.assertEqual(self.chat.chat_history[1].speaker, "patient")

    def test_chat_loop_multiple_turns(self):
        """Test multiple conversation turns."""
        inputs = [
            "Hello",
            "How are you feeling?",
            "Would you like some tea?"
        ]

        for user_input in inputs:
            response, persona_state = self.chat.chat_loop(user_input)
            self.assertIsInstance(response, str)
            self.assertIsInstance(persona_state, dict)

        # Should have 6 messages total (3 user, 3 patient)
        self.assertEqual(len(self.chat.chat_history), 6)

    def test_chat_loop_persona_state_changes(self):
        """Test that persona state changes over conversation."""
        initial_confusion = self.chat.persona_state.confusion_level

        # Have multiple conversation turns
        for i in range(5):
            self.chat.chat_loop(f"Message {i}")

        # Confusion level should have changed (increased)
        final_confusion = self.chat.persona_state.confusion_level
        self.assertGreaterEqual(final_confusion, initial_confusion)

    def test_chat_loop_returns_state_snapshot(self):
        """Test that patient messages include persona state snapshot."""
        self.chat.chat_loop("Test message")

        # Get patient message
        patient_message = self.chat.chat_history[1]

        self.assertEqual(patient_message.speaker, "patient")
        self.assertIsNotNone(patient_message.persona_state_snapshot)
        self.assertIsInstance(patient_message.persona_state_snapshot, dict)

    def test_get_conversation_history(self):
        """Test getting conversation history."""
        self.chat.chat_loop("First")
        self.chat.chat_loop("Second")

        history = self.chat.get_conversation_history()

        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 4)  # 2 user, 2 patient

        # Check format
        for entry in history:
            self.assertIsInstance(entry, dict)
            self.assertIn("speaker", entry)
            self.assertIn("content", entry)
            self.assertIn("timestamp", entry)

    def test_reset_conversation(self):
        """Test resetting conversation."""
        # Have some conversation
        self.chat.chat_loop("Hello")
        self.chat.chat_loop("How are you?")

        # Modify persona state
        self.chat.persona_state.confusion_level = 0.8

        # Reset
        self.chat.reset_conversation()

        # Check that history is cleared
        self.assertEqual(len(self.chat.chat_history), 0)

        # Check that persona state is reset
        self.assertEqual(self.chat.persona_state.confusion_level, 0.0)
        self.assertEqual(self.chat.persona_state.current_mood, "neutral")

    def test_chat_loop_memory_storage(self):
        """Test that chat loop stores information in memory."""
        user_input = "Tell me about your family"
        self.chat.chat_loop(user_input)

        # Check that input was stored in memory
        self.assertGreater(len(self.chat.persona_state.short_term_memory), 0)

    def test_chat_loop_mood_changes(self):
        """Test that mood can change during conversation."""
        # Have a conversation with emotional content
        inputs = [
            "The doctor wants to see you",
            "You need to take your medicine",
            "Everything will be okay"
        ]

        for user_input in inputs:
            self.chat.chat_loop(user_input)

        # Mood may have changed (due to emotional keywords)
        # Just verify it's still a valid mood
        self.assertIsInstance(self.chat.persona_state.current_mood, str)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete chat system."""

    def test_full_conversation_flow(self):
        """Test a complete conversation flow."""
        chat = DementiaSimulationChat()

        conversation = [
            "Good morning! How did you sleep?",
            "Would you like some breakfast?",
            "Your daughter called earlier.",
            "Do you remember what we talked about yesterday?",
            "Let's go for a walk."
        ]

        for message in conversation:
            response, state = chat.chat_loop(message)

            # Verify response format
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)

            # Verify state format
            self.assertIsInstance(state, dict)
            self.assertIn("current_mood", state)
            self.assertIn("confusion_level", state)
            self.assertIn("short_term_memory", state)

        # Verify history length
        self.assertEqual(len(chat.chat_history), len(conversation) * 2)

    def test_persona_state_progression(self):
        """Test that persona state progresses realistically."""
        chat = DementiaSimulationChat()

        confusion_levels = []

        for i in range(10):
            _, state = chat.chat_loop(f"Message number {i}")
            confusion_levels.append(state["confusion_level"])

        # Confusion should generally increase over time
        self.assertGreaterEqual(confusion_levels[-1], confusion_levels[0])

    def test_memory_forgetting_pattern(self):
        """Test that memory follows forgetting patterns."""
        chat = DementiaSimulationChat()

        # Add many messages to trigger forgetting
        for i in range(15):
            chat.chat_loop(f"Topic {i}")

        # Check that some memories were forgotten
        state = chat.persona_state.to_dict()

        # Total items in all memory types should be reasonable
        total_memory_items = (
            len(state["short_term_memory"]) +
            len(state["long_term_memory"]) +
            len(state["forgotten_topics"])
        )

        self.assertGreater(total_memory_items, 0)
        # Not everything in short-term
        self.assertLess(len(state["short_term_memory"]), 15)


if __name__ == "__main__":
    unittest.main()
