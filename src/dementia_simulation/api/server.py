"""
FastAPI server for the dementia simulation chatbot.

This module provides a REST API for interacting with the dementia simulation
system, including endpoints for chat, persona management, and evaluation.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uvicorn
from loguru import logger
import os

# Import local modules
from ..persona.models import DementiaPersona, create_sample_personas
from ..rag.pipeline import DementiaRAGPipeline
from ..retriever.faiss_retriever import (
    FAISSRetriever,
    initialize_retriever_with_knowledge_base,
)
from ..evaluator.empathy_evaluator import EmpathyEvaluator


# Pydantic models for API
class ChatMessage(BaseModel):
    """Chat message model."""

    message: str = Field(..., description="The message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., description="User's message")
    persona_id: Optional[str] = Field(None, description="Persona ID to use")
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation tracking"
    )


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str = Field(..., description="Generated response")
    persona_mood: str = Field(..., description="Current persona mood")
    confidence_score: float = Field(..., description="Response confidence")
    processing_time: float = Field(..., description="Processing time in seconds")
    model_used: str = Field(..., description="Model used for generation")
    retrieved_docs: int = Field(..., description="Number of retrieved documents")
    session_id: str = Field(..., description="Session ID")


class PersonaInfo(BaseModel):
    """Persona information model."""

    id: str = Field(..., description="Persona ID")
    name: str = Field(..., description="Persona name")
    age: int = Field(..., description="Persona age")
    stage: str = Field(..., description="Dementia stage")
    current_mood: str = Field(..., description="Current mood")
    background: Dict[str, str] = Field(..., description="Background information")


class EvaluationRequest(BaseModel):
    """Evaluation request model."""

    conversation_history: List[Dict[str, Any]] = Field(
        ..., description="Conversation history"
    )
    caregiver_responses: List[str] = Field(
        ..., description="Caregiver responses to evaluate"
    )


class EvaluationResponse(BaseModel):
    """Evaluation response model."""

    overall_empathy_score: float = Field(..., description="Overall empathy score")
    detailed_scores: Dict[str, float] = Field(
        ..., description="Detailed evaluation scores"
    )
    feedback: List[str] = Field(..., description="Feedback and suggestions")
    strengths: List[str] = Field(..., description="Identified strengths")
    improvements: List[str] = Field(..., description="Areas for improvement")


# Global state management
class AppState:
    """Application state management."""

    def __init__(self):
        self.rag_pipeline: Optional[DementiaRAGPipeline] = None
        self.personas: Dict[str, DementiaPersona] = {}
        self.sessions: Dict[str, Dict] = {}
        self.evaluator: Optional[EmpathyEvaluator] = None
        self.initialized = False

    async def initialize(self):
        """Initialize the application components."""
        if self.initialized:
            return

        logger.info("Initializing application components...")

        # Initialize retriever
        retriever = FAISSRetriever()
        initialize_retriever_with_knowledge_base(retriever)

        # Initialize RAG pipeline
        use_openai = os.getenv("OPENAI_API_KEY") is not None
        self.rag_pipeline = DementiaRAGPipeline(
            retriever=retriever, use_openai=use_openai
        )

        # Load sample personas
        sample_personas = create_sample_personas()
        for i, persona in enumerate(sample_personas):
            persona_id = f"persona_{i+1}"
            self.personas[persona_id] = persona

        # Initialize evaluator
        self.evaluator = EmpathyEvaluator()

        self.initialized = True
        logger.info("Application initialized successfully")

    def get_or_create_session(self, session_id: str) -> Dict:
        """Get or create a conversation session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "messages": [],
                "current_persona": None,
            }
        return self.sessions[session_id]


# Global app state
app_state = AppState()

# FastAPI app
app = FastAPI(
    title="Dementia Simulation Chatbot API",
    description="API for dementia patient simulation and caregiver training",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to ensure initialization
async def ensure_initialized():
    """Ensure the application is initialized."""
    await app_state.initialize()
    return app_state


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    await app_state.initialize()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information."""
    return """
    <html>
        <head>
            <title>Dementia Simulation Chatbot</title>
        </head>
        <body>
            <h1>Dementia Simulation Chatbot API</h1>
            <p>Welcome to the Dementia Simulation Chatbot API!</p>
            <p>Available endpoints:</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/personas">Available Personas</a></li>
            </ul>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "initialized": app_state.initialized,
    }


@app.get("/personas", response_model=List[PersonaInfo])
async def get_personas(state: AppState = Depends(ensure_initialized)):
    """Get all available personas."""
    personas = []
    for persona_id, persona in state.personas.items():
        personas.append(
            PersonaInfo(
                id=persona_id,
                name=persona.name,
                age=persona.age,
                stage=persona.stage.value,
                current_mood=persona.current_mood.value,
                background=persona.background,
            )
        )
    return personas


@app.get("/personas/{persona_id}", response_model=PersonaInfo)
async def get_persona(persona_id: str, state: AppState = Depends(ensure_initialized)):
    """Get specific persona information."""
    if persona_id not in state.personas:
        raise HTTPException(status_code=404, detail="Persona not found")

    persona = state.personas[persona_id]
    return PersonaInfo(
        id=persona_id,
        name=persona.name,
        age=persona.age,
        stage=persona.stage.value,
        current_mood=persona.current_mood.value,
        background=persona.background,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, state: AppState = Depends(ensure_initialized)):
    """
    Chat with a dementia persona.
    """
    # Generate session ID if not provided
    session_id = request.session_id or f"session_{datetime.now().timestamp()}"

    # Get or create session
    session = state.get_or_create_session(session_id)

    # Get persona (default to first persona if not specified)
    persona_id = request.persona_id or list(state.personas.keys())[0]
    if persona_id not in state.personas:
        raise HTTPException(status_code=404, detail="Persona not found")

    persona = state.personas[persona_id]
    session["current_persona"] = persona_id

    # Generate response
    try:
        rag_response = await state.rag_pipeline.generate_response(
            user_input=request.message,
            persona=persona,
            conversation_history=session["messages"],
        )

        # Add messages to session
        session["messages"].append(
            {
                "speaker": "caregiver",
                "message": request.message,
                "timestamp": datetime.now().isoformat(),
            }
        )
        session["messages"].append(
            {
                "speaker": "patient",
                "message": rag_response.response_text,
                "timestamp": datetime.now().isoformat(),
                "mood": rag_response.persona_mood,
            }
        )

        return ChatResponse(
            response=rag_response.response_text,
            persona_mood=rag_response.persona_mood,
            confidence_score=rag_response.confidence_score,
            processing_time=rag_response.processing_time,
            model_used=rag_response.model_used,
            retrieved_docs=len(rag_response.retrieved_documents),
            session_id=session_id,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Error generating response")


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_empathy(
    request: EvaluationRequest, state: AppState = Depends(ensure_initialized)
):
    """
    Evaluate caregiver empathy based on conversation.
    """
    try:
        evaluation = await state.evaluator.evaluate_conversation(
            conversation_history=request.conversation_history,
            caregiver_responses=request.caregiver_responses,
        )

        return EvaluationResponse(
            overall_empathy_score=evaluation["overall_score"],
            detailed_scores=evaluation["detailed_scores"],
            feedback=evaluation["feedback"],
            strengths=evaluation["strengths"],
            improvements=evaluation["improvements"],
        )

    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail="Error evaluating empathy")


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, state: AppState = Depends(ensure_initialized)):
    """Get conversation session information."""
    if session_id not in state.sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = state.sessions[session_id]
    return {
        "session_id": session_id,
        "created_at": session["created_at"],
        "message_count": len(session["messages"]),
        "current_persona": session.get("current_persona"),
        "messages": session["messages"],
    }


@app.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str, state: AppState = Depends(ensure_initialized)
):
    """Delete a conversation session."""
    if session_id not in state.sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del state.sessions[session_id]
    return {"message": "Session deleted successfully"}


@app.get("/stats")
async def get_stats(state: AppState = Depends(ensure_initialized)):
    """Get system statistics."""
    stats = {
        "total_personas": len(state.personas),
        "active_sessions": len(state.sessions),
        "pipeline_stats": state.rag_pipeline.get_pipeline_stats()
        if state.rag_pipeline
        else {},
        "uptime": datetime.now().isoformat(),
    }
    return stats


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/api.log", rotation="1 day", retention="7 days")

    # Run the server
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "localhost")

    uvicorn.run(
        "dementia_simulation.api.server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
