"""Persona module for dementia simulation with memory forgetting and mood updates."""

import random
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class MoodState(Enum):
    """Possible mood states for a persona."""
    HAPPY = "happy"
    SAD = "sad"
    CONFUSED = "confused"
    ANXIOUS = "anxious"
    CALM = "calm"
    AGITATED = "agitated"


@dataclass
class Memory:
    """Represents a memory with importance and timestamp."""
    content: str
    importance: float  # 0.0 to 1.0
    timestamp: float
    memory_type: str = "general"
    
    def age_in_seconds(self) -> float:
        """Get the age of the memory in seconds."""
        return time.time() - self.timestamp


@dataclass
class Persona:
    """Represents a persona with memory and mood management."""
    name: str
    dementia_severity: float = 0.5  # 0.0 = no dementia, 1.0 = severe
    current_mood: MoodState = MoodState.CALM
    memories: List[Memory] = field(default_factory=list)
    mood_stability: float = 0.7  # How stable the mood is (0.0 = very unstable)
    
    def add_memory(self, content: str, importance: float = 0.5, memory_type: str = "general"):
        """Add a new memory to the persona."""
        memory = Memory(
            content=content,
            importance=importance,
            timestamp=time.time(),
            memory_type=memory_type
        )
        self.memories.append(memory)
    
    def forget_memories(self, time_threshold: float = 3600) -> List[Memory]:
        """
        Forget memories based on dementia severity, importance, and age.
        Returns list of forgotten memories.
        """
        forgotten = []
        remaining = []
        
        for memory in self.memories:
            # Calculate forgetting probability based on multiple factors
            age_factor = min(memory.age_in_seconds() / time_threshold, 1.0)
            importance_factor = 1.0 - memory.importance
            dementia_factor = self.dementia_severity
            
            # Combined forgetting probability
            forget_probability = (age_factor * 0.4 + 
                                importance_factor * 0.3 + 
                                dementia_factor * 0.3)
            
            if random.random() < forget_probability:
                forgotten.append(memory)
            else:
                remaining.append(memory)
        
        self.memories = remaining
        return forgotten
    
    def update_mood(self, trigger_event: Optional[str] = None) -> MoodState:
        """
        Update mood based on current state, dementia severity, and optional trigger.
        """
        old_mood = self.current_mood
        
        # Base mood change probability
        change_probability = (1.0 - self.mood_stability) * 0.5
        
        # Dementia increases mood instability
        change_probability += self.dementia_severity * 0.3
        
        # Trigger events can force mood changes
        if trigger_event:
            change_probability += 0.4
        
        if random.random() < change_probability:
            # Choose new mood based on dementia severity
            if self.dementia_severity > 0.7:
                # High dementia: more likely confused/agitated
                mood_weights = {
                    MoodState.CONFUSED: 0.3,
                    MoodState.AGITATED: 0.25,
                    MoodState.ANXIOUS: 0.2,
                    MoodState.SAD: 0.15,
                    MoodState.CALM: 0.05,
                    MoodState.HAPPY: 0.05
                }
            elif self.dementia_severity > 0.3:
                # Moderate dementia: mixed moods
                mood_weights = {
                    MoodState.CONFUSED: 0.2,
                    MoodState.CALM: 0.2,
                    MoodState.ANXIOUS: 0.15,
                    MoodState.SAD: 0.15,
                    MoodState.HAPPY: 0.15,
                    MoodState.AGITATED: 0.15
                }
            else:
                # Low dementia: more stable moods
                mood_weights = {
                    MoodState.CALM: 0.3,
                    MoodState.HAPPY: 0.25,
                    MoodState.SAD: 0.15,
                    MoodState.CONFUSED: 0.1,
                    MoodState.ANXIOUS: 0.1,
                    MoodState.AGITATED: 0.1
                }
            
            # Select new mood based on weights
            moods = list(mood_weights.keys())
            weights = list(mood_weights.values())
            self.current_mood = random.choices(moods, weights=weights)[0]
        
        return self.current_mood
    
    def get_accessible_memories(self, query: Optional[str] = None) -> List[Memory]:
        """Get memories that are currently accessible (not forgotten)."""
        accessible = []
        
        for memory in self.memories:
            # Memory accessibility decreases with dementia severity and age
            age_penalty = min(memory.age_in_seconds() / 3600, 1.0) * 0.3
            dementia_penalty = self.dementia_severity * 0.4
            
            accessibility = memory.importance - age_penalty - dementia_penalty
            
            # Memory is accessible if above threshold
            if accessibility > 0.2:
                accessible.append(memory)
        
        # If query provided, filter relevant memories
        if query:
            relevant = []
            for memory in accessible:
                if query.lower() in memory.content.lower():
                    relevant.append(memory)
            return relevant
        
        return accessible