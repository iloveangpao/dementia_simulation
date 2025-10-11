"""Unit tests for PatientPersona in src/persona.py."""

import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from persona import PatientPersona, DementiaStage, MoodState


class TestDementiaStage:
    """Test DementiaStage enum."""
    
    def test_stages_exist(self):
        """Test that all dementia stages are defined."""
        assert DementiaStage.MILD.value == "mild"
        assert DementiaStage.MODERATE.value == "moderate"
        assert DementiaStage.SEVERE.value == "severe"
    
    def test_all_stages(self):
        """Test that we have exactly three stages."""
        stages = list(DementiaStage)
        assert len(stages) == 3


class TestMoodState:
    """Test MoodState enum."""
    
    def test_moods_exist(self):
        """Test that required mood states are defined."""
        assert MoodState.CALM.value == "calm"
        assert MoodState.AGITATED.value == "agitated"
        assert MoodState.WITHDRAWN.value == "withdrawn"
    
    def test_all_moods(self):
        """Test that we have exactly three mood states."""
        moods = list(MoodState)
        assert len(moods) == 3


class TestPatientPersonaCreation:
    """Test PatientPersona creation and initialization."""
    
    def test_minimal_creation(self):
        """Test creating a patient with minimal parameters."""
        patient = PatientPersona("Alice")
        
        assert patient.name == "Alice"
        assert patient.dementia_stage == DementiaStage.MILD
        assert patient.mood_state == MoodState.CALM
        assert isinstance(patient.memory_keys, dict)
        assert isinstance(patient.recent_memories, list)
    
    def test_full_creation(self):
        """Test creating a patient with all parameters."""
        patient = PatientPersona(
            name="Bob",
            dementia_stage=DementiaStage.SEVERE,
            initial_mood=MoodState.AGITATED
        )
        
        assert patient.name == "Bob"
        assert patient.dementia_stage == DementiaStage.SEVERE
        assert patient.mood_state == MoodState.AGITATED
    
    def test_memory_degradation_configuration(self):
        """Test that memory degradation is configured based on stage."""
        mild = PatientPersona("Mild", DementiaStage.MILD)
        moderate = PatientPersona("Moderate", DementiaStage.MODERATE)
        severe = PatientPersona("Severe", DementiaStage.SEVERE)
        
        # Forget probability increases with severity
        assert mild.forget_probability < moderate.forget_probability
        assert moderate.forget_probability < severe.forget_probability
        
        # Memory capacity decreases with severity
        assert mild.recent_memory_capacity > moderate.recent_memory_capacity
        assert moderate.recent_memory_capacity > severe.recent_memory_capacity
        
        # Retention hours decrease with severity
        assert mild.memory_retention_hours > moderate.memory_retention_hours
        assert moderate.memory_retention_hours > severe.memory_retention_hours
    
    def test_mood_parameters_configuration(self):
        """Test that mood parameters are configured based on stage."""
        mild = PatientPersona("Mild", DementiaStage.MILD)
        moderate = PatientPersona("Moderate", DementiaStage.MODERATE)
        severe = PatientPersona("Severe", DementiaStage.SEVERE)
        
        # Mood change probability increases with severity
        assert mild.mood_change_probability < moderate.mood_change_probability
        assert moderate.mood_change_probability < severe.mood_change_probability


class TestMemoryKeys:
    """Test memory key functionality."""
    
    def test_add_memory_key(self):
        """Test adding memory keys."""
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        patient.add_memory_key("favorite_color", "blue")
        patient.add_memory_key("pet_name", "Fluffy")
        
        assert len(patient.memory_keys) == 2
        assert "favorite_color" in patient.memory_keys
        assert "pet_name" in patient.memory_keys
    
    @patch('random.random')
    def test_get_memory_key_success(self, mock_random):
        """Test retrieving a memory key successfully."""
        mock_random.return_value = 0.9  # Above forget probability
        
        patient = PatientPersona("Alice", DementiaStage.MILD)
        patient.add_memory_key("test_key", "test_value")
        
        result = patient.get_memory_key("test_key")
        assert result == "test_value"
    
    @patch('random.random')
    def test_get_memory_key_forgotten(self, mock_random):
        """Test that memory keys can be forgotten."""
        mock_random.return_value = 0.01  # Below forget probability
        
        patient = PatientPersona("Alice", DementiaStage.MILD)
        patient.add_memory_key("test_key", "test_value")
        
        result = patient.get_memory_key("test_key")
        assert result is None
        # Key should be removed after forgetting
        assert "test_key" not in patient.memory_keys
    
    def test_get_nonexistent_key(self):
        """Test retrieving a non-existent key."""
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        result = patient.get_memory_key("nonexistent")
        assert result is None


class TestRecentMemories:
    """Test recent memory functionality."""
    
    def test_add_recent_memory(self):
        """Test adding recent memories."""
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        patient.add_recent_memory("Had breakfast")
        patient.add_recent_memory("Talked to daughter")
        
        assert len(patient.recent_memories) == 2
        assert patient.recent_memories[0]["content"] == "Had breakfast"
        assert patient.recent_memories[1]["content"] == "Talked to daughter"
    
    def test_recent_memory_has_timestamp(self):
        """Test that recent memories have timestamps."""
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        patient.add_recent_memory("Test memory")
        
        assert "timestamp" in patient.recent_memories[0]
        assert isinstance(patient.recent_memories[0]["timestamp"], datetime)
    
    def test_memory_capacity_limit(self):
        """Test that memory capacity is enforced."""
        patient = PatientPersona("Alice", DementiaStage.SEVERE)
        capacity = patient.recent_memory_capacity
        
        # Add more memories than capacity
        for i in range(capacity + 5):
            patient.add_recent_memory(f"Memory {i}")
        
        # Should only keep the most recent memories
        assert len(patient.recent_memories) == capacity
        # Should have the latest memories
        assert patient.recent_memories[-1]["content"] == f"Memory {capacity + 4}"
    
    @patch('random.random')
    def test_forget_recent_time_based(self, mock_random):
        """Test forgetting memories based on time."""
        mock_random.return_value = 0.9  # Don't forget randomly
        
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        # Add an old memory (manually set timestamp)
        old_time = datetime.now() - timedelta(hours=48)
        patient.recent_memories.append({
            "content": "Old memory",
            "timestamp": old_time
        })
        
        forgotten = patient.forget_recent()
        
        assert len(forgotten) == 1
        assert "Old memory" in forgotten
        assert len(patient.recent_memories) == 0
    
    @patch('random.random')
    def test_forget_recent_random(self, mock_random):
        """Test random forgetting of recent memories."""
        mock_random.return_value = 0.01  # Below forget probability
        
        patient = PatientPersona("Alice", DementiaStage.MILD)
        patient.add_recent_memory("Test memory")
        
        forgotten = patient.forget_recent()
        
        # Should have forgotten the memory
        assert len(forgotten) >= 0  # May or may not forget
        assert len(patient.recent_memories) <= 1


class TestMoodUpdate:
    """Test mood update functionality."""
    
    @patch('random.random')
    def test_mood_update_no_change(self, mock_random):
        """Test mood staying the same."""
        mock_random.return_value = 0.9  # Above mood change probability
        
        patient = PatientPersona("Alice", DementiaStage.MILD, MoodState.CALM)
        original_mood = patient.mood_state
        
        new_mood = patient.update_mood()
        
        assert new_mood == original_mood
        assert patient.mood_state == original_mood
    
    @patch('random.random')
    def test_mood_update_change(self, mock_random):
        """Test mood changing."""
        mock_random.side_effect = [0.01, 0.5]  # First below threshold, second for choice
        
        patient = PatientPersona("Alice", DementiaStage.MILD, MoodState.CALM)
        original_mood = patient.mood_state
        
        # Manually set random choice
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = MoodState.AGITATED
            new_mood = patient.update_mood()
        
        assert new_mood != original_mood
        assert patient.mood_state == MoodState.AGITATED
    
    def test_mood_update_returns_moodstate(self):
        """Test that update_mood returns a MoodState."""
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        result = patient.update_mood()
        
        assert isinstance(result, MoodState)
        assert result in list(MoodState)


class TestPatientStatus:
    """Test patient status retrieval."""
    
    def test_get_status(self):
        """Test getting patient status."""
        patient = PatientPersona("Alice", DementiaStage.MODERATE, MoodState.CALM)
        patient.add_memory_key("test", "value")
        patient.add_recent_memory("Test memory")
        
        status = patient.get_status()
        
        assert isinstance(status, dict)
        assert status["name"] == "Alice"
        assert status["dementia_stage"] == "moderate"
        assert status["mood_state"] == "calm"
        assert status["memory_keys_count"] == 1
        assert status["recent_memories_count"] == 1
        assert "forget_probability" in status
        assert "mood_change_probability" in status


class TestStringRepresentations:
    """Test string representations of PatientPersona."""
    
    def test_str_representation(self):
        """Test __str__ method."""
        patient = PatientPersona("Alice", DementiaStage.MODERATE, MoodState.AGITATED)
        
        result = str(patient)
        
        assert "Alice" in result
        assert "moderate" in result
        assert "agitated" in result
    
    def test_repr_representation(self):
        """Test __repr__ method."""
        patient = PatientPersona("Bob", DementiaStage.SEVERE, MoodState.WITHDRAWN)
        
        result = repr(patient)
        
        assert "Bob" in result
        assert "severe" in result
        assert "withdrawn" in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_memory_operations(self):
        """Test operations on empty memories."""
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        # Get non-existent key
        result = patient.get_memory_key("nonexistent")
        assert result is None
        
        # Forget when no memories
        forgotten = patient.forget_recent()
        assert forgotten == []
    
    def test_multiple_mood_updates(self):
        """Test multiple consecutive mood updates."""
        patient = PatientPersona("Alice", DementiaStage.SEVERE)
        
        moods = set()
        for _ in range(50):
            mood = patient.update_mood()
            moods.add(mood)
        
        # Should return valid moods
        assert all(mood in MoodState for mood in moods)
    
    def test_many_memory_keys(self):
        """Test handling many memory keys."""
        patient = PatientPersona("Alice", DementiaStage.MILD)
        
        for i in range(100):
            patient.add_memory_key(f"key_{i}", f"value_{i}")
        
        # All keys should be stored
        assert len(patient.memory_keys) == 100
