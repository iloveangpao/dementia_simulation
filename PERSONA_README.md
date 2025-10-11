# PatientPersona - Dementia Simulation

A Python class for simulating patients with dementia, including memory degradation and mood state management.

## Features

- **Dementia Stages**: Three configurable stages (mild, moderate, severe) with different memory and behavioral parameters
- **Memory Degradation**: Random forgetting of memory keys based on dementia stage severity
- **Recent Memory Management**: Time-based and capacity-limited recent memory system
- **Mood State System**: Three mood states (calm, agitated, withdrawn) with probabilistic transitions
- **Realistic Simulation**: Stage-dependent parameters that reflect real dementia progression

## Quick Start

```python
from src.persona import PatientPersona, DementiaStage, MoodState

# Create a patient with mild dementia
patient = PatientPersona(
    name="John Doe",
    dementia_stage=DementiaStage.MILD,
    initial_mood=MoodState.CALM
)

# Add memories
patient.add_memory_key("daughter_name", "Sarah")
patient.add_recent_memory("Had breakfast")

# Simulate interactions
current_mood = patient.update_mood()
forgotten_memories = patient.forget_recent()
remembered_name = patient.get_memory_key("daughter_name")  # May return None if forgotten
```

## API Reference

### Classes

#### `PatientPersona`

Main class representing a patient with dementia.

**Constructor:**
```python
PatientPersona(name: str, dementia_stage: DementiaStage = DementiaStage.MILD, initial_mood: MoodState = MoodState.CALM)
```

**Methods:**
- `add_memory_key(key: str, value: Any)` - Add a key-value pair to long-term memory
- `get_memory_key(key: str) -> Optional[Any]` - Retrieve a memory (may be forgotten randomly)
- `add_recent_memory(memory: str)` - Add a recent memory with timestamp
- `forget_recent() -> List[str]` - Forget recent memories, returns list of forgotten items
- `update_mood() -> MoodState` - Update mood state, returns new mood
- `get_status() -> Dict[str, Any]` - Get comprehensive patient status

#### `DementiaStage` (Enum)
- `MILD` - 10% forget probability, 24h retention, 20 memory capacity
- `MODERATE` - 30% forget probability, 8h retention, 10 memory capacity  
- `SEVERE` - 60% forget probability, 2h retention, 5 memory capacity

#### `MoodState` (Enum)
- `CALM` - Peaceful, relaxed state
- `AGITATED` - Restless, anxious state
- `WITHDRAWN` - Isolated, unresponsive state

## Examples

See `example_usage.py` for a comprehensive demonstration of the class in action.

Run tests:
```bash
python test_persona.py          # Basic functionality tests
python validate_requirements.py # Requirements validation
python test_edge_cases.py      # Edge case testing
python example_usage.py        # Usage demonstration
```

## Implementation Details

The PatientPersona class simulates realistic dementia progression:

- **Memory degradation** increases with dementia stage severity
- **Mood changes** become more frequent as dementia progresses
- **Recent memories** have both time-based and capacity-based limits
- **Random forgetting** occurs during memory retrieval to simulate real conditions

Each dementia stage has carefully calibrated parameters based on clinical understanding of dementia progression.