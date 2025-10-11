"""
Command-line interface for the dementia simulation chatbot.

This module provides a CLI for interacting with dementia personas,
managing conversations, and evaluating caregiver empathy.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import click

from ..evaluator.empathy_evaluator import EmpathyEvaluator

# Import local modules
from ..persona.models import DementiaPersona, DementiaStage, create_sample_personas
from ..rag.pipeline import DementiaRAGPipeline
from ..retriever.faiss_retriever import (
    FAISSRetriever,
    initialize_retriever_with_knowledge_base,
)


class CLISession:
    """Manages CLI session state."""

    def __init__(self):
        self.rag_pipeline: Optional[DementiaRAGPipeline] = None
        self.personas: Dict[str, DementiaPersona] = {}
        self.current_persona: Optional[DementiaPersona] = None
        self.conversation_history: List[Dict] = []
        self.evaluator: Optional[EmpathyEvaluator] = None
        self.session_start = datetime.now()

    async def initialize(self):
        """Initialize the CLI session."""
        click.echo("🧠 Initializing Dementia Simulation Chatbot...")

        # Initialize retriever
        click.echo("📚 Loading knowledge base...")
        retriever = FAISSRetriever()
        initialize_retriever_with_knowledge_base(retriever)

        # Initialize RAG pipeline
        click.echo("🤖 Setting up AI pipeline...")
        use_openai = os.getenv("OPENAI_API_KEY") is not None
        if use_openai:
            click.echo("   Using OpenAI API")
        else:
            click.echo("   Using local models (or mock responses)")

        self.rag_pipeline = DementiaRAGPipeline(
            retriever=retriever, use_openai=use_openai
        )

        # Load personas
        click.echo("👥 Loading personas...")
        sample_personas = create_sample_personas()
        for i, persona in enumerate(sample_personas):
            persona_id = f"persona_{i+1}"
            self.personas[persona_id] = persona
            click.echo(f"   - {persona.name} ({persona.stage.value} dementia)")

        # Initialize evaluator
        self.evaluator = EmpathyEvaluator()

        click.echo("✅ Initialization complete!\n")


# Global session
cli_session = CLISession()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Dementia Simulation Chatbot CLI

    A tool for practicing empathetic communication with dementia patients.
    """
    pass


@cli.command()
@click.option(
    "--persona-id", help="Persona ID to use (persona_1, persona_2, persona_3)"
)
@click.option("--save-session", is_flag=True, help="Save conversation session")
def chat(persona_id: Optional[str], save_session: bool):
    """
    Start an interactive chat session with a dementia persona.
    """

    async def run_chat():
        nonlocal persona_id
        await cli_session.initialize()

        # Select persona
        if persona_id is not None and persona_id in cli_session.personas:
            persona = cli_session.personas[persona_id]
        else:
            click.echo("Available personas:")
            for pid, persona in cli_session.personas.items():
                click.echo(
                    f"  {pid}: {persona.name} - {persona.age} years old, {persona.stage.value} dementia"
                )

            if not persona_id:
                persona_id = click.prompt("\nSelect persona ID", default="persona_1")

            if persona_id not in cli_session.personas:
                click.echo(f"❌ Persona '{persona_id}' not found.")
                return

            persona = cli_session.personas[persona_id]

        cli_session.current_persona = persona

        # Display persona information
        click.echo(f"\n🎭 Starting conversation with {persona.name}")
        click.echo(f"   Age: {persona.age}")
        click.echo(f"   Dementia stage: {persona.stage.value}")
        click.echo(f"   Current mood: {persona.current_mood.value}")

        if persona.background:
            click.echo("   Background:")
            for key, value in persona.background.items():
                click.echo(f"     {key}: {value}")

        click.echo(f"\n💡 Tips for {persona.stage.value} dementia:")
        if persona.stage == DementiaStage.MILD:
            click.echo("   - Be patient with memory lapses")
            click.echo("   - Validate their feelings")
            click.echo("   - Offer gentle reminders")
        elif persona.stage == DementiaStage.MODERATE:
            click.echo("   - Speak slowly and clearly")
            click.echo("   - Avoid arguments or corrections")
            click.echo("   - Use validation therapy")
            click.echo("   - Be prepared for repetition")
        else:  # SEVERE
            click.echo("   - Use simple, short sentences")
            click.echo("   - Focus on emotions, not facts")
            click.echo("   - Provide constant reassurance")
            click.echo("   - Be very patient and gentle")

        click.echo(
            "\n💬 Start your conversation (type 'quit' to end, 'help' for commands):"
        )
        click.echo("-" * 60)

        caregiver_responses = []

        while True:
            try:
                user_input = click.prompt("\n[You]", type=str)

                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                elif user_input.lower() == "help":
                    click.echo("\nCommands:")
                    click.echo("  quit/exit/q - End conversation")
                    click.echo("  help - Show this help")
                    click.echo("  mood - Check current persona mood")
                    click.echo("  evaluate - Get empathy evaluation")
                    continue
                elif user_input.lower() == "mood":
                    click.echo(f"Current mood: {persona.current_mood.value}")
                    continue
                elif user_input.lower() == "evaluate":
                    if caregiver_responses:
                        await show_evaluation(caregiver_responses)
                    else:
                        click.echo("No responses to evaluate yet.")
                    continue

                # Generate response
                click.echo("   🤔 Thinking...", nl=False)

                response = await cli_session.rag_pipeline.generate_response(
                    user_input=user_input,
                    persona=persona,
                    conversation_history=cli_session.conversation_history,
                )

                click.echo(f"\r[{persona.name}] {response.response_text}")
                click.echo(
                    f"   💭 Mood: {response.persona_mood} | Confidence: {response.confidence_score:.2f}"
                )

                # Store conversation
                cli_session.conversation_history.append(
                    {
                        "speaker": "caregiver",
                        "message": user_input,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                cli_session.conversation_history.append(
                    {
                        "speaker": "patient",
                        "message": response.response_text,
                        "timestamp": datetime.now().isoformat(),
                        "mood": response.persona_mood,
                    }
                )

                caregiver_responses.append(user_input)

            except KeyboardInterrupt:
                click.echo("\n\n👋 Conversation ended by user.")
                break
            except Exception as e:
                click.echo(f"\n❌ Error: {e}")

        # End of conversation
        click.echo("\n" + "=" * 60)
        click.echo("📊 Conversation Summary:")
        click.echo(f"   Duration: {datetime.now() - cli_session.session_start}")
        click.echo(f"   Messages exchanged: {len(cli_session.conversation_history)}")

        if caregiver_responses:
            click.echo("\n🎯 Final Empathy Evaluation:")
            await show_evaluation(caregiver_responses)

        # Save session if requested
        if save_session and cli_session.conversation_history:
            await save_conversation_session()

    asyncio.run(run_chat())


async def show_evaluation(caregiver_responses: List[str]):
    """Show empathy evaluation results."""
    try:
        evaluation = await cli_session.evaluator.evaluate_conversation(
            conversation_history=cli_session.conversation_history,
            caregiver_responses=caregiver_responses,
        )

        click.echo(f"\n📈 Overall Empathy Score: {evaluation['overall_score']:.2f}/1.0")

        # Detailed scores
        click.echo("\n📋 Detailed Scores:")
        for category, score in evaluation["detailed_scores"].items():
            category_name = category.replace("_", " ").title()
            click.echo(f"   {category_name}: {score:.2f}")

        # Strengths
        if evaluation["strengths"]:
            click.echo("\n✅ Strengths:")
            for strength in evaluation["strengths"]:
                click.echo(f"   • {strength}")

        # Improvements
        if evaluation["improvements"]:
            click.echo("\n🎯 Areas for Improvement:")
            for improvement in evaluation["improvements"]:
                click.echo(f"   • {improvement}")

        # Feedback
        if evaluation["feedback"]:
            click.echo("\n💡 Specific Feedback:")
            for feedback in evaluation["feedback"]:
                click.echo(f"   • {feedback}")

    except Exception as e:
        click.echo(f"❌ Error evaluating empathy: {e}")


async def save_conversation_session():
    """Save the conversation session to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    persona_name = cli_session.current_persona.name.lower().replace(" ", "_")
    filename = f"conversation_{persona_name}_{timestamp}.json"

    session_data = {
        "session_info": {
            "timestamp": cli_session.session_start.isoformat(),
            "duration": str(datetime.now() - cli_session.session_start),
            "persona": cli_session.current_persona.to_dict(),
        },
        "conversation_history": cli_session.conversation_history,
    }

    # Ensure data directory exists
    os.makedirs("data/sessions", exist_ok=True)
    filepath = f"data/sessions/{filename}"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    click.echo(f"💾 Session saved to {filepath}")


@cli.command()
def personas():
    """List all available personas."""

    async def list_personas():
        await cli_session.initialize()

        click.echo("👥 Available Personas:\n")

        for persona_id, persona in cli_session.personas.items():
            click.echo(f"🎭 {persona_id}: {persona.name}")
            click.echo(f"   Age: {persona.age}")
            click.echo(f"   Stage: {persona.stage.value}")
            click.echo(f"   Mood: {persona.current_mood.value}")

            if persona.background:
                click.echo("   Background:")
                for key, value in persona.background.items():
                    click.echo(f"     • {key}: {value}")

            click.echo()

    asyncio.run(list_personas())


@cli.command()
@click.argument("session_file", type=click.Path(exists=True))
def analyze(session_file: str):
    """Analyze a saved conversation session."""

    async def analyze_session():
        await cli_session.initialize()

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            click.echo(f"📄 Analyzing session: {session_file}")
            click.echo(f"   Date: {session_data['session_info']['timestamp']}")
            click.echo(f"   Duration: {session_data['session_info']['duration']}")
            click.echo(f"   Persona: {session_data['session_info']['persona']['name']}")

            # Extract caregiver responses
            caregiver_responses = [
                msg["message"]
                for msg in session_data["conversation_history"]
                if msg["speaker"] == "caregiver"
            ]

            if caregiver_responses:
                evaluation = await cli_session.evaluator.evaluate_conversation(
                    conversation_history=session_data["conversation_history"],
                    caregiver_responses=caregiver_responses,
                )

                click.echo("\n📊 Analysis Results:")
                click.echo(f"   Overall Score: {evaluation['overall_score']:.2f}/1.0")

                click.echo("\n📋 Detailed Scores:")
                for category, score in evaluation["detailed_scores"].items():
                    click.echo(f"   {category.replace('_', ' ').title()}: {score:.2f}")

                if evaluation["strengths"]:
                    click.echo("\n✅ Strengths:")
                    for strength in evaluation["strengths"]:
                        click.echo(f"   • {strength}")

                if evaluation["improvements"]:
                    click.echo("\n🎯 Improvements:")
                    for improvement in evaluation["improvements"]:
                        click.echo(f"   • {improvement}")
            else:
                click.echo("No caregiver responses found in session.")

        except Exception as e:
            click.echo(f"❌ Error analyzing session: {e}")

    asyncio.run(analyze_session())


@cli.command()
@click.option("--port", default=8000, help="Port to run the server on")
@click.option("--host", default="localhost", help="Host to run the server on")
def server(port: int, host: str):
    """Start the FastAPI server."""
    try:
        import uvicorn

        click.echo(f"🚀 Starting server on http://{host}:{port}")
        click.echo("📚 API documentation available at http://localhost:8000/docs")

        uvicorn.run(
            "dementia_simulation.api.server:app", host=host, port=port, reload=True
        )
    except ImportError:
        click.echo(
            "❌ FastAPI/Uvicorn not available. Install with: pip install fastapi uvicorn"
        )
    except Exception as e:
        click.echo(f"❌ Error starting server: {e}")


@cli.command()
def streamlit():
    """Start the Streamlit web interface."""
    try:
        import subprocess

        click.echo("🌐 Starting Streamlit web interface...")

        # Create streamlit app path
        streamlit_app = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "frontend", "streamlit_app.py"
        )

        if not os.path.exists(streamlit_app):
            click.echo(f"❌ Streamlit app not found at {streamlit_app}")
            return

        subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_app])

    except ImportError:
        click.echo("❌ Streamlit not available. Install with: pip install streamlit")
    except Exception as e:
        click.echo(f"❌ Error starting Streamlit: {e}")


@cli.command()
def setup():
    """Setup the dementia simulation environment."""
    click.echo("🔧 Setting up Dementia Simulation environment...\n")

    # Create directories
    directories = [
        "data/sessions",
        "data/knowledge_base",
        "data/personas",
        "embeddings",
        "logs",
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        click.echo(f"📁 Created directory: {directory}")

    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# Dementia Simulation Configuration
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
DEFAULT_MODEL=microsoft/DialoGPT-medium
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_HOST=localhost
API_PORT=8000
LOG_LEVEL=INFO
""")
        click.echo("📝 Created .env configuration file")

    click.echo("\n✅ Setup complete!")
    click.echo("\n📖 Next steps:")
    click.echo("   1. Edit .env file with your API keys (optional)")
    click.echo("   2. Run 'dementia-sim chat' to start a conversation")
    click.echo("   3. Run 'dementia-sim server' to start the API server")
    click.echo("   4. Run 'dementia-sim streamlit' for the web interface")


if __name__ == "__main__":
    cli()
