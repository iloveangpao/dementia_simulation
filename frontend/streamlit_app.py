"""
Streamlit web interface for the dementia simulation chatbot.

This module provides a user-friendly web interface for practicing
empathetic communication with dementia patients.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

try:
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
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="Dementia Simulation Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
.persona-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 5px solid #1f77b4;
}

.chat-message {
    padding: 10px;
    margin: 5px 0;
    border-radius: 10px;
}

.user-message {
    background-color: #dcf8c6;
    margin-left: 20px;
}

.bot-message {
    background-color: #f1f1f1;
    margin-right: 20px;
}

.empathy-score {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}

.score-excellent {
    background-color: #d4edda;
    color: #155724;
}

.score-good {
    background-color: #fff3cd;
    color: #856404;
}

.score-needs-improvement {
    background-color: #f8d7da;
    color: #721c24;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def initialize_components():
    """Initialize and cache the application components."""
    with st.spinner("🧠 Initializing AI components..."):
        try:
            # Initialize retriever
            retriever = FAISSRetriever()
            initialize_retriever_with_knowledge_base(retriever)

            # Initialize RAG pipeline
            use_openai = os.getenv("OPENAI_API_KEY") is not None
            rag_pipeline = DementiaRAGPipeline(
                retriever=retriever, use_openai=use_openai
            )

            # Load personas
            personas = {}
            sample_personas = create_sample_personas()
            for i, persona in enumerate(sample_personas):
                personas[f"persona_{i+1}"] = persona

            # Initialize evaluator
            evaluator = EmpathyEvaluator()

            return rag_pipeline, personas, evaluator

        except Exception as e:
            st.error(f"Failed to initialize components: {e}")
            return None, None, None


def initialize_session_state():
    """Initialize session state variables."""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "current_persona" not in st.session_state:
        st.session_state.current_persona = None

    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()

    if "caregiver_responses" not in st.session_state:
        st.session_state.caregiver_responses = []

    if "evaluation_history" not in st.session_state:
        st.session_state.evaluation_history = []


def display_persona_card(persona: DementiaPersona, persona_id: str):
    """Display a persona information card."""
    st.markdown(
        f"""
    <div class="persona-card">
        <h3>🎭 {persona.name}</h3>
        <p><strong>Age:</strong> {persona.age}</p>
        <p><strong>Dementia Stage:</strong> {persona.stage.value.title()}</p>
        <p><strong>Current Mood:</strong> {persona.current_mood.value.title()}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if persona.background:
        st.write("**Background:**")
        for key, value in persona.background.items():
            st.write(f"• **{key.title()}:** {value}")


def display_chat_message(message: str, is_user: bool, mood: Optional[str] = None):
    """Display a chat message with appropriate styling."""
    if is_user:
        st.markdown(
            f"""
        <div class="chat-message user-message">
            <strong>🧑‍⚕️ You:</strong> {message}
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        mood_emoji = {
            "calm": "😌",
            "confused": "😕",
            "agitated": "😤",
            "anxious": "😰",
            "depressed": "😔",
            "content": "😊",
            "frustrated": "😤",
        }.get(mood, "😐")

        persona_name = (
            st.session_state.current_persona.name
            if st.session_state.current_persona
            else "Patient"
        )
        st.markdown(
            f"""
        <div class="chat-message bot-message">
            <strong>{mood_emoji} {persona_name}:</strong> {message}
            {f'<br><small>💭 Mood: {mood}</small>' if mood else ''}
        </div>
        """,
            unsafe_allow_html=True,
        )


def display_empathy_scores(evaluation: Dict):
    """Display empathy evaluation scores with visualizations."""
    overall_score = evaluation["overall_score"]

    # Overall score display
    if overall_score >= 0.8:
        score_class = "score-excellent"
        score_text = "Excellent Empathy! 🌟"
    elif overall_score >= 0.6:
        score_class = "score-good"
        score_text = "Good Empathy 👍"
    else:
        score_class = "score-needs-improvement"
        score_text = "Needs Improvement 📚"

    st.markdown(
        f"""
    <div class="empathy-score {score_class}">
        {score_text}<br>
        Overall Score: {overall_score:.2f}/1.0
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Detailed scores chart
    if "detailed_scores" in evaluation:
        scores_df = pd.DataFrame(
            [
                {"Category": k.replace("_", " ").title(), "Score": v}
                for k, v in evaluation["detailed_scores"].items()
            ]
        )

        fig = px.bar(
            scores_df,
            x="Score",
            y="Category",
            orientation="h",
            title="Detailed Empathy Scores",
            color="Score",
            color_continuous_scale="RdYlGn",
            range_color=[0, 1],
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Feedback sections
    col1, col2 = st.columns(2)

    with col1:
        if evaluation.get("strengths"):
            st.success("**✅ Strengths:**")
            for strength in evaluation["strengths"]:
                st.write(f"• {strength}")

    with col2:
        if evaluation.get("improvements"):
            st.warning("**🎯 Areas for Improvement:**")
            for improvement in evaluation["improvements"]:
                st.write(f"• {improvement}")

    if evaluation.get("feedback"):
        st.info("**💡 Specific Feedback:**")
        for feedback in evaluation["feedback"]:
            st.write(f"• {feedback}")


def main():
    """Main Streamlit application."""
    st.title("🧠 Dementia Simulation Chatbot")
    st.markdown("Practice empathetic communication with dementia patients")

    # Initialize session state
    initialize_session_state()

    # Initialize components
    rag_pipeline, personas, evaluator = initialize_components()

    if not all([rag_pipeline, personas, evaluator]):
        st.error(
            "Failed to initialize application components. Please check your setup."
        )
        return

    # Sidebar for persona selection and help
    with st.sidebar:
        st.header("🎛️ Controls")

        # Persona selection
        st.subheader("Select Persona")
        persona_options = {
            persona_id: f"{persona.name} ({persona.stage.value})"
            for persona_id, persona in personas.items()
        }

        selected_persona_id = st.selectbox(
            "Choose a persona to chat with:",
            options=list(persona_options.keys()),
            format_func=lambda x: persona_options[x],
            key="persona_selector",
        )

        if selected_persona_id:
            st.session_state.current_persona = personas[selected_persona_id]

        # Session controls
        st.subheader("Session Controls")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.conversation_history = []
                st.session_state.caregiver_responses = []
                st.session_state.session_start = datetime.now()
                st.rerun()

        with col2:
            if st.button("📊 Evaluate", use_container_width=True):
                if st.session_state.caregiver_responses:
                    with st.spinner("Evaluating..."):
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            evaluation = loop.run_until_complete(
                                evaluator.evaluate_conversation(
                                    conversation_history=st.session_state.conversation_history,
                                    caregiver_responses=st.session_state.caregiver_responses,
                                )
                            )
                            loop.close()

                            st.session_state.evaluation_history.append(
                                {"timestamp": datetime.now(), "evaluation": evaluation}
                            )
                            st.success("✅ Evaluation complete!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Start a conversation first!")

        # Show tips based on dementia stage
        if st.session_state.current_persona:
            st.markdown("---")
            st.subheader("💡 Quick Tips")
            stage = st.session_state.current_persona.stage
            if stage == DementiaStage.MILD:
                st.info(
                    "**Mild Stage:** Be patient with memory lapses, "
                    "validate feelings, offer gentle reminders."
                )
            elif stage == DementiaStage.MODERATE:
                st.warning(
                    "**Moderate Stage:** Speak slowly and clearly, "
                    "avoid arguments, use validation therapy."
                )
            else:
                st.error(
                    "**Severe Stage:** Use simple sentences, focus on "
                    "emotions not facts, provide constant reassurance."
                )

        # Help section
        with st.expander("ℹ️ Help & Guidelines"):
            st.markdown("""
            ### 🎯 Purpose
            Practice empathetic communication with dementia patients.

            ### 💡 Key Principles
            - Validate feelings instead of correcting facts
            - Use simple, clear language
            - Be patient with repetition
            - Avoid arguments or confrontation
            - Focus on emotions, not accuracy

            ### 📊 Evaluation Metrics
            - Validation & Emotional Support
            - Respect & Dignity
            - Patience & Communication Clarity
            - Non-confrontational approach
            """)

    # Two-panel layout: Chat on left, Monitoring on right
    left_col, right_col = st.columns([2, 1])

    # Left Panel - Chat Interface
    with left_col:
        st.header("💬 Chat")

        # Display current persona info
        if st.session_state.current_persona:
            persona = st.session_state.current_persona
            st.markdown(
                f"**Chatting with:** {persona.name} ({persona.stage.value} stage) - "
                f"Mood: {persona.current_mood.value.title()}"
            )

        # Display conversation history in a container with fixed height
        chat_container = st.container(height=400)
        with chat_container:
            if not st.session_state.conversation_history:
                st.info("👋 Start a conversation by typing a message below!")
            else:
                for message in st.session_state.conversation_history:
                    is_user = message["speaker"] == "caregiver"
                    mood = message.get("mood") if not is_user else None
                    display_chat_message(message["message"], is_user, mood)

        # Chat input at bottom
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Your message:",
                placeholder="Type your message here...",
                height=100,
                key="chat_input",
            )
            send_button = st.form_submit_button(
                "Send Message 📤", use_container_width=True
            )

        if send_button and user_input and st.session_state.current_persona:
            # Show thinking indicator
            with st.spinner(f"{st.session_state.current_persona.name} is thinking..."):
                try:
                    # Generate response
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        rag_pipeline.generate_response(
                            user_input=user_input,
                            persona=st.session_state.current_persona,
                            conversation_history=st.session_state.conversation_history,
                        )
                    )
                    loop.close()

                    # Add messages to history
                    st.session_state.conversation_history.append(
                        {
                            "speaker": "caregiver",
                            "message": user_input,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    st.session_state.conversation_history.append(
                        {
                            "speaker": "patient",
                            "message": response.response_text,
                            "timestamp": datetime.now().isoformat(),
                            "mood": response.persona_mood,
                        }
                    )

                    st.session_state.caregiver_responses.append(user_input)
                    st.rerun()

                except Exception as e:
                    st.error(f"Error generating response: {e}")
        elif send_button and not st.session_state.current_persona:
            st.warning("Please select a persona from the sidebar first!")

    # Right Panel - Monitoring
    with right_col:
        st.header("📊 Monitoring Panel")

        # Session Stats
        st.subheader("📈 Session Stats")
        session_duration = datetime.now() - st.session_state.session_start
        st.metric(
            "Duration",
            f"{session_duration.seconds // 60}m {session_duration.seconds % 60}s",
        )
        st.metric("Messages", len(st.session_state.conversation_history))
        st.metric("Your Responses", len(st.session_state.caregiver_responses))

        st.markdown("---")

        # Mood Tracker - show current persona mood
        st.subheader("😊 Mood Tracker")
        if st.session_state.current_persona:
            persona = st.session_state.current_persona
            mood_emoji = {
                "calm": "😌",
                "confused": "😕",
                "agitated": "😤",
                "anxious": "😰",
                "depressed": "😔",
                "content": "😊",
                "frustrated": "😤",
            }.get(persona.current_mood.value, "😐")

            st.markdown(
                f"<div style='text-align: center; font-size: 3em;'>{mood_emoji}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align: center; font-size: 1.2em;'>"
                f"{persona.current_mood.value.title()}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("Select a persona to track mood")

        st.markdown("---")

        # Caregiver Performance - Latest Evaluation
        st.subheader("👩‍⚕️ Your Performance")

        if st.session_state.evaluation_history:
            latest_eval = st.session_state.evaluation_history[-1]["evaluation"]
            overall_score = latest_eval["overall_score"]

            # Overall score with color coding
            if overall_score >= 0.8:
                score_color = "#28a745"  # green
                score_label = "Excellent"
            elif overall_score >= 0.6:
                score_color = "#ffc107"  # yellow
                score_label = "Good"
            else:
                score_color = "#dc3545"  # red
                score_label = "Needs Work"

            st.markdown(
                f"""
                <div style='text-align: center; padding: 20px;
                            background-color: {score_color};
                            color: white; border-radius: 10px;
                            margin: 10px 0;'>
                    <h2>{score_label}</h2>
                    <h1>{overall_score:.2f}</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Detailed scores as progress bars
            if "detailed_scores" in latest_eval:
                for category, score in latest_eval["detailed_scores"].items():
                    st.write(f"**{category.replace('_', ' ').title()}**")
                    st.progress(score)

            # Show latest feedback
            if latest_eval.get("strengths"):
                with st.expander("✅ Strengths", expanded=False):
                    for strength in latest_eval["strengths"][:3]:
                        st.write(f"• {strength}")

            if latest_eval.get("improvements"):
                with st.expander("🎯 Improvements", expanded=False):
                    for improvement in latest_eval["improvements"][:3]:
                        st.write(f"• {improvement}")

        else:
            st.info("Click 'Evaluate' to see your performance scores!")

        # Progress chart
        if len(st.session_state.evaluation_history) > 1:
            st.markdown("---")
            st.subheader("📈 Progress")

            eval_data = []
            for i, eval_entry in enumerate(st.session_state.evaluation_history):
                eval_data.append(
                    {
                        "Eval #": i + 1,
                        "Score": eval_entry["evaluation"]["overall_score"],
                    }
                )

            progress_df = pd.DataFrame(eval_data)
            fig = px.line(
                progress_df,
                x="Eval #",
                y="Score",
                markers=True,
                line_shape="spline",
            )
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                yaxis=dict(range=[0, 1]),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
