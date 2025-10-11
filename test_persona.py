#!/usr/bin/env python3
"""
Test script for PatientPersona implementation.

This script demonstrates and tests the functionality of the PatientPersona class.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from persona import PatientPersona, DementiaStage, MoodState


def test_patient_persona():
    """Test the PatientPersona implementation."""
    print("Testing PatientPersona Implementation")
    print("=" * 40)
    
    # Test 1: Create patients with different dementia stages
    print("\n1. Creating patients with different dementia stages:")
    
    mild_patient = PatientPersona("Alice", DementiaStage.MILD, MoodState.CALM)
    moderate_patient = PatientPersona("Bob", DementiaStage.MODERATE, MoodState.AGITATED)
    severe_patient = PatientPersona("Charlie", DementiaStage.SEVERE, MoodState.WITHDRAWN)
    
    patients = [mild_patient, moderate_patient, severe_patient]
    
    for patient in patients:
        print(f"  {patient}")
        status = patient.get_status()
        print(f"    Memory capacity: {status['recent_memories_count']} memories")
        print(f"    Forget probability: {status['forget_probability']:.1%}")
        print(f"    Mood change probability: {status['mood_change_probability']:.1%}")
    
    # Test 2: Test memory key functionality
    print("\n2. Testing memory key functionality:")
    
    test_patient = mild_patient
    test_patient.add_memory_key("favorite_color", "blue")
    test_patient.add_memory_key("pet_name", "Fluffy")
    test_patient.add_memory_key("hometown", "Springfield")
    
    print(f"  Added 3 memory keys to {test_patient.name}")
    
    # Try to retrieve keys multiple times to demonstrate forgetting
    print("  Attempting to retrieve keys (may be forgotten randomly):")
    for i in range(5):
        color = test_patient.get_memory_key("favorite_color")
        pet = test_patient.get_memory_key("pet_name")
        town = test_patient.get_memory_key("hometown")
        
        print(f"    Attempt {i+1}: color={color}, pet={pet}, town={town}")
    
    # Test 3: Test recent memory functionality
    print("\n3. Testing recent memory functionality:")
    
    test_patient.add_recent_memory("Had breakfast this morning")
    test_patient.add_recent_memory("Talked to daughter on phone")
    test_patient.add_recent_memory("Watched the news")
    test_patient.add_recent_memory("Took afternoon medication")
    
    print(f"  Added 4 recent memories to {test_patient.name}")
    print(f"  Current recent memories count: {len(test_patient.recent_memories)}")
    
    # Test forget_recent method
    forgotten = test_patient.forget_recent()
    print(f"  After forget_recent(), forgotten {len(forgotten)} memories")
    print(f"  Remaining recent memories: {len(test_patient.recent_memories)}")
    if forgotten:
        print(f"  Forgotten memories: {forgotten}")
    
    # Test 4: Test mood update functionality
    print("\n4. Testing mood update functionality:")
    
    for patient in patients:
        original_mood = patient.mood_state
        print(f"  {patient.name} - Original mood: {original_mood.value}")
        
        # Try updating mood several times
        for i in range(5):
            new_mood = patient.update_mood()
            if new_mood != original_mood:
                print(f"    Mood changed to: {new_mood.value}")
                break
        else:
            print(f"    Mood remained: {patient.mood_state.value}")
    
    # Test 5: Test all enum values
    print("\n5. Testing enum values:")
    
    print("  Dementia stages:", [stage.value for stage in DementiaStage])
    print("  Mood states:", [mood.value for mood in MoodState])
    
    print("\n✓ All tests completed successfully!")


if __name__ == "__main__":
    test_patient_persona()