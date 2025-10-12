"""
Structured logging for conversation turns and events.

This module provides per-turn JSON logging with persona state,
retrieval hits, and flags.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TelemetryLogger:
    """Structured logger for conversation telemetry."""

    def __init__(self, log_dir: str = "logs/telemetry"):
        """
        Initialize the telemetry logger.

        Args:
            log_dir: Directory to store telemetry logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        self.log_file = self.log_dir / f"telemetry_{date_str}.jsonl"

    def log_turn(
        self,
        session_id: str,
        turn_number: int,
        user_input: str,
        response: str,
        persona_state: Optional[Dict[str, Any]] = None,
        retrieval_hits: Optional[List[Dict[str, Any]]] = None,
        flags: Optional[Dict[str, bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a conversation turn with structured data.

        Args:
            session_id: Unique session identifier
            turn_number: Turn number in the conversation
            user_input: User's input message
            response: System's response
            persona_state: Current persona state (mood, stage, etc.)
            retrieval_hits: Retrieved documents used
            flags: Boolean flags for special conditions
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "turn_number": turn_number,
            "user_input": user_input,
            "response": response,
            "persona_state": persona_state or {},
            "retrieval_hits": retrieval_hits or [],
            "flags": flags or {},
            "metadata": metadata or {},
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def log_event(
        self,
        event_type: str,
        session_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a system event.

        Args:
            event_type: Type of event (e.g., 'session_start', 'session_end', 'error')
            session_id: Optional session identifier
            data: Event data
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "data": data or {},
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def read_logs(
        self,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read logs, optionally filtered by session ID.

        Args:
            session_id: Optional session ID to filter by
            limit: Optional maximum number of logs to return

        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []

        logs = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if session_id is None or entry.get("session_id") == session_id:
                        logs.append(entry)
                        if limit and len(logs) >= limit:
                            break
                except json.JSONDecodeError:
                    continue

        return logs
