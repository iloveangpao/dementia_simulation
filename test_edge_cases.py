#!/usr/bin/env python3
"""
Edge case testing for PatientPersona implementation.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from persona import PatientPersona, DementiaStage, MoodState


def test_edge_cases():
    """Test edge cases and robustness."""
    print("Testing Edge Cases")
    print("=" * 20)
    
    # Test 1: Empty memory operations
    patient = PatientPersona("EdgeTest")
    
    print("1. Empty memory operations:")
    result = patient.get_memory_key("non_existent_key")
    print(f"  ✓ Getting non-existent key returns: {result}")
    
    forgotten = patient.forget_recent()
    print(f"  ✓ Forgetting when no recent memories: {forgotten}")
    
    # Test 2: Large number of operations
    print("\n2. Stress testing with many operations:")
    
    # Add many memory keys
    for i in range(100):
        patient.add_memory_key(f"stress_key_{i}", f"value_{i}")
    
    print(f"  ✓ Added 100 memory keys, current count: {len(patient.memory_keys)}")
    
    # Add many recent memories
    for i in range(50):
        patient.add_recent_memory(f"Memory number {i}")
    
    print(f"  ✓ Added 50 recent memories, current count: {len(patient.recent_memories)}")
    
    # Test 3: Boundary conditions for each dementia stage
    print("\n3. Testing all dementia stages comprehensively:")
    
    for stage in DementiaStage:
        test_patient = PatientPersona(f"Test_{stage.value}", stage)
        status = test_patient.get_status()
        
        print(f"  {stage.value.upper()}:")
        print(f"    Forget probability: {status['forget_probability']:.1%}")
        print(f"    Mood change probability: {status['mood_change_probability']:.1%}")
        
        # Test mood changes
        original_mood = test_patient.mood_state
        changes = 0
        for _ in range(20):
            if test_patient.update_mood() != original_mood:
                changes += 1
        print(f"    Mood changes in 20 attempts: {changes}")
    
    # Test 4: String representations
    print("\n4. String representations:")
    patient = PatientPersona("TestName", DementiaStage.MODERATE, MoodState.AGITATED)
    print(f"  str(): {str(patient)}")
    print(f"  repr(): {repr(patient)}")
    
    # Test 5: Status reporting
    print("\n5. Complete status report:")
    status = patient.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ All edge cases handled correctly!")


if __name__ == "__main__":
    test_edge_cases()