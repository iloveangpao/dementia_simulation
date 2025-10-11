"""
Empathy evaluator for caregiver responses in dementia simulation.

This module evaluates the empathy level and appropriateness of caregiver
responses during dementia patient interactions.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re
from datetime import datetime
import asyncio
from loguru import logger


@dataclass
class EmpathyMetrics:
    """Metrics for evaluating empathy in responses."""
    validation_score: float = 0.0  # Validates feelings without correction
    emotional_support_score: float = 0.0  # Provides emotional comfort
    respect_score: float = 0.0  # Maintains dignity and respect
    patience_score: float = 0.0  # Shows patience with repetition/confusion
    communication_clarity_score: float = 0.0  # Clear, simple communication
    non_confrontational_score: float = 0.0  # Avoids argument or correction


class EmpathyEvaluator:
    """
    Evaluates caregiver empathy and communication effectiveness
    in dementia care scenarios.
    """
    
    def __init__(self):
        """Initialize the empathy evaluator."""
        self.positive_patterns = self._load_positive_patterns()
        self.negative_patterns = self._load_negative_patterns()
        self.empathy_keywords = self._load_empathy_keywords()
        
    def _load_positive_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns that indicate positive empathetic responses."""
        return [
            {
                "pattern": r"\b(I understand|I can see|I hear you|I know this is)\b",
                "category": "validation",
                "weight": 0.8
            },
            {
                "pattern": r"\b(that must be|how (difficult|hard|frustrating)|I imagine)\b",
                "category": "emotional_support",
                "weight": 0.7
            },
            {
                "pattern": r"\b(let's|would you like|what if we|how about)\b",
                "category": "collaboration",
                "weight": 0.6
            },
            {
                "pattern": r"\b(take your time|no rush|it's okay|that's fine)\b",
                "category": "patience",
                "weight": 0.8
            },
            {
                "pattern": r"\b(tell me more|help me understand|what do you think)\b",
                "category": "engagement",
                "weight": 0.7
            },
            {
                "pattern": r"\b(you're safe|you're doing great|I'm here with you)\b",
                "category": "reassurance",
                "weight": 0.9
            }
        ]
    
    def _load_negative_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns that indicate less empathetic responses."""
        return [
            {
                "pattern": r"\b(no, that's wrong|you're mistaken|that's not right)\b",
                "category": "correction",
                "weight": -0.9
            },
            {
                "pattern": r"\b(you need to|you should|you have to|you must)\b",
                "category": "commanding",
                "weight": -0.6
            },
            {
                "pattern": r"\b(calm down|don't worry|just relax|stop)\b",
                "category": "dismissive",
                "weight": -0.7
            },
            {
                "pattern": r"\b(again\?|we already|I told you|remember\?)\b",
                "category": "impatience",
                "weight": -0.8
            },
            {
                "pattern": r"\b(why can't you|why don't you|what's wrong with)\b",
                "category": "confrontational",
                "weight": -0.9
            },
            {
                "pattern": r"\b(hurry up|quickly|faster|come on)\b",
                "category": "rushing",
                "weight": -0.5
            }
        ]
    
    def _load_empathy_keywords(self) -> Dict[str, float]:
        """Load empathy-related keywords and their weights."""
        return {
            # High empathy words
            "understand": 0.8,
            "feel": 0.7,
            "comfort": 0.8,
            "support": 0.7,
            "gentle": 0.8,
            "patient": 0.8,
            "kind": 0.7,
            "caring": 0.8,
            "compassionate": 0.9,
            "empathetic": 0.9,
            
            # Validation words
            "validate": 0.8,
            "acknowledge": 0.7,
            "accept": 0.6,
            "listen": 0.7,
            "hear": 0.6,
            
            # Negative indicators
            "argue": -0.8,
            "correct": -0.6,
            "wrong": -0.7,
            "mistake": -0.6,
            "frustrated": -0.5,  # Caregiver expressing frustration
            "impatient": -0.8,
            "annoyed": -0.7
        }
    
    def evaluate_response_patterns(self, response: str) -> EmpathyMetrics:
        """
        Evaluate a single response for empathy patterns.
        
        Args:
            response: Caregiver response to evaluate
            
        Returns:
            EmpathyMetrics with scores for different aspects
        """
        response_lower = response.lower()
        metrics = EmpathyMetrics()
        
        # Check positive patterns
        validation_score = 0.0
        emotional_support_score = 0.0
        respect_score = 0.0
        patience_score = 0.0
        communication_score = 0.0
        non_confrontational_score = 0.0
        
        for pattern_info in self.positive_patterns:
            if re.search(pattern_info["pattern"], response_lower):
                weight = pattern_info["weight"]
                category = pattern_info["category"]
                
                if category == "validation":
                    validation_score += weight
                elif category in ["emotional_support", "reassurance"]:
                    emotional_support_score += weight
                elif category in ["collaboration", "engagement"]:
                    respect_score += weight
                elif category == "patience":
                    patience_score += weight
        
        # Check negative patterns
        for pattern_info in self.negative_patterns:
            if re.search(pattern_info["pattern"], response_lower):
                weight = abs(pattern_info["weight"])  # Make positive for subtraction
                category = pattern_info["category"]
                
                if category == "correction":
                    validation_score -= weight
                    non_confrontational_score -= weight
                elif category in ["commanding", "dismissive"]:
                    respect_score -= weight
                elif category == "impatience":
                    patience_score -= weight
                elif category == "confrontational":
                    non_confrontational_score -= weight
                elif category == "rushing":
                    patience_score -= weight
        
        # Evaluate communication clarity
        sentence_length = len(response.split())
        if sentence_length <= 15:  # Simple, clear sentences
            communication_score += 0.6
        elif sentence_length <= 25:
            communication_score += 0.3
        else:
            communication_score -= 0.2  # Too complex
        
        # Check for question marks (engaging questions)
        if "?" in response:
            respect_score += 0.3
            communication_score += 0.2
        
        # Normalize scores to 0-1 range
        metrics.validation_score = max(0.0, min(1.0, validation_score))
        metrics.emotional_support_score = max(0.0, min(1.0, emotional_support_score))
        metrics.respect_score = max(0.0, min(1.0, respect_score))
        metrics.patience_score = max(0.0, min(1.0, patience_score))
        metrics.communication_clarity_score = max(0.0, min(1.0, communication_score))
        metrics.non_confrontational_score = max(0.0, min(1.0, non_confrontational_score))
        
        return metrics
    
    def analyze_conversation_flow(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyze the overall flow and patterns in the conversation.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            Dictionary with conversation flow metrics
        """
        caregiver_messages = [
            msg for msg in conversation_history 
            if msg.get('speaker') == 'caregiver'
        ]
        
        if len(caregiver_messages) < 2:
            return {"consistency": 0.5, "adaptability": 0.5, "engagement": 0.5}
        
        # Analyze consistency in empathy level
        empathy_scores = []
        for msg in caregiver_messages:
            metrics = self.evaluate_response_patterns(msg.get('message', ''))
            avg_score = (
                metrics.validation_score + 
                metrics.emotional_support_score + 
                metrics.respect_score + 
                metrics.patience_score
            ) / 4
            empathy_scores.append(avg_score)
        
        # Calculate consistency (lower variance = higher consistency)
        if len(empathy_scores) > 1:
            variance = sum((x - sum(empathy_scores)/len(empathy_scores))**2 for x in empathy_scores) / len(empathy_scores)
            consistency = max(0.0, 1.0 - variance)
        else:
            consistency = 1.0
        
        # Analyze adaptability (responding appropriately to patient mood changes)
        adaptability = 0.5  # Default if can't measure
        patient_moods = []
        for msg in conversation_history:
            if msg.get('speaker') == 'patient' and 'mood' in msg:
                patient_moods.append(msg['mood'])
        
        if len(patient_moods) > 1:
            mood_changes = sum(1 for i in range(1, len(patient_moods)) if patient_moods[i] != patient_moods[i-1])
            if mood_changes > 0:
                # Check if caregiver responses adapted to mood changes
                adaptability = min(1.0, len(caregiver_messages) / (mood_changes + 1) * 0.5)
        
        # Analyze engagement (asking questions, encouraging responses)
        engagement_indicators = 0
        for msg in caregiver_messages:
            message_text = msg.get('message', '')
            if '?' in message_text:
                engagement_indicators += 1
            if any(word in message_text.lower() for word in ['tell me', 'what do you', 'how do you']):
                engagement_indicators += 1
        
        engagement = min(1.0, engagement_indicators / len(caregiver_messages))
        
        return {
            "consistency": consistency,
            "adaptability": adaptability,
            "engagement": engagement
        }
    
    def generate_feedback(self, metrics: EmpathyMetrics, conversation_metrics: Dict[str, float]) -> Tuple[List[str], List[str], List[str]]:
        """
        Generate specific feedback based on evaluation metrics.
        
        Args:
            metrics: Average empathy metrics
            conversation_metrics: Conversation flow metrics
            
        Returns:
            Tuple of (feedback_messages, strengths, improvements)
        """
        feedback = []
        strengths = []
        improvements = []
        
        # Validation feedback
        if metrics.validation_score >= 0.7:
            strengths.append("Excellent at validating patient feelings without correction")
        elif metrics.validation_score >= 0.4:
            feedback.append("Good validation skills, but could be more consistent")
        else:
            improvements.append("Focus on validating the patient's feelings rather than correcting them")
            feedback.append("Try phrases like 'I understand how you feel' or 'That must be difficult'")
        
        # Emotional support feedback
        if metrics.emotional_support_score >= 0.7:
            strengths.append("Provides strong emotional support and comfort")
        elif metrics.emotional_support_score >= 0.4:
            feedback.append("Shows some emotional support, but could be more nurturing")
        else:
            improvements.append("Offer more emotional comfort and reassurance")
            feedback.append("Use comforting phrases and acknowledge the patient's emotional state")
        
        # Patience feedback
        if metrics.patience_score >= 0.7:
            strengths.append("Demonstrates excellent patience with repetition and confusion")
        elif metrics.patience_score >= 0.4:
            feedback.append("Generally patient, but watch for signs of frustration")
        else:
            improvements.append("Practice more patience with repeated questions and confusion")
            feedback.append("Remember that repetition is part of dementia - each time feels new to them")
        
        # Communication clarity feedback
        if metrics.communication_clarity_score >= 0.7:
            strengths.append("Uses clear, simple communication appropriate for dementia care")
        elif metrics.communication_clarity_score >= 0.4:
            feedback.append("Communication is mostly clear, but could be simplified")
        else:
            improvements.append("Use shorter, simpler sentences and speak more clearly")
            feedback.append("Break complex ideas into smaller, easier-to-understand parts")
        
        # Conversation flow feedback
        if conversation_metrics["consistency"] >= 0.7:
            strengths.append("Maintains consistent empathy throughout the conversation")
        else:
            improvements.append("Work on maintaining consistent empathy levels throughout interactions")
        
        if conversation_metrics["engagement"] >= 0.7:
            strengths.append("Effectively engages the patient in conversation")
        else:
            improvements.append("Ask more open-ended questions to encourage patient engagement")
        
        return feedback, strengths, improvements
    
    async def evaluate_conversation(
        self,
        conversation_history: List[Dict[str, Any]],
        caregiver_responses: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate the overall empathy level of a conversation.
        
        Args:
            conversation_history: Complete conversation history
            caregiver_responses: List of caregiver responses to evaluate
            
        Returns:
            Comprehensive evaluation results
        """
        if not caregiver_responses:
            return {
                "overall_score": 0.0,
                "detailed_scores": {},
                "feedback": ["No caregiver responses to evaluate"],
                "strengths": [],
                "improvements": ["Engage more actively in the conversation"]
            }
        
        # Evaluate each response
        all_metrics = []
        for response in caregiver_responses:
            metrics = self.evaluate_response_patterns(response)
            all_metrics.append(metrics)
        
        # Calculate average metrics
        avg_metrics = EmpathyMetrics()
        if all_metrics:
            avg_metrics.validation_score = sum(m.validation_score for m in all_metrics) / len(all_metrics)
            avg_metrics.emotional_support_score = sum(m.emotional_support_score for m in all_metrics) / len(all_metrics)
            avg_metrics.respect_score = sum(m.respect_score for m in all_metrics) / len(all_metrics)
            avg_metrics.patience_score = sum(m.patience_score for m in all_metrics) / len(all_metrics)
            avg_metrics.communication_clarity_score = sum(m.communication_clarity_score for m in all_metrics) / len(all_metrics)
            avg_metrics.non_confrontational_score = sum(m.non_confrontational_score for m in all_metrics) / len(all_metrics)
        
        # Analyze conversation flow
        conversation_metrics = self.analyze_conversation_flow(conversation_history)
        
        # Calculate overall score
        overall_score = (
            avg_metrics.validation_score * 0.25 +
            avg_metrics.emotional_support_score * 0.2 +
            avg_metrics.respect_score * 0.15 +
            avg_metrics.patience_score * 0.2 +
            avg_metrics.communication_clarity_score * 0.1 +
            avg_metrics.non_confrontational_score * 0.1
        )
        
        # Generate feedback
        feedback, strengths, improvements = self.generate_feedback(avg_metrics, conversation_metrics)
        
        detailed_scores = {
            "validation": avg_metrics.validation_score,
            "emotional_support": avg_metrics.emotional_support_score,
            "respect_and_dignity": avg_metrics.respect_score,
            "patience": avg_metrics.patience_score,
            "communication_clarity": avg_metrics.communication_clarity_score,
            "non_confrontational": avg_metrics.non_confrontational_score,
            "consistency": conversation_metrics["consistency"],
            "adaptability": conversation_metrics["adaptability"],
            "engagement": conversation_metrics["engagement"]
        }
        
        return {
            "overall_score": overall_score,
            "detailed_scores": detailed_scores,
            "feedback": feedback,
            "strengths": strengths,
            "improvements": improvements,
            "evaluation_timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Example usage
    evaluator = EmpathyEvaluator()
    
    # Test responses
    test_responses = [
        "I understand this must be confusing for you.",
        "No, that's wrong. You need to remember.",
        "Tell me more about how you're feeling.",
        "We already talked about this!"
    ]
    
    test_conversation = [
        {"speaker": "caregiver", "message": "I understand this must be confusing for you."},
        {"speaker": "patient", "message": "Where am I?", "mood": "confused"},
        {"speaker": "caregiver", "message": "You're in a safe place. I'm here with you."},
        {"speaker": "patient", "message": "I want to go home.", "mood": "anxious"}
    ]
    
    async def test_evaluation():
        result = await evaluator.evaluate_conversation(test_conversation, test_responses)
        print(f"Overall Score: {result['overall_score']:.2f}")
        print(f"Strengths: {result['strengths']}")
        print(f"Improvements: {result['improvements']}")
    
    asyncio.run(test_evaluation())