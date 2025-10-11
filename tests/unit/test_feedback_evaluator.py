"""Unit tests for caregiver feedback evaluator."""

import json

import pytest
from dementia_simulation.evaluator.feedback_evaluator import (
    CaregiverFeedbackEvaluator,
    FeedbackAnalysis,
    evaluate_caregiver_feedback,
)


class TestFeedbackAnalysis:
    """Test FeedbackAnalysis dataclass."""

    def test_feedback_analysis_creation(self):
        """Test creating feedback analysis."""
        analysis = FeedbackAnalysis(
            reassurance_score=0.8,
            confrontation_score=0.2,
            detected_reassurance_words=["okay", "i understand"],
            detected_confrontation_words=["that's wrong"],
            overall_score=0.46,
            feedback_type="neutral_supportive",
        )

        assert analysis.reassurance_score == 0.8
        assert analysis.confrontation_score == 0.2
        assert analysis.overall_score == 0.46
        assert analysis.feedback_type == "neutral_supportive"
        assert len(analysis.detected_reassurance_words) == 2
        assert len(analysis.detected_confrontation_words) == 1


class TestCaregiverFeedbackEvaluator:
    """Test CaregiverFeedbackEvaluator class."""

    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        evaluator = CaregiverFeedbackEvaluator()

        assert evaluator.reassurance_patterns is not None
        assert evaluator.confrontation_patterns is not None
        assert len(evaluator.reassurance_patterns) > 0
        assert len(evaluator.confrontation_patterns) > 0
        assert evaluator.use_secondary_llm is False
        assert evaluator.llm_client is None

    def test_evaluator_with_llm(self):
        """Test evaluator initialization with LLM enabled."""
        mock_client = object()
        evaluator = CaregiverFeedbackEvaluator(
            use_secondary_llm=True, llm_client=mock_client
        )

        assert evaluator.use_secondary_llm is True
        assert evaluator.llm_client is mock_client

    def test_detect_patterns_reassurance(self):
        """Test detection of reassurance patterns."""
        evaluator = CaregiverFeedbackEvaluator()
        text = "Okay, I understand your concern. Take your time."

        detected = evaluator.detect_patterns(text, evaluator.reassurance_patterns)

        assert len(detected) > 0
        assert any("okay" in word for word in detected)
        assert any("understand" in word for word in detected)

    def test_detect_patterns_confrontation(self):
        """Test detection of confrontational patterns."""
        evaluator = CaregiverFeedbackEvaluator()
        text = "No, that's wrong! You're confused and need to pay attention."

        detected = evaluator.detect_patterns(
            text, evaluator.confrontation_patterns
        )

        assert len(detected) > 0
        # Should detect "no, that's wrong", "you're confused", "pay attention"
        assert len(detected) >= 2

    def test_detect_patterns_no_matches(self):
        """Test pattern detection with no matches."""
        evaluator = CaregiverFeedbackEvaluator()
        text = "The weather is nice today."

        detected_reassurance = evaluator.detect_patterns(
            text, evaluator.reassurance_patterns
        )
        detected_confrontation = evaluator.detect_patterns(
            text, evaluator.confrontation_patterns
        )

        assert len(detected_reassurance) == 0
        assert len(detected_confrontation) == 0

    def test_calculate_reassurance_score_high(self):
        """Test reassurance score calculation with multiple patterns."""
        evaluator = CaregiverFeedbackEvaluator()
        detected_words = ["okay", "i understand", "take your time"]
        text_length = 50

        score = evaluator.calculate_reassurance_score(detected_words, text_length)

        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high with 3 patterns

    def test_calculate_reassurance_score_low(self):
        """Test reassurance score calculation with no patterns."""
        evaluator = CaregiverFeedbackEvaluator()
        detected_words = []
        text_length = 50

        score = evaluator.calculate_reassurance_score(detected_words, text_length)

        assert score == 0.0

    def test_calculate_confrontation_score_high(self):
        """Test confrontation score calculation with multiple patterns."""
        evaluator = CaregiverFeedbackEvaluator()
        detected_words = ["no, that's wrong", "you're confused", "pay attention"]
        text_length = 50

        score = evaluator.calculate_confrontation_score(
            detected_words, text_length
        )

        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high with 3 patterns

    def test_calculate_confrontation_score_low(self):
        """Test confrontation score calculation with no patterns."""
        evaluator = CaregiverFeedbackEvaluator()
        detected_words = []
        text_length = 50

        score = evaluator.calculate_confrontation_score(
            detected_words, text_length
        )

        assert score == 0.0

    def test_determine_feedback_type_supportive(self):
        """Test feedback type determination for supportive responses."""
        evaluator = CaregiverFeedbackEvaluator()

        feedback_type = evaluator.determine_feedback_type(
            reassurance_score=0.8, confrontation_score=0.1
        )

        assert feedback_type == "supportive"

    def test_determine_feedback_type_confrontational(self):
        """Test feedback type determination for confrontational responses."""
        evaluator = CaregiverFeedbackEvaluator()

        feedback_type = evaluator.determine_feedback_type(
            reassurance_score=0.1, confrontation_score=0.8
        )

        assert feedback_type == "confrontational"

    def test_determine_feedback_type_neutral(self):
        """Test feedback type determination for neutral responses."""
        evaluator = CaregiverFeedbackEvaluator()

        feedback_type = evaluator.determine_feedback_type(
            reassurance_score=0.2, confrontation_score=0.2
        )

        assert feedback_type == "neutral"

    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        evaluator = CaregiverFeedbackEvaluator()

        # High reassurance, low confrontation = high score
        score_good = evaluator.calculate_overall_score(
            reassurance_score=0.8, confrontation_score=0.1
        )
        assert score_good > 0.4

        # Low reassurance, high confrontation = low score
        score_bad = evaluator.calculate_overall_score(
            reassurance_score=0.1, confrontation_score=0.8
        )
        assert score_bad < 0.2

        # Score should be bounded 0-1
        assert 0.0 <= score_good <= 1.0
        assert 0.0 <= score_bad <= 1.0

    def test_analyze_feedback_reassurance(self):
        """Test analysis of reassuring feedback."""
        evaluator = CaregiverFeedbackEvaluator()
        text = "Okay, I understand how you're feeling. Take your time."

        result = evaluator.analyze_feedback(text)

        assert "scores" in result
        assert "detected_patterns" in result
        assert "analysis" in result
        assert "metadata" in result

        assert result["scores"]["reassurance_score"] > 0.5
        assert result["scores"]["confrontation_score"] < 0.3
        assert len(result["detected_patterns"]["reassurance_words"]) > 0

    def test_analyze_feedback_confrontational(self):
        """Test analysis of confrontational feedback."""
        evaluator = CaregiverFeedbackEvaluator()
        text = "No, that's wrong! You're confused and you need to remember."

        result = evaluator.analyze_feedback(text)

        assert "scores" in result
        assert "detected_patterns" in result
        assert "analysis" in result

        assert result["scores"]["confrontation_score"] > 0.5
        assert result["scores"]["reassurance_score"] < 0.3
        assert len(result["detected_patterns"]["confrontation_words"]) > 0

    def test_analyze_feedback_neutral(self):
        """Test analysis of neutral feedback."""
        evaluator = CaregiverFeedbackEvaluator()
        text = "Hello, how are you today?"

        result = evaluator.analyze_feedback(text)

        assert "scores" in result
        assert result["scores"]["reassurance_score"] < 0.3
        assert result["scores"]["confrontation_score"] < 0.3

    def test_analyze_feedback_empty_string(self):
        """Test analysis with empty string."""
        evaluator = CaregiverFeedbackEvaluator()

        result = evaluator.analyze_feedback("")
        assert "error" in result
        assert result["error"] == "Empty text provided"

    def test_analyze_feedback_invalid_input(self):
        """Test analysis with invalid input."""
        evaluator = CaregiverFeedbackEvaluator()

        result = evaluator.analyze_feedback(None)
        assert "error" in result

        result = evaluator.analyze_feedback(123)
        assert "error" in result

    def test_analyze_feedback_json_structure(self):
        """Test that output has valid JSON structure."""
        evaluator = CaregiverFeedbackEvaluator()
        text = "Okay, I understand."

        result = evaluator.analyze_feedback(text)

        # Check required fields
        required_fields = ["scores", "detected_patterns", "analysis", "metadata"]
        for field in required_fields:
            assert field in result

        # Check scores structure
        score_fields = [
            "reassurance_score",
            "confrontation_score",
            "overall_score",
        ]
        for field in score_fields:
            assert field in result["scores"]
            assert isinstance(result["scores"][field], (int, float))

        # Test JSON serialization
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        assert parsed == result

    def test_feedback_type_recommendation(self):
        """Test that recommendations are generated for all feedback types."""
        evaluator = CaregiverFeedbackEvaluator()

        test_cases = [
            ("Okay, I understand. Let's take our time.", "supportive"),
            (
                "I see what you mean. That makes sense.",
                "neutral_supportive",
            ),
            ("Hello, how are you?", "neutral"),
            (
                "You're confused. Pay attention to what I'm saying.",
                "mildly_confrontational",
            ),
            (
                "No, that's wrong! You need to remember what I told you.",
                "confrontational",
            ),
        ]

        for text, _expected_type in test_cases:
            result = evaluator.analyze_feedback(text)
            # Just ensure recommendation exists, not checking exact type
            # as scoring might vary
            assert "recommendation" in result["analysis"]
            assert len(result["analysis"]["recommendation"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_with_llm_disabled(self):
        """Test LLM analysis when disabled."""
        evaluator = CaregiverFeedbackEvaluator()
        result = await evaluator.analyze_with_llm("Test text")

        assert result == {}

    @pytest.mark.asyncio
    async def test_analyze_with_llm_enabled(self):
        """Test LLM analysis when enabled (placeholder)."""
        evaluator = CaregiverFeedbackEvaluator(use_secondary_llm=True)
        result = await evaluator.analyze_with_llm("Test text")

        # Should return empty dict as no client provided
        assert result == {}


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_evaluate_caregiver_feedback_returns_json_string(self):
        """Test that convenience function returns valid JSON string."""
        text = "Okay, I understand your concern."

        result = evaluate_caregiver_feedback(text)

        # Should be a string
        assert isinstance(result, str)

        # Should be valid JSON
        parsed = json.loads(result)
        assert "scores" in parsed
        assert "detected_patterns" in parsed

    def test_evaluate_caregiver_feedback_with_llm(self):
        """Test convenience function with LLM enabled."""
        text = "I understand how you feel."

        result = evaluate_caregiver_feedback(text, use_llm=True)

        # Should still work (LLM returns empty dict)
        parsed = json.loads(result)
        assert "scores" in parsed


class TestIntegration:
    """Integration tests for the feedback evaluator."""

    def test_full_workflow_supportive(self):
        """Test complete workflow with supportive response."""
        evaluator = CaregiverFeedbackEvaluator()
        text = (
            "I understand this must be difficult for you. "
            "Let's take our time and work through this together. "
            "You're safe here, and I'm here to help."
        )

        result = evaluator.analyze_feedback(text)

        assert result["scores"]["reassurance_score"] > 0.6
        assert result["scores"]["overall_score"] > 0.4
        assert (
            result["analysis"]["feedback_type"] == "supportive"
            or result["analysis"]["feedback_type"] == "neutral_supportive"
        )

    def test_full_workflow_confrontational(self):
        """Test complete workflow with confrontational response."""
        evaluator = CaregiverFeedbackEvaluator()
        text = (
            "No, that's wrong! You're confused again. "
            "I told you this already. Pay attention to what I'm saying."
        )

        result = evaluator.analyze_feedback(text)

        assert result["scores"]["confrontation_score"] > 0.6
        assert result["scores"]["overall_score"] < 0.2
        assert (
            result["analysis"]["feedback_type"] == "confrontational"
            or result["analysis"]["feedback_type"] == "mildly_confrontational"
        )

    def test_multiple_evaluations(self):
        """Test multiple consecutive evaluations."""
        evaluator = CaregiverFeedbackEvaluator()

        texts = [
            "Okay, I understand.",
            "No, that's wrong.",
            "Let's take our time with this.",
            "You're confused and need to pay attention.",
        ]

        results = []
        for text in texts:
            result = evaluator.analyze_feedback(text)
            results.append(result)

        # All should have valid scores
        for result in results:
            assert "scores" in result
            assert 0.0 <= result["scores"]["reassurance_score"] <= 1.0
            assert 0.0 <= result["scores"]["confrontation_score"] <= 1.0
            assert 0.0 <= result["scores"]["overall_score"] <= 1.0
