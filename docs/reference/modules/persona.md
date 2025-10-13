# Persona Module

Patient persona simulation with stage-based parameters and affect modeling.

## Overview

The `persona` module provides realistic dementia patient simulation across three stages: mild, moderate, and severe. It includes:

- Stage-based configuration
- Memory simulation
- Communication patterns
- Affect (mood) modeling
- Conversation history tracking

## Quick Example

```python
from dementia_simulation.persona import DementiaPersona, DementiaStage

# Create persona
persona = DementiaPersona(
    name="Mary",
    age=78,
    stage=DementiaStage.MODERATE
)

# Generate response
response = persona.generate_response(
    caregiver_message="How are you feeling today?",
    context=conversation_history
)

print(f"Response: {response['text']}")
print(f"Mood: {response['mood']}")
```

## Module Reference

The persona module is located in `src/dementia_simulation/persona/`.

**Key Classes**:

- `DementiaPersona` - Main persona class with stage simulation
- `DementiaStage` - Enum for stages (MILD, MODERATE, SEVERE)
- `AffectModel` - Mood and affect simulation
- `MemoryModel` - Memory simulation and forgetting
- `ConversationHistory` - Tracks conversation context

**Configuration**:

- `stage_config.yaml` - Stage parameters (memory, communication, behavioral)

For full module documentation, see the source code with inline docstrings using Google-style format.

## Related

- **[Personas Explanation](../../explanation/personas.md)** - Detailed stage parameters
- **[Quickstart Tutorial](../../tutorials/quickstart.md)** - Get started
- **[Architecture](../../explanation/architecture.md)** - System overview
