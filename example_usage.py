#!/usr/bin/env python3
"""
Usage example for PatientPersona class.

This script demonstrates how to use the PatientPersona class
in practical scenarios.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from persona import PatientPersona, DementiaStage, MoodState


def main():
    """Demonstrate PatientPersona usage."""
    print("PatientPersona Usage Example")
    print("=" * 30)
    
    # Create a patient with mild dementia
    patient = PatientPersona(
        name="Mary Johnson",
        dementia_stage=DementiaStage.MILD,
        initial_mood=MoodState.CALM
    )
    
    print(f"Created patient: {patient}")
    print(f"Initial status: {patient.get_status()}")
    
    # Add some personal information to memory
    print("\nAdding personal memories...")
    patient.add_memory_key("daughter_name", "Sarah")
    patient.add_memory_key("favorite_song", "Moon River")
    patient.add_memory_key("home_address", "123 Oak Street")
    patient.add_memory_key("wedding_anniversary", "June 15th")
    
    # Add some recent activities
    print("Adding recent activities...")
    patient.add_recent_memory("Had breakfast with oatmeal")
    patient.add_recent_memory("Nurse checked blood pressure")
    patient.add_recent_memory("Watched morning news")
    patient.add_recent_memory("Called daughter on phone")
    
    # Simulate daily interactions
    print("\nSimulating daily interactions:")
    print("-" * 35)
    
    for day in range(1, 4):
        print(f"\nDay {day}:")
        
        # Check if patient remembers key information
        daughter = patient.get_memory_key("daughter_name")
        song = patient.get_memory_key("favorite_song")
        address = patient.get_memory_key("home_address")
        
        print(f"  Remembers daughter's name: {daughter or 'Forgotten'}")
        print(f"  Remembers favorite song: {song or 'Forgotten'}")
        print(f"  Remembers home address: {address or 'Forgotten'}")
        
        # Update mood
        new_mood = patient.update_mood()
        print(f"  Current mood: {new_mood.value}")
        
        # Check recent memories and forget some
        print(f"  Recent memories before forgetting: {len(patient.recent_memories)}")
        forgotten = patient.forget_recent()
        if forgotten:
            print(f"  Forgot: {forgotten}")
        print(f"  Recent memories after forgetting: {len(patient.recent_memories)}")
        
        # Add new daily activity
        patient.add_recent_memory(f"Day {day} activity: Had lunch")
    
    print(f"\nFinal patient status:")
    final_status = patient.get_status()
    for key, value in final_status.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()