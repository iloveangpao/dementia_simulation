# Dementia Simulation Frontend

This directory contains the Streamlit-based web interface for the Dementia Simulation Chatbot.

## Overview

The frontend provides an intuitive two-panel layout for practicing empathetic communication with AI-powered dementia patient personas.

## Features

### Two-Panel Layout

#### Left Panel - Chat Interface
- **Real-time Chat**: Interactive conversation with dementia personas
- **Message History**: Scrollable chat container showing full conversation
- **Visual Indicators**: 
  - User messages displayed on the right (green background)
  - AI patient messages on the left (gray background)
  - Mood emoji indicators for patient responses
- **Input Area**: Text area for composing messages
- **Current Persona Info**: Display of active persona and their mood

#### Right Panel - Monitoring
- **Session Statistics**:
  - Conversation duration
  - Total messages exchanged
  - Number of caregiver responses
  
- **Mood Tracker**:
  - Large emoji visualization of patient's current mood
  - Mood label (calm, confused, agitated, etc.)
  
- **Performance Scores**:
  - Overall empathy score with color coding:
    - Green (≥0.8): Excellent
    - Yellow (0.6-0.8): Good
    - Red (<0.6): Needs Work
  - Detailed metrics with progress bars:
    - Validation
    - Emotional Support
    - Respect & Dignity
    - Patience
    - Communication Clarity
    - Non-confrontational approach
  
- **Feedback**:
  - Expandable "Strengths" section
  - Expandable "Improvements" section
  
- **Progress Chart**:
  - Line graph showing score improvement over multiple evaluations

### Sidebar Features

- **Persona Selection**: Dropdown to choose dementia stage (mild/moderate/severe)
- **Session Controls**:
  - Clear conversation button
  - Evaluate empathy button
- **Contextual Tips**: Stage-specific communication guidelines
- **Help Section**: Expandable guidelines and evaluation metrics

## Running the Frontend

### Option 1: Using Poetry
```bash
cd /path/to/dementia_simulation
poetry run dementia-sim streamlit
```

### Option 2: Direct Streamlit
```bash
cd frontend
streamlit run streamlit_app.py
```

The app will open at http://localhost:8501

## Architecture

### Components

1. **Session State Management**
   - `conversation_history`: List of all messages
   - `current_persona`: Active dementia persona
   - `caregiver_responses`: User messages for evaluation
   - `evaluation_history`: Past empathy evaluations
   - `session_start`: Start time for duration tracking

2. **Integration with Backend**
   - Direct imports from `src/dementia_simulation/`
   - RAG Pipeline: Generates AI responses
   - Persona Models: Manages patient states
   - Empathy Evaluator: Scores caregiver responses

3. **UI Components**
   - `initialize_components()`: Cached initialization of AI components
   - `initialize_session_state()`: Setup session variables
   - `display_persona_card()`: Render persona information
   - `display_chat_message()`: Render individual chat messages
   - `display_empathy_scores()`: Render evaluation results
   - `main()`: Primary application flow

### Async Handling

The frontend uses asyncio to handle async operations from the backend:
```python
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
response = loop.run_until_complete(
    rag_pipeline.generate_response(...)
)
loop.close()
```

## Custom Styling

The app includes custom CSS for enhanced visuals:
- `.persona-card`: Persona information display
- `.chat-message`: Base message styling
- `.user-message`: Caregiver messages (right-aligned, green)
- `.bot-message`: Patient messages (left-aligned, gray)
- `.empathy-score`: Score display cards
- Color-coded score classes (excellent/good/needs-improvement)

## Dependencies

Core dependencies (from `pyproject.toml`):
- `streamlit>=1.28.1` - Web framework
- `pandas>=2.1.3` - Data handling
- `plotly>=5.x` - Charts and visualizations (via streamlit)
- Backend components from `dementia_simulation` package

## Testing

Frontend tests are located in `tests/unit/test_frontend.py`:
- Import verification
- File structure validation
- Component presence checks
- Integration with backend modules
- Layout verification

Run tests:
```bash
poetry run pytest tests/unit/test_frontend.py -v
```

## Future Enhancements

Potential improvements:
- [ ] Connect to FastAPI endpoints instead of direct imports
- [ ] Add conversation export functionality
- [ ] Implement user authentication
- [ ] Add multi-session management
- [ ] Real-time collaborative features
- [ ] Mobile-responsive layout improvements
- [ ] Audio/voice interaction support
- [ ] Progress tracking across sessions
- [ ] Custom persona creation interface

## Troubleshooting

### Common Issues

**"Failed to initialize components"**
- Ensure knowledge base is built: `python build_index.py`
- Check that `data/knowledge_base/` contains documents

**"Module not found" errors**
- Run: `poetry install --with dev`
- Verify Python version >= 3.10

**Slow response generation**
- First run downloads models (this is normal)
- Set `OPENAI_API_KEY` for faster responses
- Reduce conversation history if memory is an issue

## Contributing

When modifying the frontend:
1. Keep the two-panel layout structure
2. Maintain session state consistency
3. Test with different persona stages
4. Ensure responsive design
5. Update tests for new features
6. Run linting: `poetry run ruff check frontend/`
7. Format code: `poetry run ruff format frontend/`
