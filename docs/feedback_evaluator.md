# Caregiver Feedback Evaluator

## Overview

The Caregiver Feedback Evaluator is a rule-based system for analyzing caregiver responses in dementia care scenarios. It provides automatic scoring and feedback on communication quality based on pattern detection of reassurance and confrontational language.

## Features

- **Reassurance Detection**: Identifies supportive words and phrases
  - "okay", "I understand", "take your time"
  - "don't worry", "you're safe", "I'm here"
  - And more...

- **Confrontation Detection**: Identifies problematic language
  - "no, that's wrong", "you're confused"
  - "pay attention", "you need to remember"
  - And more...

- **JSON Score Output**: Returns structured JSON with:
  - Reassurance score (0.0 - 1.0)
  - Confrontation score (0.0 - 1.0)
  - Overall score (0.0 - 1.0)
  - Detected patterns
  - Feedback type classification
  - Recommendations

- **Optional LLM Integration**: Framework in place for secondary LLM analysis

## Usage

### Basic Usage

```python
from dementia_simulation.evaluator import (
    CaregiverFeedbackEvaluator,
    evaluate_caregiver_feedback
)

# Create evaluator instance
evaluator = CaregiverFeedbackEvaluator()

# Analyze feedback
text = "Okay, I understand how you're feeling. Let's take our time."
result = evaluator.analyze_feedback(text)

# Access scores
print(f"Reassurance: {result['scores']['reassurance_score']}")
print(f"Confrontation: {result['scores']['confrontation_score']}")
print(f"Overall: {result['scores']['overall_score']}")
print(f"Type: {result['analysis']['feedback_type']}")
print(f"Recommendation: {result['analysis']['recommendation']}")
```

### Convenience Function

```python
# Get JSON string directly
json_result = evaluate_caregiver_feedback(
    "I see what you mean. That makes sense to me."
)
print(json_result)
```

### With LLM Support (Optional)

```python
# Enable secondary LLM analysis (placeholder implementation)
evaluator = CaregiverFeedbackEvaluator(
    use_secondary_llm=True,
    llm_client=your_llm_client
)

result = evaluator.analyze_feedback("Your text here")
```

## Output Format

The evaluator returns a dictionary with the following structure:

```json
{
  "input_text": "Okay, I understand how you're feeling.",
  "text_length": 38,
  "scores": {
    "reassurance_score": 0.750,
    "confrontation_score": 0.000,
    "overall_score": 0.525
  },
  "detected_patterns": {
    "reassurance_words": ["okay", "i understand"],
    "confrontation_words": []
  },
  "analysis": {
    "feedback_type": "supportive",
    "recommendation": "Excellent supportive approach. Keep up the good work!"
  },
  "metadata": {
    "evaluator_version": "1.0.0",
    "analysis_timestamp": null
  }
}
```

## Feedback Types

The system classifies feedback into five types:

1. **supportive**: High reassurance (≥0.7), low confrontation (<0.4)
   - Example: "I understand this is difficult. Take your time."

2. **neutral_supportive**: Moderate reassurance (≥0.4), minimal confrontation (<0.4)
   - Example: "I see what you mean. Let's work on this together."

3. **neutral**: Low reassurance (<0.4), low confrontation (<0.4)
   - Example: "Hello, how are you today?"

4. **mildly_confrontational**: Moderate confrontation (≥0.4, <0.7)
   - Example: "You need to remember this. Pay attention."

5. **confrontational**: High confrontation (≥0.7)
   - Example: "No, that's wrong! You're confused again."

## Scoring System

### Reassurance Score (0.0 - 1.0)

- Measures presence of supportive and comforting language
- Higher scores indicate more reassuring communication
- Calculated based on:
  - Number of reassurance patterns detected
  - Text length normalization
  - Base score: `min(detected_patterns / 3.0, 1.0)`
  - Adjusted for text length

### Confrontation Score (0.0 - 1.0)

- Measures presence of confrontational or corrective language
- Higher scores indicate more confrontational communication
- Calculated with higher weight than reassurance:
  - Base score: `min(detected_patterns / 2.0, 1.0)`
  - Weighted: `base_score * 1.2` (capped at 1.0)

### Overall Score (0.0 - 1.0)

- Combined metric emphasizing positive communication
- Formula: `(reassurance_score * 0.7) - (confrontation_score * 0.5)`
- Higher scores indicate better caregiving communication
- Range: 0.0 to 1.0 (negative values clamped to 0.0)

## Pattern Matching

### Reassurance Patterns

The evaluator detects these reassurance patterns using regex:

- Basic validation: "okay", "I understand", "I see"
- Comfort: "that's alright", "it's okay", "no problem"
- Safety: "you're safe", "I'm here"
- Patience: "take your time", "don't worry"
- Collaboration: "let's try together"
- Acknowledgment: "that makes sense"

### Confrontation Patterns

The evaluator detects these confrontational patterns:

- Direct correction: "no, that's wrong", "you're wrong", "that's not right"
- Confusion labeling: "you're confused", "you're mistaken"
- Demanding: "pay attention", "you need to remember"
- Impatience: "I told you", "we already discussed", "how many times"

## Best Practices

### For Dementia Care Communication

1. **Use Validation**: Acknowledge feelings without correction
   - ✅ "I understand this is frustrating"
   - ❌ "No, that's wrong"

2. **Show Patience**: Allow time for processing
   - ✅ "Take your time, no rush"
   - ❌ "Hurry up, we need to go"

3. **Provide Reassurance**: Create a sense of safety
   - ✅ "You're safe here with me"
   - ❌ "You're confused again"

4. **Avoid Confrontation**: Don't argue or correct directly
   - ✅ "Let's work on this together"
   - ❌ "You need to remember what I told you"

### Integration Tips

1. **Real-time Feedback**: Use during training simulations
2. **Batch Analysis**: Analyze conversation transcripts
3. **Progress Tracking**: Monitor score improvements over time
4. **Custom Patterns**: Extend pattern lists for specific contexts

## API Integration

The feedback evaluator integrates seamlessly with the dementia simulation API:

```python
from dementia_simulation.api.server import app
from dementia_simulation.evaluator import CaregiverFeedbackEvaluator

# In your FastAPI endpoint
evaluator = CaregiverFeedbackEvaluator()

@app.post("/evaluate-feedback")
async def evaluate_feedback(text: str):
    result = evaluator.analyze_feedback(text)
    return result
```

## Testing

Run the comprehensive test suite:

```bash
# Test feedback evaluator
poetry run pytest tests/unit/test_feedback_evaluator.py -v

# With coverage
poetry run pytest tests/unit/test_feedback_evaluator.py --cov=src/dementia_simulation/evaluator/feedback_evaluator.py
```

## Differences from Empathy Evaluator

The repository includes two evaluators with different purposes:

### CaregiverFeedbackEvaluator (feedback_evaluator.py)
- **Purpose**: Basic pattern matching for quick assessment
- **Focus**: Reassurance vs. confrontation
- **Complexity**: Simple, rule-based
- **Output**: Basic scores and feedback type
- **Use case**: Real-time feedback during interactions

### EmpathyEvaluator (empathy_evaluator.py)
- **Purpose**: Comprehensive empathy assessment
- **Focus**: Multiple dimensions (validation, emotional support, respect, patience, clarity, non-confrontation)
- **Complexity**: Advanced pattern matching with conversation flow analysis
- **Output**: Detailed scores, strengths, improvements, consistency metrics
- **Use case**: Post-conversation analysis and training assessment

Choose based on your needs:
- Use **CaregiverFeedbackEvaluator** for simple, fast feedback
- Use **EmpathyEvaluator** for detailed analysis and training

## Future Enhancements

1. **LLM Integration**: Complete implementation of secondary LLM analysis
2. **Custom Patterns**: Support for user-defined pattern sets
3. **Multilingual Support**: Pattern detection in multiple languages
4. **Sentiment Analysis**: Integration with sentiment analysis models
5. **Historical Tracking**: Track improvement over time
6. **Context Awareness**: Consider conversation history in scoring

## References

- [Dementia Communication Guidelines](https://www.alzheimers.org.uk/get-support/help-dementia-care/communicating-dementia)
- [Person-Centered Dementia Care](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6469873/)
- [Validation Therapy](https://vfvalidation.org/)

## License

Part of the Dementia Simulation project - MIT License
