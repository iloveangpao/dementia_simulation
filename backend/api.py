from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Dict
import random

app = FastAPI(title="Dementia Simulation API")

# Data models
class ChatMessage(BaseModel):
    message: str

class MoodUpdate(BaseModel):
    mood_score: int

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class CaregiverScores(BaseModel):
    empathy_score: float
    communication_score: float
    patience_score: float
    overall_score: float
    last_updated: str

# Mock data storage (in production, this would be a database)
caregiver_scores = {
    "empathy_score": 8.5,
    "communication_score": 7.8,
    "patience_score": 9.2,
    "overall_score": 8.5,
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

@app.get("/")
async def root():
    return {"message": "Dementia Simulation API"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Chat endpoint that processes user messages and returns responses"""
    responses = [
        "I understand you're feeling that way. Can you tell me more?",
        "That sounds challenging. How are you coping today?",
        "Thank you for sharing. What would help you feel better?",
        "I'm here to listen. Take your time.",
        "How has your day been so far?",
        "It's okay to feel confused sometimes. You're not alone.",
        "Can you describe what you're experiencing right now?",
        "Let's take this one step at a time together."
    ]
    
    response = random.choice(responses)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return ChatResponse(response=response, timestamp=timestamp)

@app.post("/api/mood")
async def update_mood(mood_update: MoodUpdate):
    """Update mood score"""
    # In production, this would save to database
    return {
        "status": "success", 
        "mood_score": mood_update.mood_score,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/caregiver-scores", response_model=CaregiverScores)
async def get_caregiver_scores():
    """Get current caregiver performance scores"""
    # Add some random variation to simulate real updates
    scores = caregiver_scores.copy()
    scores["empathy_score"] = round(scores["empathy_score"] + random.uniform(-0.2, 0.2), 1)
    scores["communication_score"] = round(scores["communication_score"] + random.uniform(-0.2, 0.2), 1)
    scores["patience_score"] = round(scores["patience_score"] + random.uniform(-0.2, 0.2), 1)
    scores["overall_score"] = round((scores["empathy_score"] + scores["communication_score"] + scores["patience_score"]) / 3, 1)
    scores["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return CaregiverScores(**scores)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)