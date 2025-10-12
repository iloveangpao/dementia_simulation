"""Unit tests for empathy evaluator."""

import pytest

from dementia_simulation.evaluator.empathy_evaluator import EmpathyMetrics


class TestEmpathyMetrics:
    """Test EmpathyMetrics dataclass."""

    def test_metrics_creation(self):
        """Test creating empathy metrics."""
        metrics = EmpathyMetrics(
            validation_score=0.8,
            emotional_support_score=0.7,
            respect_score=0.9,
            patience_score=0.6,
            communication_clarity_score=0.8,
            non_confrontational_score=0.9,
        )

        assert metrics.validation_score == 0.8
        assert metrics.emotional_support_score == 0.7
        assert metrics.respect_score == 0.9
        assert metrics.patience_score == 0.6
        assert metrics.communication_clarity_score == 0.8
        assert metrics.non_confrontational_score == 0.9

    def test_metrics_defaults(self):
        """Test default metric values."""
        metrics = EmpathyMetrics()

        assert metrics.validation_score == 0.0
        assert metrics.emotional_support_score == 0.0
        assert metrics.respect_score == 0.0
        assert metrics.patience_score == 0.0
        assert metrics.communication_clarity_score == 0.0
        assert metrics.non_confrontational_score == 0.0


class TestEmpathyEvaluator:
    """Test EmpathyEvaluator class."""

    def test_evaluator_initialization(self, empathy_evaluator):
        """Test evaluator initialization."""
        assert empathy_evaluator.positive_patterns is not None
        assert empathy_evaluator.negative_patterns is not None
        assert empathy_evaluator.empathy_keywords is not None

        assert len(empathy_evaluator.positive_patterns) > 0
        assert len(empathy_evaluator.negative_patterns) > 0
        assert len(empathy_evaluator.empathy_keywords) > 0

    def test_evaluate_positive_response(self, empathy_evaluator):
        """Test evaluation of a positive empathetic response."""
        response = (
            "I understand how difficult this must be for you. Let's take our time."
        )

        metrics = empathy_evaluator.evaluate_response_patterns(response)

        assert isinstance(metrics, EmpathyMetrics)
        assert metrics.validation_score > 0.5
        assert metrics.patience_score > 0.5

    def test_evaluate_negative_response(self, empathy_evaluator):
        """Test evaluation of a negative response."""
        response = "No, that's wrong! You need to remember what I told you!"

        metrics = empathy_evaluator.evaluate_response_patterns(response)

        assert isinstance(metrics, EmpathyMetrics)
        # Should have low scores due to correction and commanding language
        assert metrics.validation_score < 0.5
        assert metrics.non_confrontational_score < 0.5

    def test_evaluate_neutral_response(self, empathy_evaluator):
        """Test evaluation of a neutral response."""
        response = "The weather is nice today."

        metrics = empathy_evaluator.evaluate_response_patterns(response)

        assert isinstance(metrics, EmpathyMetrics)
        # Should have moderate scores
        assert 0.0 <= metrics.validation_score <= 1.0
        assert 0.0 <= metrics.communication_clarity_score <= 1.0

    def test_communication_clarity_scoring(self, empathy_evaluator):
        """Test communication clarity scoring."""
        # Short, clear response
        short_response = "That's okay. I'm here to help."
        short_metrics = empathy_evaluator.evaluate_response_patterns(short_response)

        # Long, complex response
        long_response = (
            "Well, you see, the thing is that when we consider the "
            "multifaceted nature of your current psychological and emotional "
            "state in relation to the complexities of your medical condition, "
            "we need to take into account various factors."
        )
        long_metrics = empathy_evaluator.evaluate_response_patterns(long_response)

        # Short response should score better for clarity
        assert (
            short_metrics.communication_clarity_score
            > long_metrics.communication_clarity_score
        )

    def test_analyze_conversation_flow(
        self, empathy_evaluator, sample_conversation_history
    ):
        """Test conversation flow analysis."""
        flow_metrics = empathy_evaluator.analyze_conversation_flow(
            sample_conversation_history
        )

        assert isinstance(flow_metrics, dict)
        assert "consistency" in flow_metrics
        assert "adaptability" in flow_metrics
        assert "engagement" in flow_metrics

        # All metrics should be between 0 and 1
        for metric_value in flow_metrics.values():
            assert 0.0 <= metric_value <= 1.0

    def test_generate_feedback(self, empathy_evaluator):
        """Test feedback generation."""
        # High empathy metrics
        good_metrics = EmpathyMetrics(
            validation_score=0.9,
            emotional_support_score=0.8,
            respect_score=0.9,
            patience_score=0.8,
            communication_clarity_score=0.7,
            non_confrontational_score=0.9,
        )

        conversation_metrics = {
            "consistency": 0.8,
            "adaptability": 0.7,
            "engagement": 0.8,
        }

        feedback, strengths, improvements = empathy_evaluator.generate_feedback(
            good_metrics, conversation_metrics
        )

        assert isinstance(feedback, list)
        assert isinstance(strengths, list)
        assert isinstance(improvements, list)

        # Should have more strengths than improvements for good metrics
        assert len(strengths) > 0

    def test_generate_feedback_poor_metrics(self, empathy_evaluator):
        """Test feedback generation for poor metrics."""
        poor_metrics = EmpathyMetrics(
            validation_score=0.2,
            emotional_support_score=0.1,
            respect_score=0.3,
            patience_score=0.2,
            communication_clarity_score=0.3,
            non_confrontational_score=0.1,
        )

        conversation_metrics = {
            "consistency": 0.3,
            "adaptability": 0.2,
            "engagement": 0.1,
        }

        feedback, strengths, improvements = empathy_evaluator.generate_feedback(
            poor_metrics, conversation_metrics
        )

        # Should have more improvements than strengths for poor metrics
        assert len(improvements) > 0
        assert len(improvements) >= len(strengths)

    @pytest.mark.asyncio
    async def test_evaluate_conversation_empty(self, empathy_evaluator):
        """Test evaluation with empty conversation."""
        result = await empathy_evaluator.evaluate_conversation([], [])

        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "detailed_scores" in result
        assert "feedback" in result
        assert "strengths" in result
        assert "improvements" in result

        assert result["overall_score"] == 0.0
        assert len(result["improvements"]) > 0

    @pytest.mark.asyncio
    async def test_evaluate_conversation_full(
        self, empathy_evaluator, sample_conversation_history
    ):
        """Test full conversation evaluation."""
        caregiver_responses = [
            "How are you feeling today?",
            "You're safe here with me. I understand this is confusing.",
        ]

        result = await empathy_evaluator.evaluate_conversation(
            sample_conversation_history, caregiver_responses
        )

        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "detailed_scores" in result
        assert "feedback" in result
        assert "strengths" in result
        assert "improvements" in result
        assert "evaluation_timestamp" in result

        # Overall score should be reasonable
        assert 0.0 <= result["overall_score"] <= 1.0

        # Should have detailed scores for all categories
        expected_categories = [
            "validation",
            "emotional_support",
            "respect_and_dignity",
            "patience",
            "communication_clarity",
            "non_confrontational",
            "consistency",
            "adaptability",
            "engagement",
        ]

        for category in expected_categories:
            assert category in result["detailed_scores"]
            assert 0.0 <= result["detailed_scores"][category] <= 1.0

    def test_positive_patterns_detection(self, empathy_evaluator):
        """Test detection of positive empathy patterns."""
        test_responses = [
            "I understand how you feel",
            "That must be difficult for you",
            "Let's try together",
            "Take your time, no rush",
            "Tell me more about that",
            "You're safe here with me",
        ]

        for response in test_responses:
            metrics = empathy_evaluator.evaluate_response_patterns(response)

            # At least one empathy metric should be positive
            total_score = (
                metrics.validation_score
                + metrics.emotional_support_score
                + metrics.respect_score
                + metrics.patience_score
            )
            assert total_score > 0, f"No positive metrics for: {response}"

    def test_negative_patterns_detection(self, empathy_evaluator):
        """Test detection of negative patterns."""
        test_responses = [
            "No, that's wrong",
            "You need to remember",
            "Calm down right now",
            "We already talked about this",
            "Why can't you understand?",
            "Hurry up, we don't have time",
        ]

        for response in test_responses:
            metrics = empathy_evaluator.evaluate_response_patterns(response)

            # Should have reduced scores due to negative patterns
            # At least one metric should be affected
            problematic = (
                metrics.validation_score < 0.5
                or metrics.respect_score < 0.5
                or metrics.patience_score < 0.5
                or metrics.non_confrontational_score < 0.5
            )
            assert problematic, f"Negative pattern not detected in: {response}"
