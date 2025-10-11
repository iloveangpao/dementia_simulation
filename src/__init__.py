"""
Dementia simulation package.

This package provides tools for simulating patient personas with dementia,
including memory degradation and mood state management.
"""

from .persona import PatientPersona, DementiaStage, MoodState

__all__ = ['PatientPersona', 'DementiaStage', 'MoodState']