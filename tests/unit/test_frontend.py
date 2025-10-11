"""
Unit tests for the Streamlit frontend application.

These tests verify the frontend components can be imported and basic
functionality is properly structured.
"""

import os
import sys
from pathlib import Path


def test_streamlit_app_imports():
    """Test that the Streamlit app backend dependencies can be imported."""
    # Add frontend and src to path
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    src_path = Path(__file__).parent.parent.parent / "src"
    if str(frontend_path) not in sys.path:
        sys.path.insert(0, str(frontend_path))
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Try importing dementia_simulation modules that frontend depends on
    from dementia_simulation.evaluator.empathy_evaluator import EmpathyEvaluator
    from dementia_simulation.persona.models import (
        DementiaPersona,
        DementiaStage,
        create_sample_personas,
    )
    from dementia_simulation.rag.pipeline import DementiaRAGPipeline
    from dementia_simulation.retriever.faiss_retriever import (
        FAISSRetriever,
        initialize_retriever_with_knowledge_base,
    )

    # Verify key classes can be instantiated
    assert DementiaStage is not None
    assert EmpathyEvaluator is not None
    assert DementiaRAGPipeline is not None
    assert FAISSRetriever is not None


def test_streamlit_app_file_exists():
    """Test that the Streamlit app file exists."""
    app_path = Path(__file__).parent.parent.parent / "frontend" / "streamlit_app.py"
    assert app_path.exists(), "streamlit_app.py should exist in frontend directory"
    assert app_path.is_file(), "streamlit_app.py should be a file"


def test_streamlit_app_has_main_function():
    """Test that the Streamlit app has a main function."""
    app_path = Path(__file__).parent.parent.parent / "frontend" / "streamlit_app.py"
    with open(app_path, "r") as f:
        content = f.read()
        assert "def main():" in content, "App should have a main() function"
        assert 'if __name__ == "__main__":' in content, "App should be executable"


def test_streamlit_app_has_required_components():
    """Test that the Streamlit app includes required UI components."""
    app_path = Path(__file__).parent.parent.parent / "frontend" / "streamlit_app.py"
    with open(app_path, "r") as f:
        content = f.read()

        # Check for key UI components mentioned in the issue
        assert (
            "st.columns" in content or "left_col" in content
        ), "App should have two-panel layout"
        assert "Chat" in content, "App should have chat interface"
        assert (
            "Mood" in content or "mood" in content
        ), "App should have mood tracking"
        assert (
            "Performance" in content or "evaluation" in content
        ), "App should have performance monitoring"

        # Check for session state management
        assert "st.session_state" in content, "App should use session state"
        assert (
            "conversation_history" in content
        ), "App should track conversation history"


def test_streamlit_config_is_wide_layout():
    """Test that the app uses wide layout as specified in the issue."""
    app_path = Path(__file__).parent.parent.parent / "frontend" / "streamlit_app.py"
    with open(app_path, "r") as f:
        content = f.read()
        assert 'layout="wide"' in content, "App should use wide layout"


def test_persona_models_integration():
    """Test that persona models can be created for the frontend."""
    from dementia_simulation.persona.models import (
        DementiaStage,
        create_sample_personas,
    )

    personas = create_sample_personas()
    assert len(personas) > 0, "Should have at least one sample persona"

    for persona in personas:
        assert hasattr(persona, "name"), "Persona should have a name"
        assert hasattr(persona, "stage"), "Persona should have a stage"
        assert hasattr(persona, "current_mood"), "Persona should have current_mood"
        assert isinstance(
            persona.stage, DementiaStage
        ), "Stage should be DementiaStage enum"


def test_evaluator_can_be_initialized():
    """Test that the empathy evaluator can be initialized."""
    from dementia_simulation.evaluator.empathy_evaluator import EmpathyEvaluator

    evaluator = EmpathyEvaluator()
    assert evaluator is not None, "Evaluator should be initialized"
