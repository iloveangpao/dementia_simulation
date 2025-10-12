"""
Metrics collection for monitoring and dashboards.

This module tracks counters and statistics for the application.
"""

from datetime import datetime
from typing import Any, Dict


class MetricsCollector:
    """Collects and tracks application metrics."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.start_time = datetime.now()
        self.counters: Dict[str, int] = {
            "total_turns": 0,
            "total_sessions": 0,
            "active_sessions": 0,
            "total_errors": 0,
            "total_retrievals": 0,
            "total_evaluations": 0,
        }
        self.flags: Dict[str, int] = {
            "high_confusion": 0,
            "low_empathy": 0,
            "rapid_mood_change": 0,
        }

    def increment(self, counter_name: str, amount: int = 1) -> None:
        """
        Increment a counter.

        Args:
            counter_name: Name of the counter
            amount: Amount to increment by
        """
        if counter_name not in self.counters:
            self.counters[counter_name] = 0
        self.counters[counter_name] += amount

    def set_counter(self, counter_name: str, value: int) -> None:
        """
        Set a counter to a specific value.

        Args:
            counter_name: Name of the counter
            value: Value to set
        """
        self.counters[counter_name] = value

    def increment_flag(self, flag_name: str, amount: int = 1) -> None:
        """
        Increment a flag counter.

        Args:
            flag_name: Name of the flag
            amount: Amount to increment by
        """
        if flag_name not in self.flags:
            self.flags[flag_name] = 0
        self.flags[flag_name] += amount

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.

        Returns:
            Dictionary containing all metrics
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "counters": self.counters.copy(),
            "flags": self.flags.copy(),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.start_time = datetime.now()
        for key in self.counters:
            self.counters[key] = 0
        for key in self.flags:
            self.flags[key] = 0
