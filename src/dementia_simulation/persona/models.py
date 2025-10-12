"""
Dementia persona models for simulation.

This module defines different dementia stages and their characteristics
to simulate realistic interactions for caregiver training.
"""

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class DementiaStage(Enum):
    """Dementia severity stages."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class MoodState(Enum):
    """Possible mood states for dementia patients."""

    CALM = "calm"
    CONFUSED = "confused"
    AGITATED = "agitated"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    CONTENT = "content"
    FRUSTRATED = "frustrated"


@dataclass
class MemoryProfile:
    """Memory characteristics for different dementia stages."""

    short_term_retention_minutes: int
    long_term_clarity_percent: int
    confusion_likelihood: float
    repetition_tendency: float
    forgetting_window_hours: int = 24


@dataclass
class StageParameters:
    """Extended parameters for each dementia stage."""

    # Memory parameters
    short_term_retention_minutes: int
    long_term_clarity_percent: int
    confusion_likelihood: float
    repetition_tendency: float
    forgetting_window_hours: int

    # Communication parameters
    utterance_length_max: int
    utterance_length_typical: int

    # Disorientation parameters
    time_disorientation_likelihood: float
    person_disorientation_likelihood: float
    place_disorientation_likelihood: float

    # Behavioral parameters
    agitation_baseline: float
    mood_volatility: float
    cooperation_level: float


@dataclass
class PersonalityTraits:
    """Personality and behavioral traits."""

    baseline_mood: MoodState
    mood_volatility: float  # 0.0 to 1.0
    social_engagement: float  # 0.0 to 1.0
    cooperation_level: float  # 0.0 to 1.0


def load_stage_config() -> Dict[DementiaStage, StageParameters]:
    """
    Load stage configuration from YAML file.

    Returns:
        Dictionary mapping stage to parameters
    """
    config_path = Path(__file__).parent / "stage_config.yaml"

    if not config_path.exists():
        # Return default config if file not found
        return _get_default_stage_config()

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    stage_config = {}
    for stage in DementiaStage:
        stage_key = stage.value
        if stage_key in config_data:
            params = config_data[stage_key]
            stage_config[stage] = StageParameters(**params)

    return stage_config


def _get_default_stage_config() -> Dict[DementiaStage, StageParameters]:
    """Get default stage configuration."""
    return {
        DementiaStage.MILD: StageParameters(
            short_term_retention_minutes=30,
            long_term_clarity_percent=85,
            confusion_likelihood=0.2,
            repetition_tendency=0.1,
            forgetting_window_hours=24,
            utterance_length_max=200,
            utterance_length_typical=100,
            time_disorientation_likelihood=0.1,
            person_disorientation_likelihood=0.05,
            place_disorientation_likelihood=0.05,
            agitation_baseline=0.1,
            mood_volatility=0.2,
            cooperation_level=0.8,
        ),
        DementiaStage.MODERATE: StageParameters(
            short_term_retention_minutes=10,
            long_term_clarity_percent=60,
            confusion_likelihood=0.5,
            repetition_tendency=0.3,
            forgetting_window_hours=8,
            utterance_length_max=150,
            utterance_length_typical=70,
            time_disorientation_likelihood=0.4,
            person_disorientation_likelihood=0.3,
            place_disorientation_likelihood=0.3,
            agitation_baseline=0.3,
            mood_volatility=0.4,
            cooperation_level=0.6,
        ),
        DementiaStage.SEVERE: StageParameters(
            short_term_retention_minutes=2,
            long_term_clarity_percent=25,
            confusion_likelihood=0.8,
            repetition_tendency=0.6,
            forgetting_window_hours=2,
            utterance_length_max=80,
            utterance_length_typical=40,
            time_disorientation_likelihood=0.8,
            person_disorientation_likelihood=0.7,
            place_disorientation_likelihood=0.7,
            agitation_baseline=0.5,
            mood_volatility=0.6,
            cooperation_level=0.4,
        ),
    }


class DementiaPersona:
    """
    Represents a dementia patient persona with specific characteristics
    based on their stage of dementia progression.
    """

    # Default memory profiles for each stage (backward compatibility)
    MEMORY_PROFILES = {
        DementiaStage.MILD: MemoryProfile(
            short_term_retention_minutes=30,
            long_term_clarity_percent=85,
            confusion_likelihood=0.2,
            repetition_tendency=0.1,
            forgetting_window_hours=24,
        ),
        DementiaStage.MODERATE: MemoryProfile(
            short_term_retention_minutes=10,
            long_term_clarity_percent=60,
            confusion_likelihood=0.5,
            repetition_tendency=0.3,
            forgetting_window_hours=8,
        ),
        DementiaStage.SEVERE: MemoryProfile(
            short_term_retention_minutes=2,
            long_term_clarity_percent=25,
            confusion_likelihood=0.8,
            repetition_tendency=0.6,
            forgetting_window_hours=2,
        ),
    }

    # Load stage configuration
    STAGE_CONFIG: Dict[DementiaStage, StageParameters] = load_stage_config()

    def __init__(
        self,
        name: str,
        age: int,
        stage: DementiaStage,
        personality: Optional[PersonalityTraits] = None,
        memory_profile: Optional[MemoryProfile] = None,
        background: Optional[Dict[str, str]] = None,
        context: Optional[str] = None,
    ):
        """
        Initialize a dementia persona.

        Args:
            name: Patient's name
            age: Patient's age
            stage: Dementia stage (mild/moderate/severe)
            personality: Personality traits (auto-generated if None)
            memory_profile: Memory characteristics (default for stage if None)
            background: Personal background information
            context: Current scenario context (e.g., "In emergency room after a fall")
        """
        self.name = name
        self.age = age
        self.stage = stage
        self.memory_profile = memory_profile or self.MEMORY_PROFILES[stage]
        self.personality = personality or self._generate_personality()
        self.background = background or {}
        self.context = context or ""

        # Conversation state
        self.current_mood = self.personality.baseline_mood
        self.conversation_history: List[Dict[str, str]] = []
        self.recent_topics: List[str] = []
        self.last_interaction = datetime.now()

    def _generate_personality(self) -> PersonalityTraits:
        """Generate a random personality based on dementia stage."""
        # More severe stages tend toward more volatility and less cooperation
        volatility_base = {
            DementiaStage.MILD: 0.2,
            DementiaStage.MODERATE: 0.4,
            DementiaStage.SEVERE: 0.6,
        }

        cooperation_base = {
            DementiaStage.MILD: 0.8,
            DementiaStage.MODERATE: 0.6,
            DementiaStage.SEVERE: 0.4,
        }

        return PersonalityTraits(
            baseline_mood=random.choice(list(MoodState)),
            mood_volatility=volatility_base[self.stage] + random.uniform(-0.1, 0.2),
            social_engagement=random.uniform(0.3, 0.9),
            cooperation_level=cooperation_base[self.stage] + random.uniform(-0.2, 0.2),
        )

    def update_mood(self, trigger: Optional[str] = None) -> MoodState:
        """
        Update current mood based on personality and external triggers.

        Implements rule-based affect transitions:
        - validation → calmer states
        - contradiction → agitation

        Args:
            trigger: External trigger that might affect mood

        Returns:
            Updated mood state
        """
        stage_params = self.STAGE_CONFIG.get(self.stage)

        # Random mood fluctuation based on volatility
        if stage_params and random.random() < stage_params.mood_volatility * 0.3:
            mood_options = list(MoodState)
            # Remove current mood to force a change
            if self.current_mood in mood_options:
                mood_options.remove(self.current_mood)
            self.current_mood = random.choice(mood_options)

        # Affect model: rule-based trigger responses
        if trigger:
            trigger_responses = self._get_affect_transitions(trigger)
            if trigger in trigger_responses:
                # Higher severity = more reactive to triggers
                response_probability = 0.6 + (
                    0.3
                    if self.stage == DementiaStage.SEVERE
                    else 0.2 if self.stage == DementiaStage.MODERATE else 0.1
                )
                if random.random() < response_probability:
                    self.current_mood = trigger_responses[trigger]

        return self.current_mood

    def _get_affect_transitions(self, trigger: str) -> Dict[str, MoodState]:
        """
        Get affect model transitions based on triggers.

        Rule-based transitions:
        - Validation/reassurance → calmer states
        - Contradiction/correction → agitation/frustration
        - Questions repeated → frustration
        - Unfamiliar situations → anxiety

        Args:
            trigger: The trigger type

        Returns:
            Dictionary mapping triggers to mood states
        """
        return {
            # Calming triggers (validation)
            "validation": MoodState.CALM,
            "reassurance": MoodState.CALM,
            "agreement": MoodState.CONTENT,
            "familiar_topic": MoodState.CONTENT,
            "comfort": MoodState.CALM,
            # Agitation triggers (contradiction)
            "correction": MoodState.AGITATED,
            "contradiction": MoodState.AGITATED,
            "disagreement": MoodState.FRUSTRATED,
            "confrontation": MoodState.AGITATED,
            "argument": MoodState.AGITATED,
            # Other triggers
            "question_repeated": MoodState.FRUSTRATED,
            "unfamiliar_person": MoodState.ANXIOUS,
            "unfamiliar_place": MoodState.ANXIOUS,
            "confusion": MoodState.CONFUSED,
            "pressure": MoodState.ANXIOUS,
        }

    def should_remember(self, minutes_ago: int) -> bool:
        """
        Determine if the persona should remember something from X minutes ago.

        Args:
            minutes_ago: How many minutes ago the event occurred

        Returns:
            True if should remember, False otherwise
        """
        retention_minutes = self.memory_profile.short_term_retention_minutes

        if minutes_ago <= retention_minutes:
            # Within retention window, but still some chance of forgetting
            forget_chance = 0.1 + (minutes_ago / retention_minutes) * 0.3
            return random.random() > forget_chance
        else:
            # Outside retention window, very low chance of remembering
            return random.random() < 0.05

    def should_be_confused(self) -> bool:
        """Determine if the persona should express confusion."""
        return random.random() < self.memory_profile.confusion_likelihood

    def should_repeat(self) -> bool:
        """Determine if the persona should repeat themselves."""
        return random.random() < self.memory_profile.repetition_tendency

    def check_time_disorientation(self) -> bool:
        """
        Check if persona is disoriented about time.

        Returns:
            True if disoriented about time
        """
        stage_params = self.STAGE_CONFIG.get(self.stage)
        if not stage_params:
            return False
        return random.random() < stage_params.time_disorientation_likelihood

    def check_person_disorientation(self) -> bool:
        """
        Check if persona is disoriented about people.

        Returns:
            True if disoriented about people/identities
        """
        stage_params = self.STAGE_CONFIG.get(self.stage)
        if not stage_params:
            return False
        return random.random() < stage_params.person_disorientation_likelihood

    def check_place_disorientation(self) -> bool:
        """
        Check if persona is disoriented about location.

        Returns:
            True if disoriented about place/location
        """
        stage_params = self.STAGE_CONFIG.get(self.stage)
        if not stage_params:
            return False
        return random.random() < stage_params.place_disorientation_likelihood

    def get_max_utterance_length(self) -> int:
        """
        Get maximum utterance length for this stage.

        Returns:
            Maximum response length in characters
        """
        stage_params = self.STAGE_CONFIG.get(self.stage)
        if not stage_params:
            return 200
        return stage_params.utterance_length_max

    def get_typical_utterance_length(self) -> int:
        """
        Get typical utterance length for this stage.

        Returns:
            Typical response length in characters
        """
        stage_params = self.STAGE_CONFIG.get(self.stage)
        if not stage_params:
            return 100
        return stage_params.utterance_length_typical

    def get_symptoms_description(self) -> Dict[str, str]:
        """
        Get a description of symptoms based on dementia stage.

        Returns:
            Dictionary describing memory, orientation, emotion, insight
        """
        if self.stage == DementiaStage.MILD:
            return {
                "memory": (
                    "Occasional memory lapses for recent events, "
                    "may forget words or repeat questions"
                ),
                "orientation": (
                    "Generally oriented to time and place, "
                    "may occasionally be confused"
                ),
                "emotion": (
                    "May become quietly frustrated or withdrawn "
                    "when unable to remember"
                ),
                "insight": (
                    "Aware of memory problems, may try to compensate "
                    "or cover up difficulties"
                ),
            }
        elif self.stage == DementiaStage.MODERATE:
            return {
                "memory": (
                    "Frequently forgets recent events and repeats questions; "
                    "significant memory loss"
                ),
                "orientation": (
                    "Often disoriented to time/place, may think they're "
                    "at home or another location"
                ),
                "emotion": (
                    "Anxious in unfamiliar settings; can become agitated, "
                    "suspicious, or accusatory if stressed"
                ),
                "insight": (
                    "Lacks awareness of cognitive issues, may insist "
                    "they're fine or become defensive"
                ),
            }
        else:  # SEVERE
            return {
                "memory": (
                    "Severe memory impairment; hardly remembers "
                    "recent or even past events"
                ),
                "orientation": (
                    "Severely disoriented; may not recognize familiar people "
                    "or understand where they are"
                ),
                "emotion": (
                    "Limited emotional expression; may exhibit anxiety, "
                    "fear, or agitation without clear cause"
                ),
                "insight": (
                    "No awareness of condition; communicates primarily "
                    "through simple words or non-verbal cues"
                ),
            }

    def add_to_conversation_history(self, message: str, speaker: str) -> None:
        """
        Add a message to conversation history.

        Args:
            message: The message content
            speaker: Who said it ('patient' or 'caregiver')
        """
        self.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "speaker": speaker,
                "message": message,
                "mood": self.current_mood.value,
            }
        )

        # Keep only recent history based on memory capacity
        max_history = max(5, 20 - (self.stage.value == "severe") * 10)
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]

    def get_context_prompt(self) -> str:
        """
        Generate context prompt for LLM based on persona characteristics.

        Returns:
            Formatted prompt describing the persona's current state
        """
        prompt = (
            f"You are roleplaying as {self.name}, a {self.age}-year-old "
            f"person with {self.stage.value} dementia.\n"
        )

        if self.context:
            prompt += f"\nCurrent Situation: {self.context}\n"

        prompt += f"""
Personality and Current State:
- Current mood: {self.current_mood.value}
- Memory retention: {self.memory_profile.short_term_retention_minutes} min
- Long-term memory clarity: {self.memory_profile.long_term_clarity_percent}%
- Baseline mood: {self.personality.baseline_mood.value}
- Social engagement: {self.personality.social_engagement:.1f}/1.0
- Cooperation level: {self.personality.cooperation_level:.1f}/1.0

Behavioral Guidelines for {self.stage.value} dementia:
"""

        if self.stage == DementiaStage.MILD:
            prompt += (
                "- Occasional memory lapses, especially for recent events\n"
                "- Generally able to maintain conversations\n"
                "- May repeat questions or stories occasionally\n"
                "- Mostly independent but may need gentle reminders"
            )
        elif self.stage == DementiaStage.MODERATE:
            prompt += (
                "- Significant short-term memory problems\n"
                "- May confuse people, places, or times\n"
                "- Can become easily frustrated or agitated\n"
                "- Needs assistance with daily activities\n"
                "- May repeat questions frequently"
            )
        else:  # SEVERE
            prompt += (
                "- Severe memory impairment and confusion\n"
                "- May not recognize familiar people\n"
                "- Limited vocabulary and communication\n"
                "- Requires constant supervision and care\n"
                "- May exhibit repetitive behaviors or agitation"
            )

        if self.background:
            prompt += "\n\nPersonal Background:\n"
            for key, value in self.background.items():
                prompt += f"- {key}: {value}\n"

        prompt += (
            f"\nRespond naturally as this person would, keeping their "
            f"current mood ({self.current_mood.value}) and dementia stage "
            f"in mind."
        )

        return prompt

    def to_dict(self) -> Dict:
        """Convert persona to dictionary for serialization."""
        mp = self.memory_profile
        return {
            "name": self.name,
            "age": self.age,
            "stage": self.stage.value,
            "current_mood": self.current_mood.value,
            "context": self.context,
            "memory_profile": {
                "short_term_retention_minutes": mp.short_term_retention_minutes,
                "long_term_clarity_percent": mp.long_term_clarity_percent,
                "confusion_likelihood": mp.confusion_likelihood,
                "repetition_tendency": mp.repetition_tendency,
            },
            "personality": {
                "baseline_mood": self.personality.baseline_mood.value,
                "mood_volatility": self.personality.mood_volatility,
                "social_engagement": self.personality.social_engagement,
                "cooperation_level": self.personality.cooperation_level,
            },
            "background": self.background,
        }


def get_persona_contexts(json_path: str) -> Dict[str, List[str]]:
    """
    Get all possible contexts for personas in a JSON file.

    Args:
        json_path: Path to the JSON file containing persona definitions

    Returns:
        Dictionary mapping persona names to their possible contexts
    """
    import json
    from pathlib import Path

    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Persona file not found: {json_path}")

    with open(path, "r") as f:
        personas_data = json.load(f)

    contexts = {}
    for data in personas_data:
        name = data.get("name", "Unknown")
        possible_contexts = data.get("possible_contexts", [])
        contexts[name] = possible_contexts

    return contexts


def load_personas_from_json(
    json_path: str, context_index: Optional[int] = None
) -> List[DementiaPersona]:
    """
    Load personas from a JSON file.

    Args:
        json_path: Path to the JSON file containing persona definitions
        context_index: Optional index to select a specific context from
                      possible_contexts array. If None, uses a random context
                      or falls back to current_concerns.

    Returns:
        List of DementiaPersona objects
    """
    import json
    from pathlib import Path

    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Persona file not found: {json_path}")

    with open(path, "r") as f:
        personas_data = json.load(f)

    personas = []
    for data in personas_data:
        # Map stage string to enum
        stage_map = {
            "mild": DementiaStage.MILD,
            "moderate": DementiaStage.MODERATE,
            "severe": DementiaStage.SEVERE,
        }
        stage = stage_map.get(data["stage"].lower(), DementiaStage.MILD)

        # Build background dict from available data
        background = data.get("background", {}).copy()

        # Add medical history to background if available
        if "medical_history" in data:
            med_hist = data["medical_history"]
            if "diagnosis" in med_hist:
                background["diagnosis"] = med_hist["diagnosis"]
            if "medications" in med_hist:
                background["medications"] = med_hist["medications"]
            if "other_conditions" in med_hist:
                background["other_conditions"] = med_hist["other_conditions"]

        # Build context - prioritize possible_contexts if available
        context = ""
        if "possible_contexts" in data and data["possible_contexts"]:
            possible_contexts = data["possible_contexts"]
            if context_index is not None:
                # Use specified context index
                idx = context_index % len(possible_contexts)
                context = possible_contexts[idx]
            else:
                # Use random context
                context = random.choice(possible_contexts)
        elif "current_concerns" in data and data["current_concerns"]:
            # Fallback to current concerns
            concerns = data["current_concerns"]
            context = "Current concerns: " + "; ".join(concerns[:3])

        persona = DementiaPersona(
            name=data["name"],
            age=data["age"],
            stage=stage,
            background=background,
            context=context,
        )

        personas.append(persona)

    return personas


def create_sample_personas() -> List[DementiaPersona]:
    """
    Create sample personas for testing and demonstration.

    Attempts to load from data/personas/sample_personas.json if available,
    otherwise falls back to hardcoded personas.

    Returns:
        List of DementiaPersona objects
    """
    from pathlib import Path

    # Try to find the JSON file relative to this module
    current_dir = Path(__file__).parent
    json_path = (
        current_dir.parent.parent.parent / "data" / "personas" / "sample_personas.json"
    )

    # Also check if running from installed package
    if not json_path.exists():
        # Try relative to current working directory
        json_path = Path("data/personas/sample_personas.json")

    if json_path.exists():
        try:
            return load_personas_from_json(str(json_path))
        except Exception as e:
            # Fall back to hardcoded personas if loading fails
            import warnings

            warnings.warn(
                f"Failed to load personas from {json_path}: {e}. "
                f"Using hardcoded personas.",
                stacklevel=2,
            )

    # Fallback hardcoded personas
    personas = [
        DementiaPersona(
            name="Margaret",
            age=78,
            stage=DementiaStage.MILD,
            background={
                "profession": "Retired teacher",
                "family": "Widow, 2 adult children",
                "interests": "Reading, gardening, classical music",
            },
            context="At home, concerned about memory lapses",
        ),
        DementiaPersona(
            name="Robert",
            age=82,
            stage=DementiaStage.MODERATE,
            background={
                "profession": "Former engineer",
                "family": "Married 55 years, 3 children",
                "interests": "Woodworking, baseball, old movies",
            },
            context="Often confused about time and place",
        ),
        DementiaPersona(
            name="Eleanor",
            age=85,
            stage=DementiaStage.SEVERE,
            background={
                "profession": "Former nurse",
                "family": "Widow, 4 children, 8 grandchildren",
                "interests": "Used to love cooking and knitting",
            },
            context="Requires constant supervision and care",
        ),
    ]

    return personas
