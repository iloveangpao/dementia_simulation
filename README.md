# Dementia Simulation Platform

A web-based platform for dementia simulation with chat interface and caregiver monitoring.

## Features

- **Chat Interface**: Interactive chat with simulated patient responses
- **Mood Tracker**: Real-time mood monitoring with visual feedback  
- **Caregiver Scores**: Performance tracking for empathy, communication, and patience

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the platform:
```bash
./start.sh
```

Or start components individually:

**Backend (FastAPI)**:
```bash
python backend/api.py
```

**Frontend (Streamlit)**:
```bash
streamlit run frontend/app.py
```

## Access Points

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Architecture

- **Frontend**: Streamlit-based UI with two-panel layout
- **Backend**: FastAPI with REST endpoints for chat, mood tracking, and scores
- **Data**: In-memory storage (can be extended to database)

## API Endpoints

- `POST /api/chat` - Send chat message and get response
- `POST /api/mood` - Update mood score
- `GET /api/caregiver-scores` - Get caregiver performance metrics