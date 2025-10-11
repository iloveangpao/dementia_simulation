"""
Unit tests for CLI REPL interface.
"""

import os
import tempfile
from unittest.mock import patch

from frontend.cli.main import DementiaSimulationREPL, TranscriptLogger


class TestTranscriptLogger:
    """Test the TranscriptLogger class."""

    def test_initialization_creates_logs_dir(self):
        """Test that logger creates logs directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = os.path.join(tmpdir, "test_logs")
            logger = TranscriptLogger(logs_dir=logs_dir)
            assert os.path.exists(logs_dir)
            assert logger.current_session_file is not None

    def test_session_file_created(self):
        """Test that session file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TranscriptLogger(logs_dir=tmpdir)
            assert os.path.exists(logger.current_session_file)

    def test_session_file_has_header(self):
        """Test that session file has proper header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TranscriptLogger(logs_dir=tmpdir)
            with open(logger.current_session_file, "r") as f:
                content = f.read()
                assert "Dementia Simulation Conversation Log" in content
                assert "Session started:" in content

    def test_log_interaction(self):
        """Test logging an interaction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TranscriptLogger(logs_dir=tmpdir)
            logger.log_interaction(
                persona_name="Test Patient",
                stage="mild",
                caregiver_input="Hello",
                patient_response="Hi there",
            )

            with open(logger.current_session_file, "r") as f:
                content = f.read()
                assert "Test Patient" in content
                assert "mild" in content
                assert "Caregiver: Hello" in content
                assert "Patient: Hi there" in content

    def test_log_session_end(self):
        """Test logging session end."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TranscriptLogger(logs_dir=tmpdir)
            logger.log_session_end()

            with open(logger.current_session_file, "r") as f:
                content = f.read()
                assert "Session ended:" in content

    def test_multiple_interactions(self):
        """Test logging multiple interactions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TranscriptLogger(logs_dir=tmpdir)
            logger.log_interaction("Patient 1", "mild", "Input 1", "Response 1")
            logger.log_interaction("Patient 1", "mild", "Input 2", "Response 2")

            with open(logger.current_session_file, "r") as f:
                content = f.read()
                assert "Input 1" in content
                assert "Input 2" in content
                assert "Response 1" in content
                assert "Response 2" in content


class TestDementiaSimulationREPL:
    """Test the DementiaSimulationREPL class."""

    def test_initialization(self):
        """Test REPL initialization."""
        repl = DementiaSimulationREPL()
        assert repl.logger is not None
        assert repl.running is True

    def test_handle_quit_command(self):
        """Test /quit command."""
        repl = DementiaSimulationREPL()
        result = repl.handle_command("/quit")
        assert result is True
        assert repl.running is False

    @patch("frontend.cli.main.set_patient_persona")
    def test_handle_persona_command(self, mock_set_persona):
        """Test /persona command."""
        repl = DementiaSimulationREPL()
        result = repl.handle_command("/persona John Smith mild")
        assert result is True
        mock_set_persona.assert_called_once_with("John Smith", "mild")

    @patch("frontend.cli.main.set_patient_persona")
    def test_handle_persona_command_multi_word_name(self, mock_set_persona):
        """Test /persona command with multi-word name."""
        repl = DementiaSimulationREPL()
        result = repl.handle_command("/persona Mary Jane Watson moderate")
        assert result is True
        mock_set_persona.assert_called_once_with("Mary Jane Watson", "moderate")

    def test_handle_persona_command_invalid_stage(self):
        """Test /persona command with invalid stage."""
        repl = DementiaSimulationREPL()
        result = repl.handle_command("/persona John Doe invalid_stage")
        assert result is True  # Command is handled, even if invalid

    def test_handle_persona_command_incomplete(self):
        """Test /persona command with incomplete arguments."""
        repl = DementiaSimulationREPL()
        result = repl.handle_command("/persona John")
        assert result is True  # Command is handled, shows usage

    def test_handle_non_command(self):
        """Test handling non-command input."""
        repl = DementiaSimulationREPL()
        result = repl.handle_command("Hello, how are you?")
        assert result is False  # Not a command

    @patch("frontend.cli.main.get_persona_info")
    def test_display_persona_info(self, mock_get_info):
        """Test displaying persona info."""
        mock_get_info.return_value = {"name": "Test Patient", "stage": "mild"}
        repl = DementiaSimulationREPL()

        # Should not raise any errors
        repl.display_persona_info()
        mock_get_info.assert_called_once()

    def test_display_welcome(self):
        """Test displaying welcome message."""
        repl = DementiaSimulationREPL()
        # Should not raise any errors
        repl.display_welcome()
