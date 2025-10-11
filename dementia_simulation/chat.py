"""Chat module for LLM-based conversation flow in dementia simulation."""

import random
from typing import List, Dict, Any, Optional, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .persona import Persona, MoodState
from .retriever import MemoryRetriever, Document


class LLMProvider(Protocol):
    """Protocol for LLM providers."""
    
    def generate_response(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate a response from the LLM."""
        ...


class MockLLM:
    """Mock LLM for testing purposes."""
    
    def __init__(self, responses: Optional[List[str]] = None):
        """Initialize with predefined responses or use defaults."""
        self.responses = responses or [
            "I understand what you're saying.",
            "That sounds interesting.",
            "Can you tell me more about that?",
            "I'm not sure I remember that clearly.",
            "That reminds me of something, but I can't quite recall.",
            "I feel a bit confused right now.",
            "Could you repeat that please?",
            "I think I know what you mean.",
        ]
        self.call_count = 0
    
    def generate_response(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate a mock response."""
        self.call_count += 1
        
        # Return responses cyclically or randomly
        if len(self.responses) == 1:
            return self.responses[0]
        
        return self.responses[self.call_count % len(self.responses)]


@dataclass
class ChatMessage:
    """Represents a chat message."""
    content: str
    sender: str  # "user" or "persona"
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ChatFlow:
    """Manages conversation flow for dementia simulation."""
    
    def __init__(self, persona: Persona, llm_provider: LLMProvider, 
                 memory_retriever: Optional[MemoryRetriever] = None):
        """Initialize chat flow with persona and LLM provider."""
        self.persona = persona
        self.llm_provider = llm_provider
        self.memory_retriever = memory_retriever or MemoryRetriever()
        self.conversation_history: List[ChatMessage] = []
        self.context_window = 5  # Number of recent messages to include in context
    
    def _build_context_prompt(self, user_message: str) -> str:
        """Build context prompt for LLM including persona state and recent history."""
        prompt_parts = []
        
        # Persona context
        prompt_parts.append(f"You are {self.persona.name}, a person with dementia (severity: {self.persona.dementia_severity:.1f}).")
        prompt_parts.append(f"Current mood: {self.persona.current_mood.value}")
        
        # Mood-specific behavior
        mood_behaviors = {
            MoodState.CONFUSED: "You often lose track of conversations and ask for clarification.",
            MoodState.AGITATED: "You may become frustrated or upset easily.",
            MoodState.ANXIOUS: "You feel worried and seek reassurance.",
            MoodState.SAD: "You feel down and may not be very responsive.",
            MoodState.HAPPY: "You are cheerful and engaged in conversation.",
            MoodState.CALM: "You are peaceful and speak thoughtfully."
        }
        
        if self.persona.current_mood in mood_behaviors:
            prompt_parts.append(mood_behaviors[self.persona.current_mood])
        
        # Recent conversation history
        if self.conversation_history:
            prompt_parts.append("\nRecent conversation:")
            recent_messages = self.conversation_history[-self.context_window:]
            for msg in recent_messages:
                prompt_parts.append(f"{msg.sender}: {msg.content}")
        
        # Accessible memories
        accessible_memories = self.persona.get_accessible_memories(user_message)
        if accessible_memories:
            prompt_parts.append("\nRelevant memories you can access:")
            for memory in accessible_memories[:3]:  # Limit to 3 most relevant
                prompt_parts.append(f"- {memory.content}")
        
        # Current user message
        prompt_parts.append(f"\nUser: {user_message}")
        prompt_parts.append(f"\n{self.persona.name}:")
        
        return "\n".join(prompt_parts)
    
    def process_user_message(self, message: str) -> str:
        """Process user message and generate persona response."""
        import time
        
        # Add user message to history
        user_msg = ChatMessage(
            content=message,
            sender="user",
            timestamp=time.time()
        )
        self.conversation_history.append(user_msg)
        
        # Update persona mood (conversation can trigger mood changes)
        self.persona.update_mood(trigger_event="conversation")
        
        # Create memory of the interaction
        self.persona.add_memory(
            content=f"User said: {message}",
            importance=0.6,
            memory_type="conversation"
        )
        
        # Build context and generate response
        context_prompt = self._build_context_prompt(message)
        response = self.llm_provider.generate_response(context_prompt)
        
        # Add persona response to history
        persona_msg = ChatMessage(
            content=response,
            sender="persona",
            timestamp=time.time(),
            metadata={"mood": self.persona.current_mood.value}
        )
        self.conversation_history.append(persona_msg)
        
        # Create memory of own response
        self.persona.add_memory(
            content=f"I responded: {response}",
            importance=0.5,
            memory_type="conversation"
        )
        
        # Occasionally forget memories during conversation
        if random.random() < 0.1:  # 10% chance
            forgotten = self.persona.forget_memories()
            if forgotten:
                print(f"[DEBUG] {self.persona.name} forgot {len(forgotten)} memories")
        
        return response
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation state."""
        return {
            "message_count": len(self.conversation_history),
            "persona_mood": self.persona.current_mood.value,
            "accessible_memories": len(self.persona.get_accessible_memories()),
            "total_memories": len(self.persona.memories),
            "dementia_severity": self.persona.dementia_severity
        }
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
    
    def add_memory_context(self, documents: List[Document]):
        """Add documents to memory retriever for context."""
        self.memory_retriever.add_documents(documents)
    
    def simulate_memory_degradation(self):
        """Simulate progressive memory degradation."""
        forgotten = self.persona.forget_memories(time_threshold=1800)  # 30 minutes
        return len(forgotten)