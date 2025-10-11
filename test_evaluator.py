#!/usr/bin/env python3
"""
Basic tests for the caregiver feedback evaluator.
Tests the core functionality as specified in the requirements.
"""

import sys
import json
from src.evaluator import CaregiverFeedbackEvaluator, evaluate_caregiver_feedback


def test_reassurance_detection():
    """Test detection of reassurance words like 'okay' and 'I understand'."""
    evaluator = CaregiverFeedbackEvaluator()
    
    # Test case 1: "okay"
    result1 = evaluator.analyze_feedback("Okay, let's try this together.")
    assert "okay" in result1["detected_patterns"]["reassurance_words"]
    assert result1["scores"]["reassurance_score"] > 0
    print("✓ 'okay' detection test passed")
    
    # Test case 2: "I understand"
    result2 = evaluator.analyze_feedback("I understand how you feel.")
    assert "i understand" in result2["detected_patterns"]["reassurance_words"]
    assert result2["scores"]["reassurance_score"] > 0
    print("✓ 'I understand' detection test passed")


def test_confrontation_detection():
    """Test detection of confrontational phrases like 'no, that's wrong'."""
    evaluator = CaregiverFeedbackEvaluator()
    
    # Test case 1: "no, that's wrong"
    result1 = evaluator.analyze_feedback("No, that's wrong!")
    assert len(result1["detected_patterns"]["confrontation_words"]) > 0
    assert result1["scores"]["confrontation_score"] > 0
    print("✓ 'no, that's wrong' detection test passed")
    
    # Test case 2: Various confrontational phrases
    result2 = evaluator.analyze_feedback("You're wrong and that doesn't make sense.")
    assert result2["scores"]["confrontation_score"] > 0
    print("✓ General confrontation detection test passed")


def test_json_output():
    """Test that the output is valid JSON with expected structure."""
    evaluator = CaregiverFeedbackEvaluator()
    
    result = evaluator.analyze_feedback("Okay, I understand.")
    
    # Check required fields exist
    required_fields = ["scores", "detected_patterns", "analysis"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    # Check scores structure
    score_fields = ["reassurance_score", "confrontation_score", "overall_score"]
    for field in score_fields:
        assert field in result["scores"], f"Missing score field: {field}"
        assert isinstance(result["scores"][field], (int, float)), f"Score field {field} should be numeric"
    
    # Test JSON serialization
    json_str = json.dumps(result)
    parsed = json.loads(json_str)
    assert parsed == result, "JSON serialization/deserialization failed"
    
    print("✓ JSON output structure test passed")


def test_convenience_function():
    """Test the convenience function that returns JSON strings."""
    json_result = evaluate_caregiver_feedback("Okay, I understand your concern.")
    
    # Should be valid JSON
    parsed = json.loads(json_result)
    assert "scores" in parsed
    assert "detected_patterns" in parsed
    
    print("✓ Convenience function test passed")


def test_secondary_llm_option():
    """Test that secondary LLM option can be enabled without errors."""
    evaluator = CaregiverFeedbackEvaluator(use_secondary_llm=True)
    result = evaluator.analyze_feedback("This is a test.")
    
    # Should not crash and should return normal results
    assert "scores" in result
    print("✓ Secondary LLM option test passed")


def run_all_tests():
    """Run all tests and report results."""
    print("Running caregiver feedback evaluator tests...\n")
    
    try:
        test_reassurance_detection()
        test_confrontation_detection()
        test_json_output()
        test_convenience_function()
        test_secondary_llm_option()
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)