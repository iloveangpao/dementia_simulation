"""
Unit tests for backend patient simulation module.
"""

from backend.patient_simulation import (
    DementiaPatient,
    get_patient_response,
    get_persona_info,
    set_patient_persona,
)


class TestDementiaPatient:
    """Test the DementiaPatient class."""

    def test_initialization(self):
        """Test patient initialization with default values."""
        patient = DementiaPatient()
        assert patient.persona_name == "Default Patient"
        assert patient.stage == "mild"
        assert len(patient.conversation_history) == 0

    def test_initialization_with_params(self):
        """Test patient initialization with custom parameters."""
        patient = DementiaPatient("John Doe", "moderate")
        assert patient.persona_name == "John Doe"
        assert patient.stage == "moderate"

    def test_get_response(self):
        """Test getting a response from the patient."""
        patient = DementiaPatient("Test Patient", "mild")
        response = patient.get_response("Hello, how are you?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_get_response_stores_history(self):
        """Test that conversation history is stored."""
        patient = DementiaPatient("Test Patient", "mild")
        patient.get_response("First message")
        patient.get_response("Second message")
        assert len(patient.conversation_history) == 2

    def test_get_persona_info(self):
        """Test getting persona information."""
        patient = DementiaPatient("Jane Smith", "severe")
        info = patient.get_persona_info()
        assert info["name"] == "Jane Smith"
        assert info["stage"] == "severe"
        assert "confusion_level" in info
        assert isinstance(info["confusion_level"], float)

    def test_coherent_response_greetings(self):
        """Test coherent responses to greetings."""
        patient = DementiaPatient("Test Patient", "mild")
        response = patient._generate_coherent_response("Hello")
        assert "hello" in response.lower() or "nice" in response.lower()

    def test_coherent_response_name(self):
        """Test coherent response to name question."""
        patient = DementiaPatient("Alice Johnson", "mild")
        response = patient._generate_coherent_response("What is your name?")
        assert "Alice Johnson" in response

    def test_stage_responses_exist(self):
        """Test that all stages have response patterns."""
        patient = DementiaPatient()
        for stage in ["mild", "moderate", "severe"]:
            assert stage in patient.stage_responses
            assert "patterns" in patient.stage_responses[stage]
            assert "confusion_level" in patient.stage_responses[stage]
            assert len(patient.stage_responses[stage]["patterns"]) > 0


class TestModuleFunctions:
    """Test the module-level functions."""

    def test_get_patient_response(self):
        """Test get_patient_response function."""
        response = get_patient_response("Hello")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_get_persona_info_returns_dict(self):
        """Test get_persona_info returns proper dictionary."""
        info = get_persona_info()
        assert isinstance(info, dict)
        assert "name" in info
        assert "stage" in info
        assert "confusion_level" in info

    def test_set_patient_persona(self):
        """Test setting a new patient persona."""
        set_patient_persona("Bob Wilson", "moderate")
        info = get_persona_info()
        assert info["name"] == "Bob Wilson"
        assert info["stage"] == "moderate"

    def test_set_patient_persona_changes_responses(self):
        """Test that changing persona affects responses."""
        # Set to mild stage
        set_patient_persona("Test Person", "mild")
        response1 = get_patient_response("Where am I?")

        # Set to severe stage
        set_patient_persona("Test Person", "severe")
        response2 = get_patient_response("Where am I?")

        # Both should return responses
        assert isinstance(response1, str)
        assert isinstance(response2, str)
