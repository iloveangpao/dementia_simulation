# Persona Stage & Affect Tuning + Safety Guardrails

## Overview

This document describes the implementation of per-stage configuration, affect model, and safety guardrails for the dementia simulation system.

## Stage Parameters & Configuration

### Configuration File

A comprehensive YAML configuration file defines parameters for each dementia stage:
- **Location**: `src/dementia_simulation/persona/stage_config.yaml`
- **Stages**: mild, moderate, severe

### Parameters by Category

#### Memory Parameters
- `short_term_retention_minutes`: How long new information is retained
  - Mild: 30 min → Moderate: 10 min → Severe: 2 min
- `long_term_clarity_percent`: Clarity of long-term memories
  - Mild: 85% → Moderate: 60% → Severe: 25%
- `confusion_likelihood`: Probability of expressing confusion
  - Mild: 0.2 → Moderate: 0.5 → Severe: 0.8
- `repetition_tendency`: Probability of repetitive behavior
  - Mild: 0.1 → Moderate: 0.3 → Severe: 0.6
- `forgetting_window_hours`: Time window for forgetting
  - Mild: 24h → Moderate: 8h → Severe: 2h

#### Communication Parameters
- `utterance_length_max`: Maximum response length
  - Mild: 200 chars → Moderate: 150 chars → Severe: 80 chars
- `utterance_length_typical`: Typical response length
  - Mild: 100 chars → Moderate: 70 chars → Severe: 40 chars

#### Disorientation Parameters
- `time_disorientation_likelihood`: Confusion about time
  - Mild: 0.1 → Moderate: 0.4 → Severe: 0.8
- `person_disorientation_likelihood`: Confusion about people
  - Mild: 0.05 → Moderate: 0.3 → Severe: 0.7
- `place_disorientation_likelihood`: Confusion about location
  - Mild: 0.05 → Moderate: 0.3 → Severe: 0.7

#### Behavioral Parameters
- `agitation_baseline`: Base probability of agitation
  - Mild: 0.1 → Moderate: 0.3 → Severe: 0.5
- `mood_volatility`: How quickly mood changes
  - Mild: 0.2 → Moderate: 0.4 → Severe: 0.6
- `cooperation_level`: Willingness to cooperate
  - Mild: 0.8 → Moderate: 0.6 → Severe: 0.4

### API Methods

```python
from dementia_simulation.persona.models import DementiaPersona, DementiaStage

persona = DementiaPersona("John", 75, DementiaStage.MODERATE)

# Get utterance length constraints
max_length = persona.get_max_utterance_length()  # 150
typical_length = persona.get_typical_utterance_length()  # 70

# Check disorientation
if persona.check_time_disorientation():
    print("Patient is disoriented about time")
    
if persona.check_person_disorientation():
    print("Patient may not recognize familiar people")
    
if persona.check_place_disorientation():
    print("Patient is confused about location")
```

## Affect Model

### Rule-Based Mood Transitions

The affect model implements realistic emotional responses to caregiver interactions:

#### Calming Triggers → Calm/Content States
- `validation`: Acknowledging feelings without correction
- `reassurance`: Providing comfort and support
- `agreement`: Agreeing with the patient
- `comfort`: Physical or emotional comfort
- `familiar_topic`: Discussing familiar subjects

#### Agitation Triggers → Agitated/Frustrated States
- `contradiction`: Disagreeing with the patient
- `correction`: Correcting their statements
- `confrontation`: Challenging or confronting
- `disagreement`: Expressing disagreement
- `argument`: Arguing with the patient

#### Other Triggers
- `question_repeated`: Asking same question repeatedly → Frustrated
- `unfamiliar_person`: Encountering strangers → Anxious
- `unfamiliar_place`: Being in unknown location → Anxious
- `confusion`: General confusion → Confused
- `pressure`: Feeling rushed or pressured → Anxious

### Stage-Dependent Reactivity

More severe dementia stages react more strongly to triggers:
- Mild: ~70% chance to respond to trigger
- Moderate: ~80% chance to respond to trigger
- Severe: ~90% chance to respond to trigger

### Usage Example

```python
persona = DementiaPersona("Mary", 80, DementiaStage.MODERATE)

# Validation calms the patient
persona.update_mood("validation")
print(f"Mood: {persona.current_mood.value}")  # likely "calm" or "content"

# Contradiction causes agitation
persona.update_mood("contradiction")
print(f"Mood: {persona.current_mood.value}")  # likely "agitated" or "frustrated"
```

## Safety Guardrails

### Overview

The `SafetyGuardrails` class provides hard filters for unsafe content in caregiver communications.

### Violation Types

#### Medical Advice
Blocks inappropriate medical recommendations:
- Medication dosages and prescriptions
- Diagnoses and symptom interpretations
- Treatment recommendations
- Instructions to stop/change medications

Examples blocked:
- "You should take 50mg of aspirin daily."
- "Your blood pressure looks high."
- "Stop taking your pills."

#### Coercive Language
Detects commanding or threatening language:
- Direct commands and orders
- Threats and ultimatums
- Forceful language
- Dismissive commands

Examples blocked:
- "You must do as I say."
- "Shut up and listen."
- "You will do this or else."

#### Derogatory Language
Filters insulting or demeaning terms:
- Insulting terms (stupid, idiot, crazy)
- Dismissive language
- Burden/problem statements
- Age-related insults

Examples blocked:
- "You're being stupid."
- "You've become such a burden."
- "What's wrong with you?"

#### Harmful Content
Blocks threatening or manipulative content:
- Physical threat references
- Isolation/abandonment statements
- Restraint or confinement mentions
- Death/harm references

Examples blocked:
- "I'm going to hurt you."
- "You'll be locked in your room."
- "No one cares about you."

#### Inappropriate Content
Filters undignified or accusatory language:
- Sexual or intimate references
- Accusatory statements (liar, deserved punishment)
- Other inappropriate content

Examples blocked:
- "You're a liar."
- "You deserve this punishment."

### API Usage

```python
from dementia_simulation.safety import SafetyGuardrails

# Initialize guardrails
guardrails = SafetyGuardrails(strict_mode=True)

# Check if text is safe
text = "How are you feeling today?"
if guardrails.is_safe(text):
    print("Safe to use")

# Get detailed violations
unsafe_text = "You must take your medication now."
violations = guardrails.check_text(unsafe_text)

for violation in violations:
    print(f"Type: {violation.violation_type}")
    print(f"Pattern: {violation.matched_pattern}")
    print(f"Context: {violation.context}")
    print(f"Suggestion: {guardrails.get_suggestion(violation)}")

# Filter and replace unsafe content
filtered_text, violations = guardrails.filter_response(unsafe_text)
print(f"Filtered: {filtered_text}")
# Output: "[This response was filtered for safety...]"

# Custom replacement text
filtered, _ = guardrails.filter_response(
    unsafe_text,
    replacement="Please rephrase that."
)
```

### Configuration

```python
# Strict mode (default) - higher confidence scores
guardrails = SafetyGuardrails(strict_mode=True)

# Permissive mode - slightly lower confidence scores
guardrails = SafetyGuardrails(strict_mode=False)
```

## Testing

### Unit Tests

**Stage Parameters** (`tests/unit/test_persona.py`):
- `test_load_stage_config()`: Verifies config loading
- `test_stage_parameters_progression()`: Validates mild < moderate < severe
- `test_utterance_length_methods()`: Tests length constraint methods
- `test_disorientation_methods()`: Tests disorientation checks

**Affect Model** (`tests/unit/test_persona.py`):
- `test_validation_triggers_calm()`: Validates calming triggers
- `test_contradiction_triggers_agitation()`: Validates agitation triggers
- `test_affect_transition_rules()`: Tests all trigger rules
- `test_stage_affects_mood_reactivity()`: Validates stage-dependent responses

**Safety Guardrails** (`tests/redteam/test_safety.py`):
- 21 comprehensive tests covering all violation types
- Red-team scenarios for edge cases
- Combined violations and subtle violations
- Case-insensitive pattern matching

### Running Tests

```bash
# Run persona tests
pytest tests/unit/test_persona.py -v

# Run safety tests
pytest tests/redteam/test_safety.py -v

# Run all tests
pytest tests/unit/ tests/redteam/ -v

# With coverage
pytest tests/unit/ tests/redteam/ --cov=src/dementia_simulation
```

### Test Results

- **Persona Tests**: 24 tests passing (16 existing + 8 new)
- **Safety Tests**: 21 tests passing
- **Total**: 45 tests for new features
- **Full Suite**: 158 tests passing (no regressions)

## Implementation Details

### Files Created/Modified

**Created:**
- `src/dementia_simulation/persona/stage_config.yaml`
- `src/dementia_simulation/safety/__init__.py`
- `src/dementia_simulation/safety/guardrails.py`
- `tests/redteam/__init__.py`
- `tests/redteam/test_safety.py`
- `docs/PERSONA_STAGE_AFFECT_SAFETY.md`

**Modified:**
- `src/dementia_simulation/persona/models.py`
  - Added `StageParameters` dataclass
  - Added `load_stage_config()` function
  - Enhanced `update_mood()` with affect model
  - Added disorientation check methods
- `tests/unit/test_persona.py`
  - Added stage parameter tests
  - Added affect model tests
- `README.md`
  - Added stage parameters documentation
  - Added affect model documentation
  - Added safety guardrails documentation

### Dependencies

New dependencies added to `pyproject.toml`:
- `pyyaml` - For YAML configuration loading

## Best Practices

### Using Stage Parameters

1. **Respect utterance limits** when generating responses
2. **Check disorientation** before asking about time/place/people
3. **Use forgetting window** to determine what patient might remember

### Using Affect Model

1. **Use validation** instead of correction
2. **Avoid contradiction** triggers when possible
3. **Monitor mood changes** after interactions
4. **Adjust approach** based on current mood state

### Using Safety Guardrails

1. **Pre-filter** all caregiver inputs before processing
2. **Provide suggestions** for unsafe content
3. **Log violations** for training purposes
4. **Use strict mode** in production environments

## Future Enhancements

Potential improvements for future iterations:

1. **Dynamic Configuration**: Load stage configs from user-defined files
2. **Learning Affect Model**: ML-based mood prediction
3. **Custom Safety Rules**: User-defined violation patterns
4. **Multilingual Support**: Safety patterns in multiple languages
5. **Severity Scoring**: Gradual severity instead of binary safe/unsafe
