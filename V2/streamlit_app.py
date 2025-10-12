import streamlit as st
from app.nlp import NLP
from app.avatars import render_dot_avatar, render_emotional_indicator
import time

# Page configuration with beautiful theme
st.set_page_config(
    page_title="Mindful Companion - AI Emotional Support",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .chat-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 20%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .chat-bot {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 20% 8px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 12px;
    }
    .stButton button {
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
    }
    .crisis-alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
        text-align: center;
    }
    .support-box {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">Mindful Companion</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered emotional support companion with deep empathy and understanding</p>', unsafe_allow_html=True)

# Initialize NLP engine
@st.cache_resource
def load_nlp():
    return NLP()

nlp = load_nlp()

# Session state initialization
if "chat" not in st.session_state:
    st.session_state.chat = []
if "user_emotional_state" not in st.session_state:
    st.session_state.user_emotional_state = {
        'dominant_emotion': 'neutral',
        'emotion_scores': {},
        'crisis_level': 'low',
        'confidence': 0
    }

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Your Conversation")
    
    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user"><strong>You:</strong> {msg["text"]}</div>', unsafe_allow_html=True)
            else:
                emotion = msg.get('emotion', 'neutral')
                emoji = {'joy': '😊', 'sadness': '😢', 'anger': '😠', 'fear': '😨', 'surprise': '😲', 'neutral': '🤗'}.get(emotion, '🤗')
                st.markdown(f'<div class="chat-bot"><strong>{emoji} Mindful Companion:</strong> {msg["text"]}</div>', unsafe_allow_html=True)

    # User input
    st.markdown("### 💭 Share Your Feelings")
    user_input = st.text_area(
        "What's on your mind? Share your thoughts and feelings...",
        placeholder="I'm feeling... because...\n\nExamples:\n• 'I feel anxious about my upcoming presentation'\n• 'I'm happy because I accomplished something meaningful'\n• 'I feel overwhelmed with work and need support'",
        height=120,
        key="user_input",
        label_visibility="collapsed"
    )

    # Buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        send_btn = st.button("✨ Send Message", use_container_width=True, type="primary")
    with col_btn2:
        clear_btn = st.button("🔄 Clear Chat", use_container_width=True)
    with col_btn3:
        if st.button("🆘 Emergency Resources", use_container_width=True):
            st.session_state.show_resources = True

with col2:
    st.markdown("### 🎭 Emotional Avatar")
    
    # Avatar display
    if st.session_state.user_emotional_state:
        render_dot_avatar(st.session_state.user_emotional_state)
        render_emotional_indicator(st.session_state.user_emotional_state)
    
    st.markdown("---")
    st.markdown("### 📊 Emotional Insights")
    
    if st.session_state.user_emotional_state:
        emotion_scores = st.session_state.user_emotional_state.get('emotion_scores', {})
        if emotion_scores:
            # Display emotion probabilities
            for emotion, score in sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True):
                if score > 0.1:  # Only show significant emotions
                    emoji = {'joy': '😊', 'sadness': '😢', 'anger': '😠', 'fear': '😨', 'surprise': '😲', 'disgust': '😖', 'neutral': '😐'}.get(emotion, '😐')
                    st.progress(score, text=f"{emoji} {emotion.title()}: {score:.0%}")

    st.markdown("---")
    st.markdown("### 💡 Conversation Tips")
    st.info("""
    - **Be specific** about what you're feeling and why
    - **Share openly** - this is a safe, non-judgmental space
    - **Take your time** - there's no rush to respond
    - **Notice patterns** in your emotional responses
    - **Remember** - your feelings are always valid
    """)

# Handle button actions
if clear_btn:
    st.session_state.chat = []
    st.session_state.user_emotional_state = {
        'dominant_emotion': 'neutral',
        'emotion_scores': {},
        'crisis_level': 'low',
        'confidence': 0
    }
    st.rerun()

if send_btn and user_input.strip():
    text = user_input.strip()
    
    # Add user message to chat
    st.session_state.chat.append({"role": "user", "text": text})
    
    # Analyze sentiment and generate response
    with st.spinner("🧠 Connecting with deep understanding..."):
        sentiment_info = nlp.analyze_sentiment(text)
        st.session_state.user_emotional_state = sentiment_info
        
        # Generate empathetic response
        reply = nlp.generate_reply(text, sentiment_info)
    
    # Calculate speaking intensity
    word_count = len(text.split())
    speaking_intensity = min(1.0, 0.2 + word_count / 50)
    
    # Add bot response to chat
    st.session_state.chat.append({
        "role": "bot", 
        "text": reply,
        "emotion": sentiment_info['dominant_emotion']
    })
    
    # Show emotional insights
    emotion_emoji = {'joy': '😊', 'sadness': '😢', 'anger': '😠', 'fear': '😨', 'surprise': '😲', 'neutral': '🤗'}.get(
        sentiment_info['dominant_emotion'].lower(), '🤗'
    )
    
    st.success(f"{emotion_emoji} **Emotional Insight**: I sense you're feeling **{sentiment_info['dominant_emotion'].title()}** (confidence: {sentiment_info['confidence']:.0%})")
    
    # Crisis alerts
    if sentiment_info['crisis_level'] == 'high':
        st.markdown("""
        <div class="crisis-alert">
            <h3>🚨 Immediate Support Needed</h3>
            <p>Your safety is the most important thing. Please contact professional help immediately:</p>
            <p><strong>988</strong> • <strong>911</strong> • Text <strong>HOME</strong> to <strong>741741</strong></p>
        </div>
        """, unsafe_allow_html=True)
    elif sentiment_info['crisis_level'] == 'medium':
        st.warning("""
        ⚠️ **Additional Support Recommended**
        Consider reaching out to a mental health professional for comprehensive support.
        You deserve care from trained experts during difficult times.
        """)
    
    st.rerun()

# Emergency resources section
if st.session_state.get('show_resources', False):
    st.markdown("---")
    st.markdown("### 🆘 Crisis & Support Resources")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.markdown("""
        <div class="support-box">
            <h4>🆘 Immediate Crisis Support</h4>
            <p><strong>National Suicide Prevention Lifeline</strong><br>988 or 1-800-273-8255</p>
            <p><strong>Crisis Text Line</strong><br>Text HOME to 741741</p>
            <p><strong>Emergency Services</strong><br>911 or your local emergency number</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_res2:
        st.markdown("""
        <div class="support-box">
            <h4>💙 Ongoing Support</h4>
            <p><strong>The Trevor Project</strong><br>1-866-488-7386 (LGBTQ+)</p>
            <p><strong>Veterans Crisis Line</strong><br>1-800-273-8255, press 1</p>
            <p><strong>SAMHSA Helpline</strong><br>1-800-662-4357</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>Mindful Companion</strong> - Your AI emotional support partner</p>
    <p><small>Remember: This AI provides emotional support but is not a replacement for professional mental health care. 
    In crisis situations, please contact qualified professionals immediately.</small></p>
</div>
""", unsafe_allow_html=True)