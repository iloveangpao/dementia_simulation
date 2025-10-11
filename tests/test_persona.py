"""Tests for persona module - memory forgetting and mood update rules."""

import pytest
import time
import random
from unittest.mock import patch

from dementia_simulation.persona import Persona, Memory, MoodState


class TestMemoryForgetting:
    """Test memory forgetting functionality."""
    
    def test_memory_creation(self):
        """Test basic memory creation."""
        persona = Persona("Alice", dementia_severity=0.5)
        persona.add_memory("I had breakfast this morning", importance=0.8)
        
        assert len(persona.memories) == 1
        assert persona.memories[0].content == "I had breakfast this morning"
        assert persona.memories[0].importance == 0.8
        assert persona.memories[0].memory_type == "general"
    
    def test_memory_age_calculation(self):
        """Test memory age calculation."""
        timestamp = time.time() - 3600  # 1 hour ago
        memory = Memory("Old memory", 0.5, timestamp)
        
        age = memory.age_in_seconds()
        assert age >= 3600  # Should be at least 1 hour
        assert age < 3700   # But not much more
    
    @patch('random.random')
    def test_forget_memories_high_dementia(self, mock_random):
        """Test memory forgetting with high dementia severity."""
        # With high dementia (0.9), old memories (2 hours), and varying importance:
        # Important (0.9): forget_prob = 1.0*0.4 + 0.1*0.3 + 0.9*0.3 = 0.70
        # Medium (0.5): forget_prob = 1.0*0.4 + 0.5*0.3 + 0.9*0.3 = 0.82  
        # Unimportant (0.1): forget_prob = 1.0*0.4 + 0.9*0.3 + 0.9*0.3 = 0.94
        
        persona = Persona("Bob", dementia_severity=0.9)
        
        # Add memories with different importance levels
        base_time = time.time() - 7200  # 2 hours ago
        persona.memories = [
            Memory("Important memory", 0.9, base_time, "important"),
            Memory("Medium memory", 0.5, base_time, "medium"), 
            Memory("Unimportant memory", 0.1, base_time, "low")
        ]
        
        # Test with values that should keep memories based on probabilities
        mock_random.side_effect = [0.8, 0.9, 0.95]  # > 0.70, > 0.82, > 0.94
        forgotten = persona.forget_memories(time_threshold=3600)
        
        # All should be kept
        assert len(forgotten) == 0
        assert len(persona.memories) == 3
        
        # Reset memories
        persona.memories = [
            Memory("Important memory", 0.9, base_time, "important"),
            Memory("Medium memory", 0.5, base_time, "medium"), 
            Memory("Unimportant memory", 0.1, base_time, "low")
        ]
        
        # Test with values that should forget memories
        mock_random.side_effect = [0.6, 0.7, 0.8]  # < 0.70, < 0.82, < 0.94
        forgotten = persona.forget_memories(time_threshold=3600)
        
        # All should be forgotten
        assert len(forgotten) == 3
        assert len(persona.memories) == 0
    
    @patch('random.random')
    def test_forget_memories_low_dementia(self, mock_random):
        """Test memory forgetting with low dementia severity."""
        mock_random.side_effect = [0.8, 0.9, 0.8]  # High values, less forgetting
        
        persona = Persona("Carol", dementia_severity=0.1)
        
        # Add recent memories
        recent_time = time.time() - 1800  # 30 minutes ago
        persona.memories = [
            Memory("Recent important memory", 0.9, recent_time),
            Memory("Recent medium memory", 0.5, recent_time),
            Memory("Recent low memory", 0.2, recent_time)
        ]
        
        forgotten = persona.forget_memories(time_threshold=3600)
        
        # With low dementia and recent memories, should forget less
        assert len(forgotten) == 0
        assert len(persona.memories) == 3
    
    def test_forget_memories_importance_factor(self):
        """Test that importance affects forgetting probability."""
        persona = Persona("Dave", dementia_severity=0.5)
        
        # Add many memories to test statistical behavior
        base_time = time.time() - 7200  # 2 hours ago
        for i in range(50):
            if i < 25:
                persona.add_memory(f"Important memory {i}", importance=0.9)
            else:
                persona.add_memory(f"Unimportant memory {i}", importance=0.1)
        
        # Set timestamps manually
        for memory in persona.memories:
            memory.timestamp = base_time
        
        forgotten = persona.forget_memories(time_threshold=3600)
        
        # Count forgotten memories by importance
        forgotten_important = sum(1 for m in forgotten if m.importance == 0.9)
        forgotten_unimportant = sum(1 for m in forgotten if m.importance == 0.1)
        
        # Should forget more unimportant memories
        assert forgotten_unimportant > forgotten_important
    
    def test_get_accessible_memories(self):
        """Test memory accessibility based on dementia severity."""
        persona = Persona("Eve", dementia_severity=0.6)
        
        # Add memories with different importance
        persona.add_memory("Very important", importance=0.9)
        persona.add_memory("Somewhat important", importance=0.6)
        persona.add_memory("Not important", importance=0.2)
        
        accessible = persona.get_accessible_memories()
        
        # With moderate dementia, should have some accessible memories
        assert len(accessible) > 0
        assert len(accessible) <= 3
    
    def test_get_accessible_memories_with_query(self):
        """Test querying specific memories."""
        persona = Persona("Frank", dementia_severity=0.3)
        
        persona.add_memory("I love eating apples", importance=0.8)
        persona.add_memory("The weather is nice today", importance=0.7)
        persona.add_memory("Apples are my favorite fruit", importance=0.9)
        
        apple_memories = persona.get_accessible_memories("apple")
        
        assert len(apple_memories) == 2
        assert all("apple" in m.content.lower() for m in apple_memories)


class TestMoodUpdate:
    """Test mood update functionality."""
    
    def test_initial_mood(self):
        """Test default mood initialization."""
        persona = Persona("Grace")
        assert persona.current_mood == MoodState.CALM
        assert persona.mood_stability == 0.7
    
    @patch('random.random')
    def test_mood_update_stable_persona(self, mock_random):
        """Test mood updates with high stability."""
        mock_random.return_value = 0.8  # High value, no mood change
        
        persona = Persona("Helen", mood_stability=0.9, dementia_severity=0.2)
        initial_mood = persona.current_mood
        
        new_mood = persona.update_mood()
        
        # Should maintain same mood with high stability
        assert new_mood == initial_mood
    
    @patch('random.random')
    @patch('random.choices')
    def test_mood_update_unstable_persona(self, mock_choices, mock_random):
        """Test mood updates with low stability."""
        mock_random.return_value = 0.1  # Low value, should change mood
        mock_choices.return_value = [MoodState.CONFUSED]
        
        persona = Persona("Ian", mood_stability=0.1, dementia_severity=0.8)
        initial_mood = persona.current_mood
        
        new_mood = persona.update_mood()
        
        # Should change mood with low stability and high dementia
        assert new_mood == MoodState.CONFUSED
    
    @patch('random.random')
    @patch('random.choices')
    def test_mood_update_with_trigger(self, mock_choices, mock_random):
        """Test mood updates with trigger events."""
        mock_random.return_value = 0.3  # Moderate value
        mock_choices.return_value = [MoodState.ANXIOUS]
        
        persona = Persona("Jane", mood_stability=0.8, dementia_severity=0.3)
        
        # Trigger event should increase change probability
        new_mood = persona.update_mood(trigger_event="stressful_situation")
        
        # Should be more likely to change mood with trigger
        assert new_mood == MoodState.ANXIOUS
    
    @patch('random.choices')
    def test_mood_weights_high_dementia(self, mock_choices):
        """Test mood selection weights for high dementia."""
        mock_choices.return_value = [MoodState.CONFUSED]
        
        persona = Persona("Ken", dementia_severity=0.8)
        
        # Force mood change by setting random to low value
        with patch('random.random', return_value=0.1):
            persona.update_mood()
        
        # Should have been called with weights favoring confused/agitated states
        mock_choices.assert_called_once()
        call_args = mock_choices.call_args
        moods = call_args[0][0]
        weights = call_args[1]['weights']
        
        # Find weights for confused and happy states
        confused_weight = weights[moods.index(MoodState.CONFUSED)]
        happy_weight = weights[moods.index(MoodState.HAPPY)]
        
        # Confused should have higher weight than happy for high dementia
        assert confused_weight > happy_weight
    
    @patch('random.choices')
    def test_mood_weights_low_dementia(self, mock_choices):
        """Test mood selection weights for low dementia."""
        mock_choices.return_value = [MoodState.CALM]
        
        persona = Persona("Linda", dementia_severity=0.1)
        
        # Force mood change
        with patch('random.random', return_value=0.1):
            persona.update_mood()
        
        mock_choices.assert_called_once()
        call_args = mock_choices.call_args
        moods = call_args[0][0]
        weights = call_args[1]['weights']
        
        # Find weights for calm and confused states
        calm_weight = weights[moods.index(MoodState.CALM)]
        confused_weight = weights[moods.index(MoodState.CONFUSED)]
        
        # Calm should have higher weight than confused for low dementia
        assert calm_weight > confused_weight
    
    def test_mood_stability_affects_change_probability(self):
        """Test that mood stability affects change probability."""
        # Create two personas with different stability
        stable_persona = Persona("Mike", mood_stability=0.9, dementia_severity=0.5)
        unstable_persona = Persona("Nancy", mood_stability=0.1, dementia_severity=0.5)
        
        # Track mood changes over multiple updates
        stable_changes = 0
        unstable_changes = 0
        
        for _ in range(100):
            old_stable_mood = stable_persona.current_mood
            old_unstable_mood = unstable_persona.current_mood
            
            stable_persona.update_mood()
            unstable_persona.update_mood()
            
            if stable_persona.current_mood != old_stable_mood:
                stable_changes += 1
            if unstable_persona.current_mood != old_unstable_mood:
                unstable_changes += 1
        
        # Unstable persona should change mood more often
        assert unstable_changes > stable_changes


class TestPersonaIntegration:
    """Integration tests for persona functionality."""
    
    def test_persona_lifecycle(self):
        """Test a complete persona lifecycle with memory and mood changes."""
        persona = Persona("Oliver", dementia_severity=0.4, mood_stability=0.6)
        
        # Add various memories
        persona.add_memory("My daughter visited yesterday", importance=0.9, memory_type="family")
        persona.add_memory("I had coffee this morning", importance=0.5, memory_type="daily")
        persona.add_memory("The TV show was boring", importance=0.2, memory_type="entertainment")
        
        initial_memory_count = len(persona.memories)
        initial_mood = persona.current_mood
        
        # Simulate time passing and forgetting
        for memory in persona.memories:
            memory.timestamp = time.time() - 5400  # 1.5 hours ago
        
        forgotten = persona.forget_memories(time_threshold=3600)
        accessible = persona.get_accessible_memories()
        
        # Update mood
        new_mood = persona.update_mood()
        
        # Verify system behavior
        assert len(persona.memories) <= initial_memory_count
        assert len(accessible) <= len(persona.memories)
        assert new_mood in MoodState
        
        # Important family memory should be more likely to be retained
        family_memories = [m for m in persona.memories if m.memory_type == "family"]
        assert len(family_memories) <= 1  # At most the original family memory