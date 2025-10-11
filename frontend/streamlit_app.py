"""
Streamlit web interface for the dementia simulation chatbot.

This module provides a user-friendly web interface for practicing
empathetic communication with dementia patients.
"""

import streamlit as st
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from dementia_simulation.persona.models import DementiaPersona, DementiaStage, create_sample_personas
    from dementia_simulation.rag.pipeline import DementiaRAGPipeline
    from dementia_simulation.retriever.faiss_retriever import FAISSRetriever, initialize_retriever_with_knowledge_base
    from dementia_simulation.evaluator.empathy_evaluator import EmpathyEvaluator
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="Dementia Simulation Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
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
""", unsafe_allow_html=True)


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
                retriever=retriever,
                use_openai=use_openai
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
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_persona' not in st.session_state:
        st.session_state.current_persona = None
    
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    
    if 'caregiver_responses' not in st.session_state:
        st.session_state.caregiver_responses = []
    
    if 'evaluation_history' not in st.session_state:
        st.session_state.evaluation_history = []


def display_persona_card(persona: DementiaPersona, persona_id: str):
    """Display a persona information card."""
    st.markdown(f"""
    <div class="persona-card">
        <h3>🎭 {persona.name}</h3>
        <p><strong>Age:</strong> {persona.age}</p>
        <p><strong>Dementia Stage:</strong> {persona.stage.value.title()}</p>
        <p><strong>Current Mood:</strong> {persona.current_mood.value.title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if persona.background:
        st.write("**Background:**")
        for key, value in persona.background.items():
            st.write(f"• **{key.title()}:** {value}")


def display_chat_message(message: str, is_user: bool, mood: Optional[str] = None):
    """Display a chat message with appropriate styling."""
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>🧑‍⚕️ You:</strong> {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        mood_emoji = {
            'calm': '😌',
            'confused': '😕',
            'agitated': '😤',
            'anxious': '😰',
            'depressed': '😔',
            'content': '😊',
            'frustrated': '😤'
        }.get(mood, '😐')
        
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>{mood_emoji} {st.session_state.current_persona.name if st.session_state.current_persona else 'Patient'}:</strong> {message}
            {f'<br><small>💭 Mood: {mood}</small>' if mood else ''}
        </div>
        """, unsafe_allow_html=True)


def display_empathy_scores(evaluation: Dict):
    """Display empathy evaluation scores with visualizations."""
    overall_score = evaluation['overall_score']
    
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
    
    st.markdown(f"""
    <div class="empathy-score {score_class}">
        {score_text}<br>
        Overall Score: {overall_score:.2f}/1.0
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed scores chart
    if 'detailed_scores' in evaluation:
        scores_df = pd.DataFrame([
            {"Category": k.replace('_', ' ').title(), "Score": v}
            for k, v in evaluation['detailed_scores'].items()
        ])
        
        fig = px.bar(
            scores_df, 
            x='Score', 
            y='Category',
            orientation='h',
            title="Detailed Empathy Scores",
            color='Score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 1]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Feedback sections
    col1, col2 = st.columns(2)
    
    with col1:
        if evaluation.get('strengths'):
            st.success("**✅ Strengths:**")
            for strength in evaluation['strengths']:
                st.write(f"• {strength}")
    
    with col2:
        if evaluation.get('improvements'):
            st.warning("**🎯 Areas for Improvement:**")
            for improvement in evaluation['improvements']:
                st.write(f"• {improvement}")
    
    if evaluation.get('feedback'):
        st.info("**💡 Specific Feedback:**")
        for feedback in evaluation['feedback']:
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
        st.error("Failed to initialize application components. Please check your setup.")
        return
    
    # Sidebar
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
            key="persona_selector"
        )
        
        if selected_persona_id:
            st.session_state.current_persona = personas[selected_persona_id]
        
        # Session controls
        st.subheader("Session Controls")
        
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            st.session_state.caregiver_responses = []
            st.session_state.session_start = datetime.now()
            st.rerun()
        
        if st.button("📊 Evaluate Empathy"):
            if st.session_state.caregiver_responses:
                with st.spinner("Evaluating your empathy..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        evaluation = loop.run_until_complete(
                            evaluator.evaluate_conversation(
                                conversation_history=st.session_state.conversation_history,
                                caregiver_responses=st.session_state.caregiver_responses
                            )
                        )
                        loop.close()
                        
                        st.session_state.evaluation_history.append({
                            'timestamp': datetime.now(),
                            'evaluation': evaluation
                        })
                        
                        # Switch to evaluation tab
                        st.session_state.tab_selection = "Evaluation"
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error evaluating empathy: {e}")
            else:
                st.warning("No conversation to evaluate yet.")
        
        # Session stats
        st.subheader("📈 Session Stats")
        session_duration = datetime.now() - st.session_state.session_start
        st.metric("Session Duration", f"{session_duration.seconds // 60}m {session_duration.seconds % 60}s")
        st.metric("Messages Exchanged", len(st.session_state.conversation_history))
        st.metric("Your Responses", len(st.session_state.caregiver_responses))
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Evaluation", "ℹ️ Help"])
    
    with tab1:
        # Display current persona info
        if st.session_state.current_persona:
            st.subheader(f"Current Persona: {st.session_state.current_persona.name}")
            display_persona_card(st.session_state.current_persona, selected_persona_id)
            
            # Tips based on dementia stage
            stage = st.session_state.current_persona.stage
            if stage == DementiaStage.MILD:
                st.info("💡 **Tips for Mild Dementia:** Be patient with memory lapses, validate feelings, offer gentle reminders.")
            elif stage == DementiaStage.MODERATE:
                st.warning("💡 **Tips for Moderate Dementia:** Speak slowly and clearly, avoid arguments, use validation therapy, be prepared for repetition.")
            else:
                st.error("💡 **Tips for Severe Dementia:** Use simple sentences, focus on emotions not facts, provide constant reassurance, be very patient.")
        
        # Chat interface
        st.subheader("💬 Conversation")
        
        # Display conversation history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.conversation_history:
                is_user = message['speaker'] == 'caregiver'
                mood = message.get('mood') if not is_user else None
                display_chat_message(message['message'], is_user, mood)
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_input(
                    "Your message:",
                    placeholder="Type your message here...",
                    key="chat_input"
                )
            
            with col2:
                send_button = st.form_submit_button("Send 📤")
        
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
                            conversation_history=st.session_state.conversation_history
                        )
                    )
                    loop.close()
                    
                    # Add messages to history
                    st.session_state.conversation_history.append({
                        "speaker": "caregiver",
                        "message": user_input,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.session_state.conversation_history.append({
                        "speaker": "patient",
                        "message": response.response_text,
                        "timestamp": datetime.now().isoformat(),
                        "mood": response.persona_mood
                    })
                    
                    st.session_state.caregiver_responses.append(user_input)
                    
                    # Show response info
                    st.success(f"✨ Response generated (Confidence: {response.confidence_score:.2f}, Model: {response.model_used})")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating response: {e}")
    
    with tab2:
        st.subheader("📊 Empathy Evaluation")
        
        if st.session_state.evaluation_history:
            # Show latest evaluation
            latest_eval = st.session_state.evaluation_history[-1]
            st.write(f"**Latest Evaluation** (from {latest_eval['timestamp'].strftime('%H:%M:%S')})")
            display_empathy_scores(latest_eval['evaluation'])
            
            # Historical evaluations
            if len(st.session_state.evaluation_history) > 1:
                st.subheader("📈 Progress Over Time")
                
                # Create progress chart
                eval_data = []
                for i, eval_entry in enumerate(st.session_state.evaluation_history):
                    eval_data.append({
                        'Evaluation': i + 1,
                        'Overall Score': eval_entry['evaluation']['overall_score'],
                        'Timestamp': eval_entry['timestamp']
                    })
                
                progress_df = pd.DataFrame(eval_data)
                
                fig = px.line(
                    progress_df,
                    x='Evaluation',
                    y='Overall Score',
                    title='Empathy Score Progress',
                    markers=True
                )
                fig.update_layout(yaxis=dict(range=[0, 1]))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No evaluations yet. Start a conversation and click 'Evaluate Empathy' to see your scores!")
    
    with tab3:
        st.subheader("ℹ️ How to Use This Application")
        
        st.markdown("""
        ### 🎯 Purpose
        This application helps you practice empathetic communication with people who have dementia.
        Each persona represents a different stage of dementia with unique characteristics and needs.
        
        ### 📋 How to Use
        1. **Select a Persona**: Choose from different dementia stages (mild, moderate, severe)
        2. **Start Chatting**: Practice your communication skills in the Chat tab
        3. **Get Feedback**: Use the "Evaluate Empathy" button to get detailed feedback
        4. **Improve**: Review suggestions and practice more
        
        ### 🧠 Dementia Stages
        - **Mild**: Memory lapses, mostly independent, needs gentle reminders
        - **Moderate**: Significant memory problems, confusion, needs assistance
        - **Severe**: Severe impairment, limited communication, needs constant care
        
        ### 💡 Empathy Tips
        - **Validate feelings** instead of correcting facts
        - **Use simple, clear language**
        - **Be patient with repetition**
        - **Avoid arguments or confrontation**
        - **Focus on emotions, not accuracy**
        - **Provide reassurance and comfort**
        
        ### 🎯 Evaluation Metrics
        The system evaluates your responses on:
        - **Validation**: Acknowledging feelings without correction
        - **Emotional Support**: Providing comfort and reassurance
        - **Respect & Dignity**: Maintaining the person's dignity
        - **Patience**: Handling repetition and confusion gracefully
        - **Communication Clarity**: Using clear, simple language
        - **Non-confrontational**: Avoiding arguments
        """)
        
        st.subheader("🔧 Technical Information")
        
        # System stats
        pipeline_stats = rag_pipeline.get_pipeline_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**AI Pipeline:**")
            st.write(f"• Model: {pipeline_stats.get('model_name', 'Unknown')}")
            st.write(f"• Using OpenAI: {pipeline_stats.get('use_openai', False)}")
            st.write(f"• Model Loaded: {pipeline_stats.get('model_loaded', False)}")
        
        with col2:
            retriever_stats = pipeline_stats.get('retriever_stats', {})
            st.write("**Knowledge Base:**")
            st.write(f"• Documents: {retriever_stats.get('total_documents', 0)}")
            st.write(f"• Embedding Model: {retriever_stats.get('model_name', 'Unknown')}")
            st.write(f"• Index Vectors: {retriever_stats.get('index_total_vectors', 0)}")


if __name__ == "__main__":
    main()