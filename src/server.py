"""
FastAPI server for dementia simulation with chat and evaluation endpoints.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="Dementia Simulation API",
    description="API for dementia patient simulation and caregiver evaluation",
    version="1.0.0"
)

# Pydantic schemas
class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    text: str

class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    patient_reply: str
    persona_mood: str

class EvaluateRequest(BaseModel):
    """Request schema for evaluate endpoint."""
    transcript: str

class EvaluateResponse(BaseModel):
    """Response schema for evaluate endpoint."""
    evaluation_result: Dict[str, Any]

# Mock dementia patient persona for simulation
class DementiaPatientSimulator:
    """Simple simulator for dementia patient responses."""
    
    def __init__(self):
        self.current_mood = "confused"
        self.mood_states = ["confused", "agitated", "calm", "anxious", "withdrawn"]
    
    def generate_response(self, caregiver_text: str) -> tuple[str, str]:
        """Generate patient response based on caregiver input."""
        caregiver_lower = caregiver_text.lower()
        
        # Simple response logic based on input
        if any(word in caregiver_lower for word in ["hello", "hi", "good morning"]):
            response = "Who are you? I don't recognize you..."
            self.current_mood = "confused"
        elif any(word in caregiver_lower for word in ["eat", "food", "lunch", "dinner"]):
            response = "I'm not hungry. I already ate... didn't I?"
            self.current_mood = "confused"
        elif any(word in caregiver_lower for word in ["calm", "relax", "okay"]):
            response = "I... I think I remember you. You're nice."
            self.current_mood = "calm"
        elif any(word in caregiver_lower for word in ["medicine", "pills", "doctor"]):
            response = "No! I don't need pills! Leave me alone!"
            self.current_mood = "agitated"
        elif any(word in caregiver_lower for word in ["name", "who"]):
            response = "My name? I... what's your name? Where am I?"
            self.current_mood = "anxious"
        else:
            response = "I don't understand. Everything is so confusing..."
            self.current_mood = "withdrawn"
        
        return response, self.current_mood

# Mock evaluator for caregiver performance
class CaregiverEvaluator:
    """Simple evaluator for caregiver transcript analysis."""
    
    def evaluate_transcript(self, transcript: str) -> Dict[str, Any]:
        """Evaluate caregiver performance based on transcript."""
        transcript_lower = transcript.lower()
        
        # Simple evaluation metrics
        positive_words = ["calm", "gentle", "understanding", "patient", "kind"]
        negative_words = ["force", "argue", "frustrated", "angry", "rush"]
        
        positive_count = sum(1 for word in positive_words if word in transcript_lower)
        negative_count = sum(1 for word in negative_words if word in transcript_lower)
        
        # Calculate basic scores
        empathy_score = min(10, max(0, positive_count * 2 - negative_count))
        communication_score = min(10, len(transcript.split()) // 10)  # Basic length consideration
        patience_score = max(0, 10 - negative_count * 2)
        
        overall_score = (empathy_score + communication_score + patience_score) / 3
        
        # Generate feedback
        feedback = []
        if positive_count > 0:
            feedback.append("Good use of positive communication techniques")
        if negative_count > 0:
            feedback.append("Consider avoiding confrontational language")
        if len(transcript.split()) < 20:
            feedback.append("Consider providing more detailed responses")
        
        return {
            "overall_score": round(overall_score, 2),
            "empathy_score": empathy_score,
            "communication_score": communication_score,
            "patience_score": patience_score,
            "feedback": feedback,
            "word_count": len(transcript.split()),
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }

# Initialize simulators
patient_simulator = DementiaPatientSimulator()
evaluator = CaregiverEvaluator()

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Dementia Simulation API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for interacting with dementia patient simulation.
    
    Args:
        request: ChatRequest containing the caregiver's text input
        
    Returns:
        ChatResponse with patient reply and current persona mood
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        logger.info(f"Received chat request: {request.text}")
        
        # Generate patient response
        patient_reply, persona_mood = patient_simulator.generate_response(request.text)
        
        response = ChatResponse(
            patient_reply=patient_reply,
            persona_mood=persona_mood
        )
        
        logger.info(f"Generated response: {patient_reply}, mood: {persona_mood}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(request: EvaluateRequest):
    """
    Evaluate endpoint for analyzing caregiver transcript performance.
    
    Args:
        request: EvaluateRequest containing the caregiver transcript
        
    Returns:
        EvaluateResponse with evaluation results and metrics
    """
    try:
        if not request.transcript or not request.transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript cannot be empty")
        
        logger.info(f"Received evaluation request for transcript length: {len(request.transcript)}")
        
        # Run evaluation on the transcript
        evaluation_result = evaluator.evaluate_transcript(request.transcript)
        
        response = EvaluateResponse(
            evaluation_result=evaluation_result
        )
        
        logger.info(f"Generated evaluation with overall score: {evaluation_result.get('overall_score')}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in evaluate endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)