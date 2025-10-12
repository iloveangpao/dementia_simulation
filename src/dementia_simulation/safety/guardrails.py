"""
Safety guardrails for dementia simulation.

This module provides hard filters for unsafe content including:
- Medical advice
- Coercive language
- Derogatory language
- Other harmful content
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ViolationType(Enum):
    """Types of safety violations."""

    MEDICAL_ADVICE = "medical_advice"
    COERCIVE = "coercive"
    DEROGATORY = "derogatory"
    HARMFUL = "harmful"
    INAPPROPRIATE = "inappropriate"


@dataclass
class SafetyViolation:
    """Represents a safety violation found in text."""

    violation_type: ViolationType
    matched_pattern: str
    confidence: float  # 0.0 to 1.0
    context: str  # The surrounding text


class SafetyGuardrails:
    """
    Safety guardrails for filtering unsafe content in dementia simulation.

    Provides hard filters for medical advice, coercive language,
    derogatory language, and other harmful content.
    """

    # Medical advice patterns
    MEDICAL_ADVICE_PATTERNS = [
        r"\b(take|prescribe|prescribed)\b.{0,30}\b\d+\s*(mg|pill|tablet|tablets|dose)\b",
        r"\bshould take\b.{0,30}\b(medication|medicine|drug|aspirin|pill)\b",
        (
            r"\b(you have|you are|looks like).{0,30}\b(high|low)\b.{0,20}"
            r"\b(blood pressure|sugar|cholesterol)\b"
        ),
        r"\b(increase|decrease|adjust)\b.{0,30}\b(medication|medicine|drug|dose|pill)\b",
        r"\bstop taking\b.{0,30}\b(medicine|medication|pill|your pills)\b",
        r"\b(cure|heal|treat)\b.{0,30}\b(with|using|by taking)\b",
        (
            r"\byou (need|should|must) (see|visit|go to)\b.{0,30}"
            r"\b(doctor|hospital|emergency)\b"
        ),
        (
            r"\b(blood pressure|heart rate|sugar level|cholesterol)\b.{0,30}"
            r"\b(is|seems|looks|appears).{0,20}\b(high|low|abnormal|dangerous)\b"
        ),
        (
            r"\b(symptoms|condition)\b.{0,30}\b(indicate|suggest|mean|is).{0,30}"
            r"\b(you (might |are )?have|diabetes|disease|serious|very sick)\b"
        ),
    ]

    # Coercive language patterns
    COERCIVE_PATTERNS = [
        r"\byou (must|have to|need to|will) (do|comply|obey|listen|take)\b",
        r"\b(do as (I say|told)|follow (orders|instructions))\b",
        r"\b(or else|otherwise|if you don't).{0,30}\b(bad|punish|consequence|regret)\b",
        r"\b(force|make you|compel)\b",
        r"\bshut up\b",
        r"\b(be quiet|stop talking) (now|immediately)\b",
        r"\byou('re| are) going to\b.{0,30}\b(whether you like it|like it or not)\b",
        r"\bmust take.{0,30}\b(medication|now|or else)\b",
    ]

    # Derogatory language patterns
    DEROGATORY_PATTERNS = [
        r"\b(stupid|idiot|moron|dumb|crazy|insane|lunatic|psycho)\b",
        r"\byou('re| are) (worthless|useless|pathetic|incompetent)\b",
        r"\bwhat('s| is) wrong with you\b",
        r"\b(senile|demented) (old )?(person|man|woman|fool)\b",
        r"\bacting like (a child|baby|fool)\b",
        r"\b(get over it|stop complaining|quit whining)\b",
        r"\byou('re| are|'ve| have).{0,30}\b(burden|problem|nuisance)\b",
        (
            r"\b(burden|problem|nuisance).{0,30}"
            r"\b(you are|you've become|to everyone|lately)\b"
        ),
        r"\bbecoming.{0,20}\b(burden|nuisance)\b",
        r"\blose your mind\b",
        r"\bcan't (remember|think) anything\b",
    ]

    # Harmful patterns
    HARMFUL_PATTERNS = [
        r"\b(hurt|harm|hit|strike|slap|push)\b.{0,30}\byou\b",
        r"\b(threat|threaten)\b",
        (
            r"\b(you'll be |you will be )?(locked|lock|restrain|tie).{0,30}"
            r"\b(you|up|in your room)\b"
        ),
        r"\bno one (cares|loves|wants)\b",
        r"\byou('re| are) (alone|abandoned|forgotten)\b",
        r"\b(die|death|kill)\b",
    ]

    # Inappropriate patterns
    INAPPROPRIATE_PATTERNS = [
        r"\b(sexual|intimate|naked|undress)\b",
        r"\byou (deserve|earned) (this|it|punishment)\b",
        r"\byou('re| are).{0,20}\b(lie|lying|liar)\b",
        r"\b(liar).{0,20}\byou (are|know it)\b",
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize safety guardrails.

        Args:
            strict_mode: If True, applies stricter filtering
        """
        self.strict_mode = strict_mode
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        self.compiled_patterns = {
            ViolationType.MEDICAL_ADVICE: [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.MEDICAL_ADVICE_PATTERNS
            ],
            ViolationType.COERCIVE: [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.COERCIVE_PATTERNS
            ],
            ViolationType.DEROGATORY: [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.DEROGATORY_PATTERNS
            ],
            ViolationType.HARMFUL: [
                re.compile(pattern, re.IGNORECASE) for pattern in self.HARMFUL_PATTERNS
            ],
            ViolationType.INAPPROPRIATE: [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.INAPPROPRIATE_PATTERNS
            ],
        }

    def check_text(self, text: str) -> List[SafetyViolation]:
        """
        Check text for safety violations.

        Args:
            text: Text to check

        Returns:
            List of safety violations found (empty if safe)
        """
        if not text or not isinstance(text, str):
            return []

        violations = []
        text_lower = text.lower()

        for violation_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text_lower)
                for match in matches:
                    # Extract context (50 chars before and after)
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    violation = SafetyViolation(
                        violation_type=violation_type,
                        matched_pattern=match.group(),
                        confidence=1.0 if self.strict_mode else 0.8,
                        context=context.strip(),
                    )
                    violations.append(violation)

        return violations

    def is_safe(self, text: str) -> bool:
        """
        Check if text is safe (no violations).

        Args:
            text: Text to check

        Returns:
            True if safe, False if violations found
        """
        return len(self.check_text(text)) == 0

    def filter_response(
        self, text: str, replacement: Optional[str] = None
    ) -> tuple[str, List[SafetyViolation]]:
        """
        Filter unsafe content from text.

        Args:
            text: Text to filter
            replacement: Optional replacement text for unsafe content

        Returns:
            Tuple of (filtered_text, violations_found)
        """
        violations = self.check_text(text)

        if not violations:
            return text, []

        if replacement is None:
            replacement = (
                "[This response was filtered for safety. "
                "Please rephrase using supportive, non-judgmental language.]"
            )

        # If any violations found, replace entire response
        return replacement, violations

    def get_suggestion(self, violation: SafetyViolation) -> str:
        """
        Get a suggestion for how to rephrase based on violation type.

        Args:
            violation: The safety violation

        Returns:
            Suggestion text
        """
        suggestions = {
            ViolationType.MEDICAL_ADVICE: (
                "Instead of giving medical advice, suggest consulting "
                "with their healthcare provider."
            ),
            ViolationType.COERCIVE: (
                "Use collaborative language like 'Would you like to...' "
                "or 'Let's try...' instead of commands."
            ),
            ViolationType.DEROGATORY: (
                "Use respectful, person-first language. Remember they are "
                "a person with dementia, not defined by it."
            ),
            ViolationType.HARMFUL: (
                "Avoid any language that could be perceived as threatening "
                "or harmful. Focus on safety and reassurance."
            ),
            ViolationType.INAPPROPRIATE: (
                "Keep communication appropriate and professional. "
                "Focus on comfort and dignity."
            ),
        }
        return suggestions.get(
            violation.violation_type,
            "Please rephrase using supportive, empathetic language.",
        )
