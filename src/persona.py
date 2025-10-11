"""
Persona module for dementia simulation.

This module implements the PatientPersona class that simulates a patient
with dementia, including memory degradation and mood states.
"""

import random
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class DementiaStage(Enum):
    """Enum representing different stages of dementia."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class MoodState(Enum):
    """Enum representing different mood states."""
    CALM = "calm"
    AGITATED = "agitated"
    WITHDRAWN = "withdrawn"


class PatientPersona:
    """
    A class representing a patient with dementia.
    
    This class simulates memory degradation, mood changes, and other
    characteristics associated with different stages of dementia.
    """
    
    def __init__(
        self, 
        name: str,
        dementia_stage: DementiaStage = DementiaStage.MILD,
        initial_mood: MoodState = MoodState.CALM
    ):
        """
        Initialize a PatientPersona.
        
        Args:
            name: The patient's name
            dementia_stage: The stage of dementia (mild, moderate, severe)
            initial_mood: The initial mood state
        """
        self.name = name
        self.dementia_stage = dementia_stage
        self.mood_state = initial_mood
        
        # Memory storage - keys that the patient remembers
        self.memory_keys: Dict[str, Any] = {}
        
        # Recent memories - stored with timestamps
        self.recent_memories: List[Dict[str, Any]] = []
        
        # Configure memory degradation based on dementia stage
        self._configure_memory_degradation()
        
        # Track mood change probability
        self._configure_mood_parameters()
    
    def _configure_memory_degradation(self) -> None:
        """Configure memory degradation parameters based on dementia stage."""
        if self.dementia_stage == DementiaStage.MILD:
            self.forget_probability = 0.1  # 10% chance to forget keys
            self.recent_memory_capacity = 20
            self.memory_retention_hours = 24
        elif self.dementia_stage == DementiaStage.MODERATE:
            self.forget_probability = 0.3  # 30% chance to forget keys
            self.recent_memory_capacity = 10
            self.memory_retention_hours = 8
        else:  # SEVERE
            self.forget_probability = 0.6  # 60% chance to forget keys
            self.recent_memory_capacity = 5
            self.memory_retention_hours = 2
    
    def _configure_mood_parameters(self) -> None:
        """Configure mood change parameters based on dementia stage."""
        if self.dementia_stage == DementiaStage.MILD:
            self.mood_change_probability = 0.1
        elif self.dementia_stage == DementiaStage.MODERATE:
            self.mood_change_probability = 0.3
        else:  # SEVERE
            self.mood_change_probability = 0.5
    
    def add_memory_key(self, key: str, value: Any) -> None:
        """
        Add a key-value pair to memory.
        
        Args:
            key: The memory key
            value: The associated value
        """
        self.memory_keys[key] = value
    
    def get_memory_key(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory, with chance of forgetting.
        
        Args:
            key: The memory key to retrieve
            
        Returns:
            The associated value or None if forgotten/not found
        """
        if key not in self.memory_keys:
            return None
        
        # Random chance to forget the key
        if random.random() < self.forget_probability:
            # Forget the key
            del self.memory_keys[key]
            return None
        
        return self.memory_keys[key]
    
    def add_recent_memory(self, memory: str) -> None:
        """
        Add a recent memory with timestamp.
        
        Args:
            memory: The memory content to store
        """
        memory_entry = {
            "content": memory,
            "timestamp": datetime.now()
        }
        
        self.recent_memories.append(memory_entry)
        
        # Remove oldest memories if capacity exceeded
        if len(self.recent_memories) > self.recent_memory_capacity:
            self.recent_memories = self.recent_memories[-self.recent_memory_capacity:]
    
    def forget_recent(self) -> List[str]:
        """
        Forget recent memories based on dementia stage and time.
        
        Returns:
            List of forgotten memory contents
        """
        current_time = datetime.now()
        forgotten_memories = []
        
        # Filter out memories older than retention period
        cutoff_time = current_time - timedelta(hours=self.memory_retention_hours)
        
        memories_to_keep = []
        for memory in self.recent_memories:
            if memory["timestamp"] >= cutoff_time:
                # Even recent memories might be forgotten randomly
                if random.random() < self.forget_probability:
                    forgotten_memories.append(memory["content"])
                else:
                    memories_to_keep.append(memory)
            else:
                # Old memories are definitely forgotten
                forgotten_memories.append(memory["content"])
        
        self.recent_memories = memories_to_keep
        return forgotten_memories
    
    def update_mood(self) -> MoodState:
        """
        Update the patient's mood state.
        
        The mood can change randomly based on dementia stage,
        with more severe stages having more frequent mood changes.
        
        Returns:
            The new mood state
        """
        # Check if mood should change
        if random.random() < self.mood_change_probability:
            # Choose a new mood state randomly
            possible_moods = [mood for mood in MoodState if mood != self.mood_state]
            if possible_moods:
                self.mood_state = random.choice(possible_moods)
        
        return self.mood_state
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the patient.
        
        Returns:
            Dictionary containing patient status information
        """
        return {
            "name": self.name,
            "dementia_stage": self.dementia_stage.value,
            "mood_state": self.mood_state.value,
            "memory_keys_count": len(self.memory_keys),
            "recent_memories_count": len(self.recent_memories),
            "forget_probability": self.forget_probability,
            "mood_change_probability": self.mood_change_probability
        }
    
    def __str__(self) -> str:
        """String representation of the patient."""
        return f"PatientPersona(name='{self.name}', stage={self.dementia_stage.value}, mood={self.mood_state.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the patient."""
        return self.__str__()