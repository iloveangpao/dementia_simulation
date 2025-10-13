# Evaluator Module

Caregiver feedback evaluation and communication quality scoring.

## Overview

The `evaluator` module provides:

- Pattern-based feedback analysis
- Reassurance detection
- Confrontation detection
- Overall quality scoring
- Actionable recommendations

## Quick Example

```python
from dementia_simulation.evaluator import CaregiverFeedbackEvaluator

# Initialize evaluator
evaluator = CaregiverFeedbackEvaluator()

# Analyze feedback
text = "That's okay. I understand how you're feeling."
result = evaluator.analyze_feedback(text)

print(f"Overall score: {result['scores']['overall_score']:.2f}")
print(f"Feedback type: {result['analysis']['feedback_type']}")
print(f"Recommendations: {result['recommendations']}")
```

## Scoring System

### Reassurance Score

Detects supportive language patterns:

- "I understand"
- "That's okay"
- "Take your time"
- "You're safe"
- "I'm here"

### Confrontation Score

Detects problematic patterns:

- "No, that's wrong"
- "You're confused"
- "Pay attention"
- "You need to remember"
- "That didn't happen"

### Overall Score

Weighted combination:

```
overall = (reassurance * 0.6) - (confrontation * 0.4)
```

## Module Reference

The evaluator module is located in `src/dementia_simulation/evaluator/`.

**Key Classes**:

- `CaregiverFeedbackEvaluator` - Main feedback evaluation class
- `PatternDetector` - Detects reassurance/confrontation patterns
- `ScoreCalculator` - Computes quality scores
- `RecommendationEngine` - Generates feedback recommendations

**Key Methods**:

- `analyze_feedback()` - Analyze caregiver response
- `detect_reassurance()` - Find supportive language
- `detect_confrontation()` - Find problematic language
- `calculate_scores()` - Compute metric scores
- `generate_recommendations()` - Create actionable feedback

For full module documentation, see the source code with inline docstrings.

## Related

- **[Evaluation & Iteration](../../explanation/evaluation-iteration.md)** - Testing workflow
- **[Safety Guardrails](../../explanation/safety-guardrails.md)** - Safety mechanisms
- **[Quickstart Tutorial](../../tutorials/quickstart.md)** - Get started
