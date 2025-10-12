"""Tests for session store module."""

import time

import pytest

from src.dementia_simulation.session.store import InMemorySessionStore


class TestInMemorySessionStore:
    """Test InMemorySessionStore class."""

    def test_initialization(self):
        """Test store initialization."""
        store = InMemorySessionStore(ttl_seconds=60)
        assert store.ttl_seconds == 60
        assert len(store.list_all()) == 0

    def test_set_and_get(self):
        """Test setting and getting a session."""
        store = InMemorySessionStore()
        session_data = {"messages": [], "created_at": "2024-01-01"}
        
        store.set("session_1", session_data)
        retrieved = store.get("session_1")
        
        assert retrieved is not None
        assert retrieved["messages"] == []
        assert retrieved["created_at"] == "2024-01-01"

    def test_get_nonexistent(self):
        """Test getting a nonexistent session."""
        store = InMemorySessionStore()
        assert store.get("nonexistent") is None

    def test_delete(self):
        """Test deleting a session."""
        store = InMemorySessionStore()
        store.set("session_1", {"messages": []})
        
        assert store.delete("session_1") is True
        assert store.get("session_1") is None
        assert store.delete("session_1") is False

    def test_list_all(self):
        """Test listing all session IDs."""
        store = InMemorySessionStore()
        store.set("session_1", {"messages": []})
        store.set("session_2", {"messages": []})
        store.set("session_3", {"messages": []})
        
        session_ids = store.list_all()
        assert len(session_ids) == 3
        assert "session_1" in session_ids
        assert "session_2" in session_ids
        assert "session_3" in session_ids

    def test_clear(self):
        """Test clearing all sessions."""
        store = InMemorySessionStore()
        store.set("session_1", {"messages": []})
        store.set("session_2", {"messages": []})
        
        count = store.clear()
        assert count == 2
        assert len(store.list_all()) == 0

    def test_ttl_expiration(self):
        """Test that sessions expire after TTL."""
        store = InMemorySessionStore(ttl_seconds=1)
        store.set("session_1", {"messages": []})
        
        # Session should exist immediately
        assert store.get("session_1") is not None
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Session should be expired
        assert store.get("session_1") is None

    def test_cleanup_expired(self):
        """Test cleanup of expired sessions."""
        store = InMemorySessionStore(ttl_seconds=1)
        store.set("session_1", {"messages": []})
        store.set("session_2", {"messages": []})
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Add a new session that won't expire
        store.set("session_3", {"messages": []})
        
        # Cleanup should remove 2 expired sessions
        count = store.cleanup_expired()
        assert count == 2
        assert len(store.list_all()) == 1
        assert "session_3" in store.list_all()

    def test_get_refreshes_ttl(self):
        """Test that accessing a session refreshes its TTL."""
        store = InMemorySessionStore(ttl_seconds=2)
        store.set("session_1", {"messages": []})
        
        # Wait halfway to expiration
        time.sleep(1)
        
        # Access the session (should refresh TTL)
        store.get("session_1")
        
        # Wait another second (would be expired without refresh)
        time.sleep(1)
        
        # Session should still exist
        assert store.get("session_1") is not None

    def test_get_or_create_existing(self):
        """Test get_or_create with existing session."""
        store = InMemorySessionStore()
        store.set("session_1", {"messages": ["test"]})
        
        session = store.get_or_create("session_1")
        assert session["messages"] == ["test"]

    def test_get_or_create_new(self):
        """Test get_or_create with new session."""
        store = InMemorySessionStore()
        
        session = store.get_or_create("session_1")
        assert session is not None
        assert "created_at" in session
        assert "messages" in session
        assert session["messages"] == []

    def test_multiple_sessions(self):
        """Test managing multiple sessions."""
        store = InMemorySessionStore()
        
        # Create multiple sessions
        for i in range(10):
            store.set(f"session_{i}", {"index": i})
        
        assert len(store.list_all()) == 10
        
        # Verify each session
        for i in range(10):
            session = store.get(f"session_{i}")
            assert session["index"] == i
        
        # Delete half
        for i in range(0, 10, 2):
            store.delete(f"session_{i}")
        
        assert len(store.list_all()) == 5
