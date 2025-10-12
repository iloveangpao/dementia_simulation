"""Tests for telemetry module."""

import json
import tempfile

from src.dementia_simulation.telemetry.logger import TelemetryLogger
from src.dementia_simulation.telemetry.metrics import MetricsCollector


class TestTelemetryLogger:
    """Test TelemetryLogger class."""

    def test_initialization(self):
        """Test logger initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger(log_dir=tmpdir)
            assert logger.log_dir.exists()
            assert str(logger.log_dir) == tmpdir

    def test_log_turn(self):
        """Test logging a conversation turn."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger(log_dir=tmpdir)

            logger.log_turn(
                session_id="session_1",
                turn_number=1,
                user_input="Hello",
                response="Hi there",
                persona_state={"mood": "happy", "stage": "mild"},
                retrieval_hits=[{"text": "doc1", "score": 0.9}],
                flags={"low_confidence": False},
                metadata={"model": "gpt-3.5"},
            )

            # Verify log file exists
            assert logger.log_file.exists()

            # Read and verify content
            with open(logger.log_file, "r") as f:
                line = f.readline()
                entry = json.loads(line)

                assert entry["session_id"] == "session_1"
                assert entry["turn_number"] == 1
                assert entry["user_input"] == "Hello"
                assert entry["response"] == "Hi there"
                assert entry["persona_state"]["mood"] == "happy"
                assert len(entry["retrieval_hits"]) == 1
                assert entry["flags"]["low_confidence"] is False

    def test_log_event(self):
        """Test logging an event."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger(log_dir=tmpdir)

            logger.log_event(
                event_type="session_start",
                session_id="session_1",
                data={"user_id": "user_123"},
            )

            with open(logger.log_file, "r") as f:
                line = f.readline()
                entry = json.loads(line)

                assert entry["event_type"] == "session_start"
                assert entry["session_id"] == "session_1"
                assert entry["data"]["user_id"] == "user_123"

    def test_read_logs_all(self):
        """Test reading all logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger(log_dir=tmpdir)

            # Log multiple turns
            for i in range(5):
                logger.log_turn(
                    session_id=f"session_{i % 2}",
                    turn_number=i,
                    user_input=f"input_{i}",
                    response=f"response_{i}",
                )

            logs = logger.read_logs()
            assert len(logs) == 5

    def test_read_logs_filtered(self):
        """Test reading logs filtered by session ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger(log_dir=tmpdir)

            # Log turns for different sessions
            for i in range(6):
                logger.log_turn(
                    session_id=f"session_{i % 3}",
                    turn_number=i,
                    user_input=f"input_{i}",
                    response=f"response_{i}",
                )

            # Read logs for session_0
            logs = logger.read_logs(session_id="session_0")
            assert len(logs) == 2
            assert all(log["session_id"] == "session_0" for log in logs)

    def test_read_logs_with_limit(self):
        """Test reading logs with a limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger(log_dir=tmpdir)

            # Log many turns
            for i in range(20):
                logger.log_turn(
                    session_id="session_1",
                    turn_number=i,
                    user_input=f"input_{i}",
                    response=f"response_{i}",
                )

            logs = logger.read_logs(limit=5)
            assert len(logs) == 5

    def test_read_logs_empty(self):
        """Test reading logs when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger(log_dir=tmpdir)
            logs = logger.read_logs()
            assert logs == []


class TestMetricsCollector:
    """Test MetricsCollector class."""

    def test_initialization(self):
        """Test metrics collector initialization."""
        collector = MetricsCollector()
        assert "total_turns" in collector.counters
        assert "total_sessions" in collector.counters
        assert collector.counters["total_turns"] == 0

    def test_increment_counter(self):
        """Test incrementing a counter."""
        collector = MetricsCollector()

        collector.increment("total_turns")
        assert collector.counters["total_turns"] == 1

        collector.increment("total_turns", 5)
        assert collector.counters["total_turns"] == 6

    def test_increment_new_counter(self):
        """Test incrementing a new counter."""
        collector = MetricsCollector()

        collector.increment("custom_counter")
        assert collector.counters["custom_counter"] == 1

    def test_set_counter(self):
        """Test setting a counter value."""
        collector = MetricsCollector()

        collector.set_counter("active_sessions", 5)
        assert collector.counters["active_sessions"] == 5

    def test_increment_flag(self):
        """Test incrementing a flag."""
        collector = MetricsCollector()

        collector.increment_flag("high_confusion")
        assert collector.flags["high_confusion"] == 1

        collector.increment_flag("high_confusion", 3)
        assert collector.flags["high_confusion"] == 4

    def test_increment_new_flag(self):
        """Test incrementing a new flag."""
        collector = MetricsCollector()

        collector.increment_flag("custom_flag")
        assert collector.flags["custom_flag"] == 1

    def test_get_metrics(self):
        """Test getting all metrics."""
        collector = MetricsCollector()

        collector.increment("total_turns", 10)
        collector.increment("total_sessions", 3)
        collector.increment_flag("low_empathy", 2)

        metrics = collector.get_metrics()

        assert "timestamp" in metrics
        assert "uptime_seconds" in metrics
        assert metrics["counters"]["total_turns"] == 10
        assert metrics["counters"]["total_sessions"] == 3
        assert metrics["flags"]["low_empathy"] == 2

    def test_reset(self):
        """Test resetting metrics."""
        collector = MetricsCollector()

        collector.increment("total_turns", 10)
        collector.increment_flag("low_empathy", 2)

        collector.reset()

        assert collector.counters["total_turns"] == 0
        assert collector.flags["low_empathy"] == 0

    def test_uptime_tracking(self):
        """Test that uptime is tracked."""
        import time

        collector = MetricsCollector()
        time.sleep(0.1)

        metrics = collector.get_metrics()
        assert metrics["uptime_seconds"] > 0
