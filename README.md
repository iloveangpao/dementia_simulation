# Dementia Simulation Chat System

A Python-based chat system that simulates conversations with patients experiencing dementia. The system includes persona management, memory/forgetting patterns, mood changes, and a RAG (Retrieval-Augmented Generation) pipeline for generating realistic responses.

## Features

- **Chat Loop**: Implements a conversation loop that stores complete chat history
- **Persona State Management**: Tracks and evolves the patient's cognitive and emotional state
- **Forgetting Rules**: Simulates memory degradation patterns typical in dementia
- **Mood System**: Models emotional states and mood changes during conversations
- **RAG Pipeline**: Generates contextually appropriate responses based on persona state
- **Persistence**: Save and load conversation sessions
- **Comprehensive Testing**: Full test suite validating all components

## Quick Start

```python
from src.chat import DementiaSimulationChat

# Initialize the chat system
chat = DementiaSimulationChat()

# Have a conversation
response, persona_state = chat.chat_loop("Hello, how are you feeling today?")
print(f"Patient: {response}")
print(f"Current mood: {persona_state['current_mood']}")
print(f"Confusion level: {persona_state['confusion_level']}")
```

## Running Examples

```bash
# Run automated demonstration
python example.py

# Run interactive chat session
python example.py interactive

# Run tests
python -m unittest tests.test_chat -v
```

## Architecture

### Core Components

1. **PersonaState**: Tracks the patient's cognitive and emotional state
   - Short-term and long-term memory
   - Confusion level and mood
   - Behavioral patterns and preferences

2. **ChatMessage**: Represents individual messages with timestamps and persona snapshots

3. **DementiaSimulationRules**: Implements forgetting and mood change logic
   - Memory degradation patterns
   - Mood triggers and transitions

4. **RAG Pipeline**: Generates responses based on query, context, and persona state
   - Mood-influenced responses
   - Confusion-level appropriate replies
   - Topic-aware response selection

5. **DementiaSimulationChat**: Main chat system orchestrating all components
   - Chat loop with history storage
   - Persona state evolution
   - Conversation persistence

### Chat Loop Flow

1. **Input Processing**: Store user message in chat history
2. **Forgetting Rules**: Apply memory degradation to persona state
3. **Mood Rules**: Update mood based on conversation context
4. **Response Generation**: Use RAG pipeline to generate patient response
5. **State Storage**: Save patient response and updated persona state
6. **Return**: Provide both response and current persona state

## Example Output

```
User: Tell me about your family.
Patient: My husband used to say something like that. But that's nice to think about.
[Mood: happy, Confusion: 0.23]

User: What year is it?
Patient: Is it time for lunch? I thought we just had breakfast.
[Mood: comfortable, Confusion: 0.28]
```

## API Reference

### Main Chat Interface

```python
chat = DementiaSimulationChat()

# Primary chat function - returns (response, persona_state_dict)
response, state = chat.chat_loop(user_input: str) -> Tuple[str, Dict[str, Any]]

# Get full conversation history
history = chat.get_chat_history() -> List[Dict[str, Any]]

# Reset conversation
chat.reset_conversation()

# Save/load conversations
chat.save_conversation(filepath: str)
chat.load_conversation(filepath: str)
```

### Persona State Structure

```python
{
    "short_term_memory": ["recent", "topics"],
    "long_term_memory": ["older", "memories"],
    "forgotten_topics": ["forgotten", "items"],
    "confusion_level": 0.25,  # 0.0 to 1.0
    "current_mood": "happy",  # neutral, happy, sad, agitated, confused, etc.
    "mood_intensity": 0.7,   # 0.0 to 1.0
    "repetition_tendency": 0.3,
    "time_orientation": 0.8,
    "last_topics": ["recent", "conversation", "topics"],
    "preferred_topics": ["family", "past", "home"]
}
```

## Implementation Notes

- The system uses rule-based response generation for predictable, testable behavior
- Randomness is controlled to simulate natural variation in dementia symptoms
- Memory patterns follow research-based forgetting curves
- Mood changes are triggered by conversational context and content
- All components are designed to be easily extensible and modifiable

## Testing

The system includes comprehensive unit tests covering:
- Persona state management and serialization
- Chat message handling
- Forgetting and mood rule application
- RAG pipeline functionality
- Full chat system integration
- Conversation persistence

Run tests with: `python -m unittest tests.test_chat -v`