"""
FastAPI server for the dementia simulation chatbot.

This module provides a REST API for interacting with the dementia simulation
system, including endpoints for chat, persona management, and evaluation.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from loguru import logger
from pydantic import BaseModel, Field

from ..evaluator.empathy_evaluator import EmpathyEvaluator

# Import local modules
from ..persona.models import DementiaPersona, create_sample_personas
from ..rag.pipeline import DementiaRAGPipeline
from ..retriever.faiss_retriever import (
    FAISSRetriever,
    initialize_retriever_with_knowledge_base,
)
from ..session.store import InMemorySessionStore, SessionStore
from ..telemetry.logger import TelemetryLogger
from ..telemetry.metrics import MetricsCollector


# Pydantic models for API
class ChatMessage(BaseModel):
    """Chat message model."""

    message: str = Field(..., description="The message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request model."""

    message: Optional[str] = Field(None, description="User's message")
    text: Optional[str] = Field(None, description="User's text (alias for message)")
    persona_id: Optional[str] = Field(None, description="Persona ID to use")
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation tracking"
    )

    def get_message_text(self) -> str:
        """Get the message text from either field."""
        return self.message or self.text or ""


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str = Field(..., description="Generated response")
    reply: Optional[str] = Field(None, description="Reply (alias for response)")
    persona_mood: str = Field(..., description="Current persona mood")
    mood: Optional[str] = Field(None, description="Mood (alias for persona_mood)")
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

    conversation_history: Optional[List[Dict[str, Any]]] = Field(
        None, description="Conversation history"
    )
    caregiver_responses: Optional[List[str]] = Field(
        None, description="Caregiver responses to evaluate"
    )
    transcript: Optional[str] = Field(
        None, description="Transcript text to evaluate"
    )

    def get_caregiver_responses(self) -> List[str]:
        """Extract caregiver responses from transcript or list."""
        if self.caregiver_responses:
            return self.caregiver_responses
        if self.transcript:
            # Split transcript into sentences as caregiver responses
            import re
            sentences = re.split(r'[.!?]+', self.transcript)
            return [s.strip() for s in sentences if s.strip()]
        return []

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get or construct conversation history."""
        if self.conversation_history:
            return self.conversation_history
        # Construct from transcript if available
        responses = self.get_caregiver_responses()
        return [
            {"speaker": "caregiver", "message": msg}
            for msg in responses
        ]


class EvaluationResponse(BaseModel):
    """Evaluation response model."""

    overall_empathy_score: float = Field(..., description="Overall empathy score")
    overall_score: Optional[float] = Field(None, description="Overall score (alias)")
    detailed_scores: Dict[str, float] = Field(
        ..., description="Detailed evaluation scores"
    )
    flags: Optional[Dict[str, Any]] = Field(None, description="Evaluation flags")
    feedback: List[str] = Field(..., description="Feedback and suggestions")
    strengths: List[str] = Field(..., description="Identified strengths")
    improvements: List[str] = Field(..., description="Areas for improvement")


# Global state management
class AppState:
    """Application state management."""

    def __init__(self):
        self.rag_pipeline: Optional[DementiaRAGPipeline] = None
        self.personas: Dict[str, DementiaPersona] = {}
        self.session_store: Optional[SessionStore] = None
        self.evaluator: Optional[EmpathyEvaluator] = None
        self.telemetry_logger: Optional[TelemetryLogger] = None
        self.metrics: Optional[MetricsCollector] = None
        self.initialized = False
        self.turn_counters: Dict[str, int] = {}

    async def initialize(self):
        """Initialize the application components."""
        if self.initialized:
            return

        logger.info("Initializing application components...")

        # Initialize session store with TTL
        ttl_seconds = int(os.getenv("SESSION_TTL_SECONDS", 3600))
        self.session_store = InMemorySessionStore(ttl_seconds=ttl_seconds)

        # Initialize telemetry
        self.telemetry_logger = TelemetryLogger()
        self.metrics = MetricsCollector()

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
        session = self.session_store.get_or_create(session_id)

        # Track new session
        if session_id not in self.turn_counters:
            self.turn_counters[session_id] = 0
            self.metrics.increment("total_sessions")
            self.metrics.set_counter(
                "active_sessions", len(self.session_store.list_all())
            )
            self.telemetry_logger.log_event("session_start", session_id)

        return session


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

    # Get message text from either field
    message_text = request.get_message_text()
    if not message_text or not message_text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    # Generate response
    try:
        rag_response = await state.rag_pipeline.generate_response(
            user_input=message_text,
            persona=persona,
            conversation_history=session["messages"],
        )

        # Increment turn counter
        state.turn_counters[session_id] = state.turn_counters.get(session_id, 0) + 1
        turn_number = state.turn_counters[session_id]

        # Add messages to session
        session["messages"].append(
            {
                "speaker": "caregiver",
                "message": message_text,
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

        # Update session in store
        state.session_store.set(session_id, session)

        # Log telemetry
        persona_state = {
            "mood": rag_response.persona_mood,
            "stage": persona.stage.value,
            "name": persona.name,
        }
        retrieval_hits = [
            {
                "text": (
                    str(doc.get("text", ""))[:100]
                    if isinstance(doc, dict)
                    else str(doc)[:100]
                ),
                "score": doc.get("score", 0.0) if isinstance(doc, dict) else 0.0,
            }
            for doc in rag_response.retrieved_documents
        ]
        flags = {
            "low_confidence": rag_response.confidence_score < 0.5,
            "long_processing": rag_response.processing_time > 2.0,
        }
        state.telemetry_logger.log_turn(
            session_id=session_id,
            turn_number=turn_number,
            user_input=message_text,
            response=rag_response.response_text,
            persona_state=persona_state,
            retrieval_hits=retrieval_hits,
            flags=flags,
            metadata={
                "model_used": rag_response.model_used,
                "processing_time": rag_response.processing_time,
            },
        )

        # Update metrics
        state.metrics.increment("total_turns")
        state.metrics.increment(
            "total_retrievals", len(rag_response.retrieved_documents)
        )
        if flags["low_confidence"]:
            state.metrics.increment_flag("low_confidence")

        return ChatResponse(
            response=rag_response.response_text,
            reply=rag_response.response_text,  # Alias
            persona_mood=rag_response.persona_mood,
            mood=rag_response.persona_mood,  # Alias
            confidence_score=rag_response.confidence_score,
            processing_time=rag_response.processing_time,
            model_used=rag_response.model_used,
            retrieved_docs=len(rag_response.retrieved_documents),
            session_id=session_id,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        state.metrics.increment("total_errors")
        state.telemetry_logger.log_event(
            "error", session_id, {"error": str(e), "endpoint": "chat"}
        )
        raise HTTPException(status_code=500, detail="Error generating response") from e


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_empathy(
    request: EvaluationRequest, state: AppState = Depends(ensure_initialized)
):
    """
    Evaluate caregiver empathy based on conversation.
    Accepts either conversation_history + caregiver_responses or a transcript string.
    """
    try:
        # Get conversation data from request
        conversation_history = request.get_conversation_history()
        caregiver_responses = request.get_caregiver_responses()

        if not caregiver_responses:
            raise HTTPException(
                status_code=400,
                detail="No caregiver responses to evaluate. "
                "Provide transcript or caregiver_responses.",
            )

        evaluation = await state.evaluator.evaluate_conversation(
            conversation_history=conversation_history,
            caregiver_responses=caregiver_responses,
        )

        # Create flags from detailed scores
        flags = {
            "low_validation": evaluation["detailed_scores"].get("validation", 0) < 0.5,
            "low_patience": evaluation["detailed_scores"].get("patience", 0) < 0.5,
            "needs_improvement": len(evaluation.get("improvements", [])) > 2,
        }

        # Update metrics
        state.metrics.increment("total_evaluations")
        if flags["low_validation"]:
            state.metrics.increment_flag("low_empathy")

        return EvaluationResponse(
            overall_empathy_score=evaluation["overall_score"],
            overall_score=evaluation["overall_score"],  # Alias
            detailed_scores=evaluation["detailed_scores"],
            flags=flags,
            feedback=evaluation["feedback"],
            strengths=evaluation["strengths"],
            improvements=evaluation["improvements"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        state.metrics.increment("total_errors")
        raise HTTPException(status_code=500, detail="Error evaluating empathy") from e


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, state: AppState = Depends(ensure_initialized)):
    """Get conversation session information."""
    session = state.session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

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
    if not state.session_store.delete(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    if session_id in state.turn_counters:
        del state.turn_counters[session_id]

    state.telemetry_logger.log_event("session_end", session_id)
    state.metrics.set_counter("active_sessions", len(state.session_store.list_all()))

    return {"message": "Session deleted successfully"}


@app.get("/stats")
async def get_stats(state: AppState = Depends(ensure_initialized)):
    """Get system statistics."""
    stats = {
        "total_personas": len(state.personas),
        "active_sessions": len(state.session_store.list_all()),
        "pipeline_stats": state.rag_pipeline.get_pipeline_stats()
        if state.rag_pipeline
        else {},
        "uptime": datetime.now().isoformat(),
    }
    return stats


@app.post("/reset")
async def reset_sessions(state: AppState = Depends(ensure_initialized)):
    """Reset all sessions and clear session store."""
    count = state.session_store.clear()
    state.turn_counters.clear()
    state.telemetry_logger.log_event("reset", data={"sessions_cleared": count})
    state.metrics.set_counter("active_sessions", 0)
    return {
        "message": "All sessions reset successfully",
        "sessions_cleared": count,
    }


@app.get("/export", response_class=PlainTextResponse)
async def export_transcript(
    session_id: str = Query(..., description="Session ID to export"),
    state: AppState = Depends(ensure_initialized),
):
    """Export conversation transcript in JSONL format."""
    session = state.session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Build JSONL output
    lines = []
    for message in session["messages"]:
        line = json.dumps(message, ensure_ascii=False)
        lines.append(line)

    return "\n".join(lines)


@app.get("/metrics/quick")
async def get_quick_metrics(state: AppState = Depends(ensure_initialized)):
    """Get quick metrics for CI/nightly dashboards."""
    metrics = state.metrics.get_metrics()

    # Add additional computed metrics
    metrics["sessions_with_turns"] = len(state.turn_counters)
    metrics["avg_turns_per_session"] = (
        metrics["counters"]["total_turns"] / max(1, metrics["sessions_with_turns"])
    )

    return metrics


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
