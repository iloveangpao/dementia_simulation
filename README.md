# Dementia Simulation API

A FastAPI-based server for dementia patient simulation and caregiver evaluation.

## Features

- **Chat Endpoint**: Simulates conversations with a dementia patient
- **Evaluation Endpoint**: Evaluates caregiver performance based on conversation transcripts
- **Pydantic Validation**: All endpoints use Pydantic schemas for request/response validation
- **Mood Tracking**: Patient responses include mood states (confused, agitated, calm, anxious, withdrawn)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python src/server.py
```

Or using the run script:
```bash
python run_server.py
```

## API Endpoints

### POST /chat

Interact with the dementia patient simulation.

**Request:**
```json
{
  "text": "Hello, how are you feeling today?"
}
```

**Response:**
```json
{
  "patient_reply": "Who are you? I don't recognize you...",
  "persona_mood": "confused"
}
```

### POST /evaluate

Evaluate caregiver performance based on conversation transcript.

**Request:**
```json
{
  "transcript": "I spoke to the patient with calm and gentle words, showing understanding and patience throughout our conversation."
}
```

**Response:**
```json
{
  "evaluation_result": {
    "overall_score": 6.67,
    "empathy_score": 8,
    "communication_score": 2,
    "patience_score": 10,
    "feedback": ["Good use of positive communication techniques"],
    "word_count": 27,
    "positive_indicators": 4,
    "negative_indicators": 0
  }
}
```

## Testing

Run the test suite:
```bash
python test_server.py
```

## API Documentation

Once the server is running, visit:
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc