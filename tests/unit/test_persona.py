"""Unit tests for persona models."""

from dementia_simulation.persona.models import (
    DementiaPersona,
    DementiaStage,
    MemoryProfile,
    MoodState,
    PersonalityTraits,
    StageParameters,
    create_sample_personas,
    load_stage_config,
)


class TestDementiaStage:
    """Test DementiaStage enum."""

    def test_stages_exist(self):
        """Test that all dementia stages are defined."""
        assert DementiaStage.MILD.value == "mild"
        assert DementiaStage.MODERATE.value == "moderate"
        assert DementiaStage.SEVERE.value == "severe"


class TestMoodState:
    """Test MoodState enum."""

    def test_moods_exist(self):
        """Test that mood states are defined."""
        expected_moods = [
            "calm",
            "confused",
            "agitated",
            "anxious",
            "depressed",
            "content",
            "frustrated",
        ]
        actual_moods = [mood.value for mood in MoodState]

        for mood in expected_moods:
            assert mood in actual_moods


class TestMemoryProfile:
    """Test MemoryProfile dataclass."""

    def test_memory_profile_creation(self):
        """Test creating a memory profile."""
        profile = MemoryProfile(
            short_term_retention_minutes=30,
            long_term_clarity_percent=85,
            confusion_likelihood=0.2,
            repetition_tendency=0.1,
        )

        assert profile.short_term_retention_minutes == 30
        assert profile.long_term_clarity_percent == 85
        assert profile.confusion_likelihood == 0.2
        assert profile.repetition_tendency == 0.1


class TestPersonalityTraits:
    """Test PersonalityTraits dataclass."""

    def test_personality_traits_creation(self):
        """Test creating personality traits."""
        traits = PersonalityTraits(
            baseline_mood=MoodState.CALM,
            mood_volatility=0.3,
            social_engagement=0.8,
            cooperation_level=0.7,
        )

        assert traits.baseline_mood == MoodState.CALM
        assert traits.mood_volatility == 0.3
        assert traits.social_engagement == 0.8
        assert traits.cooperation_level == 0.7


class TestDementiaPersona:
    """Test DementiaPersona class."""

    def test_persona_creation_minimal(self):
        """Test creating a persona with minimal parameters."""
        persona = DementiaPersona(name="Test Person", age=75, stage=DementiaStage.MILD)

        assert persona.name == "Test Person"
        assert persona.age == 75
        assert persona.stage == DementiaStage.MILD
        assert persona.memory_profile is not None
        assert persona.personality is not None
        assert isinstance(persona.conversation_history, list)
        assert len(persona.conversation_history) == 0

    def test_persona_creation_full(self):
        """Test creating a persona with all parameters."""
        memory_profile = MemoryProfile(20, 70, 0.4, 0.2)
        personality = PersonalityTraits(MoodState.CONTENT, 0.2, 0.9, 0.8)
        background = {"profession": "Teacher"}

        persona = DementiaPersona(
            name="Full Test",
            age=80,
            stage=DementiaStage.MODERATE,
            personality=personality,
            memory_profile=memory_profile,
            background=background,
        )

        assert persona.name == "Full Test"
        assert persona.memory_profile == memory_profile
        assert persona.personality == personality
        assert persona.background == background

    def test_default_memory_profiles(self):
        """Test that default memory profiles exist for all stages."""
        for stage in DementiaStage:
            assert stage in DementiaPersona.MEMORY_PROFILES
            profile = DementiaPersona.MEMORY_PROFILES[stage]
            assert isinstance(profile, MemoryProfile)

    def test_memory_profiles_progression(self):
        """Test that memory profiles show progression of dementia."""
        mild = DementiaPersona.MEMORY_PROFILES[DementiaStage.MILD]
        moderate = DementiaPersona.MEMORY_PROFILES[DementiaStage.MODERATE]
        severe = DementiaPersona.MEMORY_PROFILES[DementiaStage.SEVERE]

        # Retention time should decrease
        assert mild.short_term_retention_minutes > moderate.short_term_retention_minutes
        assert (
            moderate.short_term_retention_minutes > severe.short_term_retention_minutes
        )

        # Clarity should decrease
        assert mild.long_term_clarity_percent > moderate.long_term_clarity_percent
        assert moderate.long_term_clarity_percent > severe.long_term_clarity_percent

        # Confusion should increase
        assert mild.confusion_likelihood < moderate.confusion_likelihood
        assert moderate.confusion_likelihood < severe.confusion_likelihood

    def test_mood_update(self):
        """Test mood update functionality."""
        persona = DementiaPersona("Test", 75, DementiaStage.MILD)

        # Update mood with trigger
        new_mood = persona.update_mood("validation")
        assert isinstance(new_mood, MoodState)

        # Mood might change or stay the same
        assert persona.current_mood in list(MoodState)

    def test_should_remember(self):
        """Test memory retention logic."""
        persona = DementiaPersona("Test", 75, DementiaStage.MILD)

        # Should remember recent events (probabilistic)
        recent_memory = persona.should_remember(5)
        assert isinstance(recent_memory, bool)

        # Should rarely remember very old events
        old_memory = persona.should_remember(1000)
        assert isinstance(old_memory, bool)

    def test_should_be_confused(self):
        """Test confusion probability."""
        persona = DementiaPersona("Test", 75, DementiaStage.SEVERE)
        confusion = persona.should_be_confused()
        assert isinstance(confusion, bool)

    def test_should_repeat(self):
        """Test repetition tendency."""
        persona = DementiaPersona("Test", 75, DementiaStage.MODERATE)
        repetition = persona.should_repeat()
        assert isinstance(repetition, bool)

    def test_conversation_history(self):
        """Test conversation history management."""
        persona = DementiaPersona("Test", 75, DementiaStage.MILD)

        # Add messages
        persona.add_to_conversation_history("Hello", "caregiver")
        persona.add_to_conversation_history("Hi there", "patient")

        assert len(persona.conversation_history) == 2

        # Check message structure
        message = persona.conversation_history[0]
        assert "timestamp" in message
        assert message["speaker"] == "caregiver"
        assert message["message"] == "Hello"
        assert "mood" in message

    def test_context_prompt_generation(self):
        """Test context prompt generation."""
        persona = DementiaPersona("Test", 75, DementiaStage.MILD)
        prompt = persona.get_context_prompt()

        assert isinstance(prompt, str)
        assert "Test" in prompt
        assert "75" in prompt
        assert "mild" in prompt
        assert len(prompt) > 100  # Should be substantial

    def test_to_dict_serialization(self):
        """Test persona serialization to dictionary."""
        persona = DementiaPersona(
            name="Test", age=75, stage=DementiaStage.MILD, background={"test": "value"}
        )

        persona_dict = persona.to_dict()

        assert isinstance(persona_dict, dict)
        assert persona_dict["name"] == "Test"
        assert persona_dict["age"] == 75
        assert persona_dict["stage"] == "mild"
        assert "memory_profile" in persona_dict
        assert "personality" in persona_dict
        assert persona_dict["background"]["test"] == "value"


class TestSamplePersonas:
    """Test sample persona creation."""

    def test_create_sample_personas(self):
        """Test that sample personas are created correctly."""
        personas = create_sample_personas()

        assert isinstance(personas, list)
        assert len(personas) >= 3  # Should have at least 3 personas

        # Check that all stages are represented
        stages = [persona.stage for persona in personas]
        assert DementiaStage.MILD in stages
        assert DementiaStage.MODERATE in stages
        assert DementiaStage.SEVERE in stages

        # Check persona validity
        for persona in personas:
            assert isinstance(persona, DementiaPersona)
            assert isinstance(persona.name, str)
            assert persona.age > 0
            assert persona.stage in DementiaStage
            assert isinstance(persona.background, dict)


class TestStageParameters:
    """Test stage parameters and configuration."""

    def test_load_stage_config(self):
        """Test loading stage configuration."""
        config = load_stage_config()

        assert isinstance(config, dict)
        assert len(config) == 3  # Three stages

        for stage in DementiaStage:
            assert stage in config
            params = config[stage]
            assert isinstance(params, StageParameters)

    def test_stage_parameters_progression(self):
        """Test that stage parameters show proper progression."""
        config = load_stage_config()

        mild = config[DementiaStage.MILD]
        moderate = config[DementiaStage.MODERATE]
        severe = config[DementiaStage.SEVERE]

        # Memory should worsen
        assert mild.short_term_retention_minutes > moderate.short_term_retention_minutes
        assert (
            moderate.short_term_retention_minutes > severe.short_term_retention_minutes
        )
        assert mild.long_term_clarity_percent > moderate.long_term_clarity_percent
        assert moderate.long_term_clarity_percent > severe.long_term_clarity_percent
        assert mild.forgetting_window_hours > moderate.forgetting_window_hours
        assert moderate.forgetting_window_hours > severe.forgetting_window_hours

        # Confusion/repetition should increase
        assert mild.confusion_likelihood < moderate.confusion_likelihood
        assert moderate.confusion_likelihood < severe.confusion_likelihood
        assert mild.repetition_tendency < moderate.repetition_tendency
        assert moderate.repetition_tendency < severe.repetition_tendency

        # Communication ability should decrease
        assert mild.utterance_length_max > moderate.utterance_length_max
        assert moderate.utterance_length_max > severe.utterance_length_max

        # Disorientation should increase
        assert (
            mild.time_disorientation_likelihood
            < moderate.time_disorientation_likelihood
        )
        assert (
            moderate.time_disorientation_likelihood
            < severe.time_disorientation_likelihood
        )
        assert (
            mild.person_disorientation_likelihood
            < moderate.person_disorientation_likelihood
        )
        assert (
            moderate.person_disorientation_likelihood
            < severe.person_disorientation_likelihood
        )
        assert (
            mild.place_disorientation_likelihood
            < moderate.place_disorientation_likelihood
        )
        assert (
            moderate.place_disorientation_likelihood
            < severe.place_disorientation_likelihood
        )

        # Cooperation should decrease
        assert mild.cooperation_level > moderate.cooperation_level
        assert moderate.cooperation_level > severe.cooperation_level

    def test_utterance_length_methods(self):
        """Test utterance length getter and sampling methods."""
        persona = DementiaPersona("Test", 75, DementiaStage.MODERATE)

        max_length = persona.get_max_utterance_length()
        typical_length = persona.get_typical_utterance_length()

        assert isinstance(max_length, int)
        assert isinstance(typical_length, int)
        assert max_length > typical_length
        assert typical_length > 0

        # Test sampling method
        samples = [persona.sample_utterance_length() for _ in range(100)]
        assert all(isinstance(s, int) for s in samples)
        assert all(s > 0 for s in samples)

        # Samples should vary (not all the same - avoids robotic cadence)
        assert len(set(samples)) > 10, "Should have variety in utterance lengths"

        # Most samples should be reasonably close to mean
        mean_sample = sum(samples) / len(samples)
        assert abs(mean_sample - typical_length) < 30  # Within 30 chars of mean

    def test_disorientation_methods(self):
        """Test disorientation check methods."""
        persona = DementiaPersona("Test", 75, DementiaStage.SEVERE)

        # Run multiple times to test probabilistic behavior
        time_disorientations = [persona.check_time_disorientation() for _ in range(100)]
        person_disorientations = [
            persona.check_person_disorientation() for _ in range(100)
        ]
        place_disorientations = [
            persona.check_place_disorientation() for _ in range(100)
        ]

        # All should return booleans
        assert all(isinstance(x, bool) for x in time_disorientations)
        assert all(isinstance(x, bool) for x in person_disorientations)
        assert all(isinstance(x, bool) for x in place_disorientations)

        # For severe stage, should have some disorientations
        assert any(time_disorientations), "Should have some time disorientation"
        assert any(person_disorientations), "Should have some person disorientation"
        assert any(place_disorientations), "Should have some place disorientation"


class TestAffectModel:
    """Test affect model and mood transitions."""

    def test_validation_triggers_calm(self):
        """Test that validation triggers drift toward calmer states."""
        persona = DementiaPersona("Test", 75, DementiaStage.MODERATE)

        # Apply validation multiple times to build up drift
        calmer_states = {MoodState.CALM, MoodState.CONTENT}
        for _ in range(30):
            persona.update_mood("validation")

        # Should drift toward calmer states
        assert persona.current_mood in calmer_states or persona._mood_drift < 0, (
            f"Validation should lead to calmer mood, got {persona.current_mood.value} "
            f"with drift {persona._mood_drift}"
        )

    def test_contradiction_triggers_agitation(self):
        """Test that contradiction triggers drift toward agitated states."""
        persona = DementiaPersona("Test", 75, DementiaStage.MODERATE)

        # Apply contradiction multiple times to build up drift
        agitated_states = {MoodState.AGITATED, MoodState.FRUSTRATED, MoodState.ANXIOUS}
        for _ in range(30):
            persona.update_mood("contradiction")

        # Should drift toward more agitated states
        assert persona.current_mood in agitated_states or persona._mood_drift > 0, (
            f"Contradiction should lead to agitated mood, "
            f"got {persona.current_mood.value} with drift {persona._mood_drift}"
        )

    def test_affect_transition_rules(self):
        """Test that affect transitions follow defined drift directions."""

        # Test calming triggers reduce drift
        calming_triggers = ["validation", "reassurance", "agreement", "comfort"]
        for trigger in calming_triggers:
            persona = DementiaPersona("Test", 75, DementiaStage.MILD)
            initial_drift = persona._mood_drift

            # Apply trigger multiple times
            for _ in range(15):
                persona.update_mood(trigger)

            # Drift should move negative (toward calm)
            assert persona._mood_drift < initial_drift + 0.5, (
                f"Calming trigger '{trigger}' should reduce mood drift"
            )

        # Test agitation triggers increase drift
        agitation_triggers = ["correction", "contradiction", "confrontation"]
        for trigger in agitation_triggers:
            persona = DementiaPersona("Test", 75, DementiaStage.MILD)
            initial_drift = persona._mood_drift

            # Apply trigger multiple times
            for _ in range(15):
                persona.update_mood(trigger)

            # Drift should move positive (toward agitated)
            assert persona._mood_drift > initial_drift - 0.5, (
                f"Agitation trigger '{trigger}' should increase mood drift"
            )

    def test_stage_affects_mood_reactivity(self):
        """Test that more severe stages are more reactive to triggers."""
        # Run multiple trials to account for randomness
        severe_higher_count = 0
        trials = 10

        for _trial in range(trials):
            mild_persona = DementiaPersona("Mild", 75, DementiaStage.MILD)
            severe_persona = DementiaPersona("Severe", 75, DementiaStage.SEVERE)

            # Start from same baseline
            mild_persona._mood_drift = 0.0
            severe_persona._mood_drift = 0.0

            # Apply same trigger to both personas
            for _ in range(20):
                mild_persona.update_mood("contradiction")
                severe_persona.update_mood("contradiction")

            # Count how many times severe had higher drift
            if severe_persona._mood_drift > mild_persona._mood_drift:
                severe_higher_count += 1

        # Severe stage should be more reactive in majority of trials
        assert severe_higher_count >= trials * 0.6, (
            f"Severe stage should be more reactive in at least 60% of trials. "
            f"Was higher in {severe_higher_count}/{trials} trials"
        )
