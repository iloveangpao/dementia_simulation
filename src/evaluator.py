"""
Caregiver Feedback Evaluator

This module provides functionality to analyze caregiver responses in dementia care scenarios.
It evaluates feedback based on reassurance patterns and confrontational language.
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class FeedbackAnalysis:
    """Data class to hold feedback analysis results."""
    reassurance_score: float
    confrontation_score: float
    detected_reassurance_words: List[str]
    detected_confrontation_words: List[str]
    overall_score: float
    feedback_type: str


class CaregiverFeedbackEvaluator:
    """
    Evaluates caregiver feedback for dementia care scenarios.
    
    Analyzes text for reassurance patterns and confrontational language,
    providing scores and detailed feedback.
    """
    
    def __init__(self, use_secondary_llm: bool = False, llm_client: Optional[Any] = None):
        """
        Initialize the evaluator.
        
        Args:
            use_secondary_llm: Whether to use a secondary LLM for analysis
            llm_client: Optional LLM client for secondary analysis
        """
        self.use_secondary_llm = use_secondary_llm
        self.llm_client = llm_client
        
        # Reassurance words and phrases
        self.reassurance_patterns = [
            r'\bokay\b',
            r'\bi understand\b',
            r'\bi see\b',
            r'\bthat\'s alright\b',
            r'\bit\'s okay\b',
            r'\bno problem\b',
            r'\bdon\'t worry\b',
            r'\bdo not worry\b',
            r'\byou\'re safe\b',
            r'\bi\'m here\b',
            r'\btake your time\b',
            r'\blet\'s try together\b',
            r'\bthat makes sense\b'
        ]
        
        # Confrontational words and phrases
        self.confrontation_patterns = [
            r'\bno,?\s*that\'s wrong\b',
            r'\bno,?\s*that is wrong\b',
            r'\byou\'re wrong\b',
            r'\bthat\'s incorrect\b',
            r'\bno,?\s*you can\'t\b',
            r'\byou shouldn\'t\b',
            r'\bstop it\b',
            r'\bthat\'s not right\b',
            r'\byou\'re confused\b',
            r'\bthat doesn\'t make sense\b',
            r'\byou forgot\b',
            r'\bremember\?\b',
            r'\bpay attention\b'
        ]
    
    def detect_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """
        Detect patterns in text using regex.
        
        Args:
            text: Input text to analyze
            patterns: List of regex patterns to search for
            
        Returns:
            List of matched patterns/words
        """
        text_lower = text.lower()
        detected = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                # Extract the actual matched text for reporting
                for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                    detected.append(match.group())
        
        return list(set(detected))  # Remove duplicates
    
    def calculate_reassurance_score(self, detected_words: List[str], text_length: int) -> float:
        """
        Calculate reassurance score based on detected patterns.
        
        Args:
            detected_words: List of detected reassurance words/phrases
            text_length: Length of the input text
            
        Returns:
            Reassurance score between 0 and 1
        """
        if not detected_words or text_length == 0:
            return 0.0
        
        # Base score from number of reassurance patterns
        base_score = min(len(detected_words) / 3.0, 1.0)  # Normalize to max 1.0
        
        # Adjust for text length - longer text might naturally have more patterns
        length_factor = min(text_length / 100.0, 1.0)  # Normalize for ~100 char baseline
        adjusted_score = base_score * (0.7 + 0.3 * length_factor)
        
        return min(adjusted_score, 1.0)
    
    def calculate_confrontation_score(self, detected_words: List[str], text_length: int) -> float:
        """
        Calculate confrontation score based on detected patterns.
        
        Args:
            detected_words: List of detected confrontational words/phrases
            text_length: Length of the input text
            
        Returns:
            Confrontation score between 0 and 1
        """
        if not detected_words or text_length == 0:
            return 0.0
        
        # Confrontational language is more serious, so we penalize more heavily
        base_score = min(len(detected_words) / 2.0, 1.0)  # Normalize to max 1.0
        
        # Weight confrontational words more heavily than reassurance
        weighted_score = base_score * 1.2
        
        return min(weighted_score, 1.0)
    
    def determine_feedback_type(self, reassurance_score: float, confrontation_score: float) -> str:
        """
        Determine the overall feedback type based on scores.
        
        Args:
            reassurance_score: Score for reassurance patterns
            confrontation_score: Score for confrontational patterns
            
        Returns:
            String describing the feedback type
        """
        if confrontation_score > 0.5:
            return "confrontational"
        elif reassurance_score > 0.6:
            return "supportive"
        elif reassurance_score > 0.3:
            return "neutral_supportive"
        elif confrontation_score > 0.2:
            return "mildly_confrontational"
        else:
            return "neutral"
    
    def calculate_overall_score(self, reassurance_score: float, confrontation_score: float) -> float:
        """
        Calculate overall feedback quality score.
        
        Args:
            reassurance_score: Score for reassurance patterns
            confrontation_score: Score for confrontational patterns
            
        Returns:
            Overall score between 0 and 1 (higher is better)
        """
        # Good caregiving emphasizes reassurance and minimizes confrontation
        overall = (reassurance_score * 0.7) - (confrontation_score * 0.5)
        return max(0.0, min(overall, 1.0))
    
    async def analyze_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Use secondary LLM for additional analysis (optional).
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with LLM analysis results
        """
        if not self.use_secondary_llm or not self.llm_client:
            return {}
        
        try:
            # This is a placeholder for actual LLM integration
            # You would implement the actual LLM call here based on your LLM client
            prompt = f"""
            Analyze this caregiver response for empathy and appropriateness in dementia care:
            
            Text: "{text}"
            
            Rate on a scale of 1-10:
            1. Empathy level
            2. Appropriateness for dementia care
            3. Potential for building trust
            
            Provide brief reasoning for each score.
            """
            
            # Placeholder response - replace with actual LLM call
            return {
                "llm_empathy_score": 0.0,
                "llm_appropriateness_score": 0.0,
                "llm_trust_score": 0.0,
                "llm_reasoning": "LLM analysis not implemented"
            }
            
        except Exception as e:
            return {"llm_error": str(e)}
    
    def analyze_feedback(self, text: str) -> Dict[str, Any]:
        """
        Analyze caregiver feedback text and return JSON scores.
        
        Args:
            text: The caregiver feedback text to analyze
            
        Returns:
            Dictionary containing analysis results in JSON-serializable format
        """
        if not text or not isinstance(text, str):
            return {
                "error": "Invalid input: text must be a non-empty string",
                "scores": {}
            }
        
        text = text.strip()
        if not text:
            return {
                "error": "Empty text provided",
                "scores": {}
            }
        
        # Detect patterns
        reassurance_words = self.detect_patterns(text, self.reassurance_patterns)
        confrontation_words = self.detect_patterns(text, self.confrontation_patterns)
        
        # Calculate scores
        text_length = len(text)
        reassurance_score = self.calculate_reassurance_score(reassurance_words, text_length)
        confrontation_score = self.calculate_confrontation_score(confrontation_words, text_length)
        overall_score = self.calculate_overall_score(reassurance_score, confrontation_score)
        feedback_type = self.determine_feedback_type(reassurance_score, confrontation_score)
        
        # Create analysis object
        analysis = FeedbackAnalysis(
            reassurance_score=reassurance_score,
            confrontation_score=confrontation_score,
            detected_reassurance_words=reassurance_words,
            detected_confrontation_words=confrontation_words,
            overall_score=overall_score,
            feedback_type=feedback_type
        )
        
        # Build result dictionary
        result = {
            "input_text": text,
            "text_length": text_length,
            "scores": {
                "reassurance_score": round(reassurance_score, 3),
                "confrontation_score": round(confrontation_score, 3),
                "overall_score": round(overall_score, 3)
            },
            "detected_patterns": {
                "reassurance_words": reassurance_words,
                "confrontation_words": confrontation_words
            },
            "analysis": {
                "feedback_type": feedback_type,
                "recommendation": self._get_recommendation(analysis)
            },
            "metadata": {
                "evaluator_version": "1.0.0",
                "analysis_timestamp": None  # Could add timestamp if needed
            }
        }
        
        return result
    
    def _get_recommendation(self, analysis: FeedbackAnalysis) -> str:
        """
        Get a recommendation based on the analysis.
        
        Args:
            analysis: FeedbackAnalysis object
            
        Returns:
            String with recommendation
        """
        if analysis.feedback_type == "confrontational":
            return "Consider using more supportive and understanding language. Avoid direct corrections."
        elif analysis.feedback_type == "supportive":
            return "Excellent use of reassuring language. This approach builds trust and comfort."
        elif analysis.feedback_type == "neutral_supportive":
            return "Good supportive approach. Consider adding more reassurance words for better comfort."
        elif analysis.feedback_type == "mildly_confrontational":
            return "Try to reduce confrontational language and focus on validation and support."
        else:
            return "Consider adding more supportive and reassuring language to build connection."


def evaluate_caregiver_feedback(text: str, use_llm: bool = False, llm_client: Optional[Any] = None) -> str:
    """
    Convenience function to evaluate caregiver feedback and return JSON string.
    
    Args:
        text: The feedback text to analyze
        use_llm: Whether to use secondary LLM analysis
        llm_client: Optional LLM client
        
    Returns:
        JSON string with analysis results
    """
    evaluator = CaregiverFeedbackEvaluator(use_secondary_llm=use_llm, llm_client=llm_client)
    result = evaluator.analyze_feedback(text)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Example usage
    examples = [
        "Okay, I understand how you're feeling. Let's take our time with this.",
        "No, that's wrong! You need to remember what I told you.",
        "I see what you mean. That makes sense to me.",
        "You're confused again. Pay attention to what I'm saying."
    ]
    
    evaluator = CaregiverFeedbackEvaluator()
    
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example}")
        result = evaluator.analyze_feedback(example)
        print(json.dumps(result, indent=2))