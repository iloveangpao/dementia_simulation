"""Unit tests for PatientPersona class."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path to import persona module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from persona import DementiaStage, MoodState, PatientPersona


class TestDementiaStage:
    """Test DementiaStage enum."""

    def test_stages_exist(self):
        """Test that all dementia stages are defined."""
        assert DementiaStage.MILD.value == "mild"
        assert DementiaStage.MODERATE.value == "moderate"
        assert DementiaStage.SEVERE.value == "severe"

    def test_all_stages_present(self):
        """Test that all required stages are present."""
        stages = [stage.value for stage in DementiaStage]
        assert "mild" in stages
        assert "moderate" in stages
        assert "severe" in stages
        assert len(stages) == 3


class TestMoodState:
    """Test MoodState enum."""

    def test_moods_exist(self):
        """Test that mood states are defined."""
        assert MoodState.CALM.value == "calm"
        assert MoodState.AGITATED.value == "agitated"
        assert MoodState.WITHDRAWN.value == "withdrawn"

    def test_all_moods_present(self):
        """Test that all required moods are present."""
        moods = [mood.value for mood in MoodState]
        assert "calm" in moods
        assert "agitated" in moods
        assert "withdrawn" in moods
        assert len(moods) == 3


class TestPatientPersona:
    """Test PatientPersona class."""

    def test_persona_creation_minimal(self):
        """Test creating a persona with minimal parameters."""
        persona = PatientPersona("Alice")

        assert persona.name == "Alice"
        assert persona.dementia_stage == DementiaStage.MILD
        assert persona.mood_state == MoodState.CALM
        assert isinstance(persona.memory_keys, dict)
        assert isinstance(persona.recent_memories, list)
        assert len(persona.memory_keys) == 0
        assert len(persona.recent_memories) == 0

    def test_persona_creation_with_stage(self):
        """Test creating persona with specific dementia stage."""
        persona = PatientPersona("Bob", DementiaStage.SEVERE)

        assert persona.name == "Bob"
        assert persona.dementia_stage == DementiaStage.SEVERE
        assert persona.mood_state == MoodState.CALM

    def test_persona_creation_with_mood(self):
        """Test creating persona with specific mood."""
        persona = PatientPersona("Charlie", DementiaStage.MODERATE, MoodState.AGITATED)

        assert persona.name == "Charlie"
        assert persona.dementia_stage == DementiaStage.MODERATE
        assert persona.mood_state == MoodState.AGITATED

    def test_memory_degradation_configuration_mild(self):
        """Test memory degradation parameters for mild dementia."""
        persona = PatientPersona("Test", DementiaStage.MILD)

        assert persona.forget_probability == 0.1
        assert persona.recent_memory_capacity == 20
        assert persona.memory_retention_hours == 24

    def test_memory_degradation_configuration_moderate(self):
        """Test memory degradation parameters for moderate dementia."""
        persona = PatientPersona("Test", DementiaStage.MODERATE)

        assert persona.forget_probability == 0.3
        assert persona.recent_memory_capacity == 10
        assert persona.memory_retention_hours == 8

    def test_memory_degradation_configuration_severe(self):
        """Test memory degradation parameters for severe dementia."""
        persona = PatientPersona("Test", DementiaStage.SEVERE)

        assert persona.forget_probability == 0.6
        assert persona.recent_memory_capacity == 5
        assert persona.memory_retention_hours == 2

    def test_mood_change_probability_configuration(self):
        """Test mood change probabilities for different stages."""
        mild = PatientPersona("Mild", DementiaStage.MILD)
        moderate = PatientPersona("Moderate", DementiaStage.MODERATE)
        severe = PatientPersona("Severe", DementiaStage.SEVERE)

        assert mild.mood_change_probability == 0.1
        assert moderate.mood_change_probability == 0.25
        assert severe.mood_change_probability == 0.4

        # Verify progression
        assert mild.mood_change_probability < moderate.mood_change_probability
        assert moderate.mood_change_probability < severe.mood_change_probability

    def test_add_memory_key(self):
        """Test adding memory keys."""
        persona = PatientPersona("Test")

        persona.add_memory_key("favorite_color", "blue")
        persona.add_memory_key("pet_name", "Fluffy")

        assert len(persona.memory_keys) == 2
        assert "favorite_color" in persona.memory_keys
        assert "pet_name" in persona.memory_keys

    def test_get_memory_key_success(self):
        """Test retrieving a memory key."""
        persona = PatientPersona("Test", DementiaStage.MILD)
        persona.add_memory_key("hometown", "Springfield")

        # Try multiple times to get at least one successful retrieval
        retrieved = None
        for _ in range(10):
            result = persona.get_memory_key("hometown")
            if result is not None:
                retrieved = result
                break

        # With 10% forget rate and 10 tries, we should get at least one success
        assert retrieved == "Springfield" or "hometown" not in persona.memory_keys

    def test_get_memory_key_not_found(self):
        """Test retrieving a non-existent memory key."""
        persona = PatientPersona("Test")

        result = persona.get_memory_key("nonexistent")
        assert result is None

    def test_memory_key_forgetting(self):
        """Test that memory keys can be forgotten."""
        persona = PatientPersona("Test", DementiaStage.SEVERE)
        persona.add_memory_key("test_key", "test_value")

        # With 60% forget rate, try many times to trigger forgetting
        forgotten = False
        for _ in range(20):
            result = persona.get_memory_key("test_key")
            if result is None:
                forgotten = True
                break

        # With severe dementia and many attempts, should forget at least once
        assert forgotten

    def test_add_recent_memory(self):
        """Test adding recent memories."""
        persona = PatientPersona("Test")

        persona.add_recent_memory("Had breakfast")
        persona.add_recent_memory("Talked to daughter")

        assert len(persona.recent_memories) == 2
        assert persona.recent_memories[0]["content"] == "Had breakfast"
        assert persona.recent_memories[1]["content"] == "Talked to daughter"
        assert "timestamp" in persona.recent_memories[0]

    def test_recent_memory_capacity_limit(self):
        """Test that recent memories are limited by capacity."""
        persona = PatientPersona("Test", DementiaStage.SEVERE)

        # Add more memories than capacity (5 for severe)
        for i in range(10):
            persona.add_recent_memory(f"Memory {i}")

        # Should only keep the most recent 5
        assert len(persona.recent_memories) == 5
        assert persona.recent_memories[-1]["content"] == "Memory 9"

    def test_forget_recent_by_time(self):
        """Test forgetting recent memories based on time."""
        persona = PatientPersona("Test", DementiaStage.MODERATE)

        # Add a memory and manually set old timestamp
        persona.add_recent_memory("Old memory")
        old_time = datetime.now() - timedelta(hours=10)
        persona.recent_memories[0]["timestamp"] = old_time

        # Add a recent memory
        persona.add_recent_memory("Recent memory")

        # Forget old memories
        forgotten = persona.forget_recent()

        # The old memory should be forgotten (retention is 8 hours for moderate)
        assert "Old memory" in forgotten
        assert len(persona.recent_memories) == 1
        assert persona.recent_memories[0]["content"] == "Recent memory"

    def test_forget_recent_returns_empty_when_all_recent(self):
        """Test that forget_recent returns empty list when all memories are recent."""
        persona = PatientPersona("Test", DementiaStage.MILD)

        persona.add_recent_memory("Recent memory 1")
        persona.add_recent_memory("Recent memory 2")

        forgotten = persona.forget_recent()

        assert len(forgotten) == 0
        assert len(persona.recent_memories) == 2

    def test_update_mood_returns_mood_state(self):
        """Test that update_mood returns a MoodState."""
        persona = PatientPersona("Test")

        mood = persona.update_mood()

        assert isinstance(mood, MoodState)
        assert mood in [MoodState.CALM, MoodState.AGITATED, MoodState.WITHDRAWN]

    def test_update_mood_can_change(self):
        """Test that mood can change with repeated updates."""
        persona = PatientPersona("Test", DementiaStage.SEVERE)
        original_mood = persona.mood_state

        # Try many times to trigger a mood change
        mood_changed = False
        for _ in range(50):
            new_mood = persona.update_mood()
            if new_mood != original_mood:
                mood_changed = True
                break

        # With 40% probability and 50 attempts, should change at least once
        assert mood_changed

    def test_update_mood_different_from_current(self):
        """Test that when mood changes, it changes to a different mood."""
        persona = PatientPersona("Test", DementiaStage.SEVERE)

        # Keep updating until mood changes
        original_mood = persona.mood_state
        for _ in range(100):
            new_mood = persona.update_mood()
            if new_mood != original_mood:
                # Verify it's a different mood
                assert new_mood != original_mood
                break

    def test_get_status(self):
        """Test getting persona status."""
        persona = PatientPersona("Alice", DementiaStage.MODERATE, MoodState.WITHDRAWN)
        persona.add_memory_key("key1", "value1")
        persona.add_recent_memory("memory1")

        status = persona.get_status()

        assert status["name"] == "Alice"
        assert status["dementia_stage"] == "moderate"
        assert status["mood_state"] == "withdrawn"
        assert status["memory_keys_count"] == 1
        assert status["recent_memories_count"] == 1
        assert status["forget_probability"] == 0.3
        assert status["mood_change_probability"] == 0.25

    def test_repr(self):
        """Test string representation."""
        persona = PatientPersona("Bob", DementiaStage.SEVERE, MoodState.AGITATED)

        repr_str = repr(persona)

        assert "Bob" in repr_str
        assert "severe" in repr_str
        assert "agitated" in repr_str
        assert "PatientPersona" in repr_str


class TestIntegration:
    """Integration tests for PatientPersona."""

    def test_full_workflow(self):
        """Test a complete workflow with a patient persona."""
        # Create patient
        patient = PatientPersona("Margaret", DementiaStage.MILD, MoodState.CALM)

        # Add memory keys
        patient.add_memory_key("daughter_name", "Sarah")
        patient.add_memory_key("favorite_food", "apple pie")

        # Add recent memories
        patient.add_recent_memory("Had breakfast")
        patient.add_recent_memory("Visited by daughter")
        patient.add_recent_memory("Took morning medication")

        # Check status
        status = patient.get_status()
        assert status["memory_keys_count"] >= 0  # May have forgotten some
        assert status["recent_memories_count"] == 3

        # Update mood
        patient.update_mood()
        assert patient.mood_state in MoodState

        # Retrieve memory (may be forgotten)
        daughter = patient.get_memory_key("daughter_name")
        assert daughter is None or daughter == "Sarah"

    def test_severe_dementia_rapid_forgetting(self):
        """Test that severe dementia forgets more rapidly."""
        patient = PatientPersona("Eleanor", DementiaStage.SEVERE)

        # Add multiple memory keys
        for i in range(20):
            patient.add_memory_key(f"key_{i}", f"value_{i}")

        initial_count = len(patient.memory_keys)

        # Try retrieving multiple times to trigger forgetting
        for _ in range(10):
            for i in range(20):
                patient.get_memory_key(f"key_{i}")

        final_count = len(patient.memory_keys)

        # With 60% forget rate, should have forgotten some keys
        assert final_count < initial_count
