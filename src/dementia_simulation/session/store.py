"""
Session store implementations for managing conversation sessions.

This module provides pluggable session stores with TTL support.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class SessionStore(ABC):
    """Abstract base class for session storage."""

    @abstractmethod
    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        pass

    @abstractmethod
    def set(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Store or update a session."""
        pass

    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """Delete a session. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def list_all(self) -> List[str]:
        """List all session IDs."""
        pass

    @abstractmethod
    def clear(self) -> int:
        """Clear all sessions. Returns the number of sessions deleted."""
        pass

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns the number of sessions deleted."""
        pass


class InMemorySessionStore(SessionStore):
    """In-memory session store with TTL support."""

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize the in-memory session store.

        Args:
            ttl_seconds: Time-to-live for sessions in seconds (default: 1 hour)
        """
        self.ttl_seconds = ttl_seconds
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._expiry_times: Dict[str, float] = {}

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        # Cleanup expired sessions first
        self._cleanup_if_expired(session_id)

        if session_id not in self._sessions:
            return None

        # Update expiry time on access
        self._expiry_times[session_id] = time.time() + self.ttl_seconds
        return self._sessions[session_id]

    def set(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Store or update a session."""
        self._sessions[session_id] = session_data
        self._expiry_times[session_id] = time.time() + self.ttl_seconds

    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            del self._expiry_times[session_id]
            return True
        return False

    def list_all(self) -> List[str]:
        """List all session IDs."""
        # Cleanup expired sessions first
        self.cleanup_expired()
        return list(self._sessions.keys())

    def clear(self) -> int:
        """Clear all sessions."""
        count = len(self._sessions)
        self._sessions.clear()
        self._expiry_times.clear()
        return count

    def cleanup_expired(self) -> int:
        """Remove expired sessions."""
        current_time = time.time()
        expired = [
            session_id
            for session_id, expiry_time in self._expiry_times.items()
            if expiry_time < current_time
        ]

        for session_id in expired:
            del self._sessions[session_id]
            del self._expiry_times[session_id]

        return len(expired)

    def _cleanup_if_expired(self, session_id: str) -> None:
        """Clean up a specific session if expired."""
        if session_id in self._expiry_times:
            if self._expiry_times[session_id] < time.time():
                del self._sessions[session_id]
                del self._expiry_times[session_id]

    def get_or_create(self, session_id: str) -> Dict[str, Any]:
        """Get or create a session."""
        session = self.get(session_id)
        if session is None:
            session = {
                "created_at": datetime.now(),
                "messages": [],
                "current_persona": None,
            }
            self.set(session_id, session)
        return session
