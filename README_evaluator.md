# Caregiver Feedback Evaluator

This module provides functionality to analyze caregiver responses in dementia care scenarios. It evaluates feedback based on reassurance patterns and confrontational language, returning JSON scores as specified in the requirements.

## Features

- **Reassurance Detection**: Detects supportive words and phrases like "okay", "I understand", "take your time", etc.
- **Confrontation Detection**: Identifies confrontational language like "no, that's wrong", "you're confused", etc.
- **JSON Score Output**: Returns structured JSON with detailed scores and analysis
- **Optional LLM Integration**: Supports secondary LLM analysis (placeholder implementation)

## Usage

### Basic Usage

```python
from src.evaluator import CaregiverFeedbackEvaluator

# Create evaluator instance
evaluator = CaregiverFeedbackEvaluator()

# Analyze feedback text
result = evaluator.analyze_feedback("Okay, I understand how you feel.")
print(result["scores"])
# Output: {'reassurance_score': 0.742, 'confrontation_score': 0.0, 'overall_score': 0.519}
```

### Convenience Function

```python
from src.evaluator import evaluate_caregiver_feedback

# Get JSON string result
json_result = evaluate_caregiver_feedback("That's wrong! You need to pay attention.")
print(json_result)
```

### With Secondary LLM (Optional)

```python
# Enable secondary LLM analysis
evaluator = CaregiverFeedbackEvaluator(use_secondary_llm=True, llm_client=your_llm_client)
result = evaluator.analyze_feedback("Your feedback text here")
```

## Output Format

The evaluator returns a JSON structure with the following fields:

```json
{
  "input_text": "The original feedback text",
  "text_length": 42,
  "scores": {
    "reassurance_score": 0.750,
    "confrontation_score": 0.200,
    "overall_score": 0.425
  },
  "detected_patterns": {
    "reassurance_words": ["okay", "i understand"],
    "confrontation_words": ["that's wrong"]
  },
  "analysis": {
    "feedback_type": "neutral_supportive",
    "recommendation": "Good supportive approach. Consider adding more reassurance words for better comfort."
  },
  "metadata": {
    "evaluator_version": "1.0.0",
    "analysis_timestamp": null
  }
}
```

## Scoring System

### Reassurance Score (0.0 - 1.0)
- Measures presence of supportive and comforting language
- Higher scores indicate more reassuring communication
- Patterns include: "okay", "I understand", "take your time", "don't worry", etc.

### Confrontation Score (0.0 - 1.0)  
- Measures presence of confrontational or corrective language
- Higher scores indicate more confrontational communication
- Patterns include: "no, that's wrong", "you're confused", "pay attention", etc.

### Overall Score (0.0 - 1.0)
- Calculated as: `(reassurance_score * 0.7) - (confrontation_score * 0.5)`
- Higher scores indicate better caregiving communication
- Emphasizes positive reinforcement over correction

## Feedback Types

The system categorizes feedback into these types:

- **supportive**: High reassurance, low confrontation
- **neutral_supportive**: Moderate reassurance, minimal confrontation  
- **neutral**: Low reassurance and confrontation
- **mildly_confrontational**: Some confrontational language present
- **confrontational**: High confrontational language

## Requirements Met

✅ **Detect reassurance words**: Identifies "okay", "I understand", and many other supportive phrases
✅ **Detect confrontation**: Identifies "no, that's wrong" and other confrontational patterns  
✅ **Optional secondary LLM**: Framework in place for LLM integration
✅ **Return JSON scores**: Structured JSON output with detailed scoring

## Testing

Run the included tests to verify functionality:

```bash
python3 test_evaluator.py
```

## Example Demonstrations

```python
# Supportive feedback
evaluate_caregiver_feedback("Okay, I understand. Let's take our time with this.")
# Result: High reassurance score, supportive feedback type

# Confrontational feedback  
evaluate_caregiver_feedback("No, that's wrong! You need to remember what I told you.")
# Result: High confrontation score, confrontational feedback type

# Neutral feedback
evaluate_caregiver_feedback("Hello, how are you today?")
# Result: Low scores, neutral feedback type
```