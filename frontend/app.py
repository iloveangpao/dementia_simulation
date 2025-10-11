import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict

# Set page config for wide layout
st.set_page_config(
    page_title="Dementia Simulation Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mock FastAPI endpoints (replace with actual endpoints when backend is ready)
FASTAPI_BASE_URL = "http://localhost:8000"

def get_chat_response(message: str) -> str:
    """Get chat response from FastAPI endpoint"""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/chat",
            json={"message": message},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return "I'm having trouble connecting right now. Please try again."
    except requests.exceptions.RequestException:
        # Fallback to mock response if API is not available
        responses = [
            "I understand you're feeling that way. Can you tell me more?",
            "That sounds challenging. How are you coping today?",
            "Thank you for sharing. What would help you feel better?",
            "I'm here to listen. Take your time.",
            "How has your day been so far?"
        ]
        import random
        return random.choice(responses)

def update_mood_score(mood_score: int) -> bool:
    """Update mood score via FastAPI endpoint"""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/mood",
            json={"mood_score": mood_score},
            timeout=5
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return True  # Assume success for fallback

def get_caregiver_scores() -> Dict:
    """Get caregiver feedback scores from FastAPI endpoint"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/api/caregiver-scores", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.exceptions.RequestException()
    except requests.exceptions.RequestException:
        # Fallback to mock data if API is not available
        return {
            "empathy_score": 8.5,
            "communication_score": 7.8,
            "patience_score": 9.2,
            "overall_score": 8.5,
            "last_updated": "2024-01-15 14:30:00"
        }

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'mood_score' not in st.session_state:
    st.session_state.mood_score = 5
if 'caregiver_scores' not in st.session_state:
    st.session_state.caregiver_scores = get_caregiver_scores()

# Main title
st.title("🧠 Dementia Simulation Platform")

# Create two columns for the main layout
left_col, right_col = st.columns([2, 1])

# Left Panel - Chat Interface
with left_col:
    st.header("💬 Chat Interface")
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for i, chat in enumerate(st.session_state.chat_history):
            if chat['type'] == 'user':
                st.markdown(
                    f"""
                    <div style="text-align: right; margin: 10px 0;">
                        <div style="background-color: #0066cc; color: white; padding: 10px; 
                                   border-radius: 20px; display: inline-block; max-width: 70%;">
                            {chat['message']}
                        </div>
                        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                            {chat['timestamp']}
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:  # assistant
                st.markdown(
                    f"""
                    <div style="text-align: left; margin: 10px 0;">
                        <div style="background-color: #f0f0f0; color: #333; padding: 10px; 
                                   border-radius: 20px; display: inline-block; max-width: 70%;">
                            {chat['message']}
                        </div>
                        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                            {chat['timestamp']}
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message here...", placeholder="How are you feeling today?")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            # Add user message to chat history
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({
                'type': 'user',
                'message': user_input,
                'timestamp': timestamp
            })
            
            # Get response from FastAPI endpoint
            response = get_chat_response(user_input)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                'type': 'assistant',
                'message': response,
                'timestamp': timestamp
            })
            
            # Rerun to update the chat display
            st.rerun()

# Right Panel - Mood Tracker and Caregiver Feedback
with right_col:
    st.header("📊 Monitoring Panel")
    
    # Mood Tracker Section
    st.subheader("😊 Mood Tracker")
    
    mood_score = st.slider(
        "How are you feeling? (1=Very Sad, 10=Very Happy)",
        min_value=1,
        max_value=10,
        value=st.session_state.mood_score,
        key="mood_slider"
    )
    
    # Update mood if changed
    if mood_score != st.session_state.mood_score:
        st.session_state.mood_score = mood_score
        update_mood_score(mood_score)  # Call FastAPI endpoint
        st.success(f"Mood updated to {mood_score}/10")
    
    # Mood visualization
    mood_emoji = ["😢", "😔", "😐", "🙂", "😊"][min(4, max(0, (mood_score - 1) // 2))]
    st.markdown(f"<div style='text-align: center; font-size: 3em;'>{mood_emoji}</div>", 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Caregiver Feedback Scores Section
    st.subheader("👩‍⚕️ Caregiver Performance")
    
    scores = st.session_state.caregiver_scores
    
    # Display scores with progress bars
    st.metric("Empathy Score", f"{scores['empathy_score']}/10")
    st.progress(scores['empathy_score'] / 10)
    
    st.metric("Communication Score", f"{scores['communication_score']}/10")
    st.progress(scores['communication_score'] / 10)
    
    st.metric("Patience Score", f"{scores['patience_score']}/10")
    st.progress(scores['patience_score'] / 10)
    
    st.metric("Overall Score", f"{scores['overall_score']}/10")
    st.progress(scores['overall_score'] / 10)
    
    st.caption(f"Last updated: {scores['last_updated']}")
    
    # Refresh scores button
    if st.button("🔄 Refresh Scores"):
        st.session_state.caregiver_scores = get_caregiver_scores()
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        Dementia Simulation Platform - Connecting to FastAPI endpoints at {FASTAPI_BASE_URL}
    </div>
    """.format(FASTAPI_BASE_URL=FASTAPI_BASE_URL), 
    unsafe_allow_html=True
)