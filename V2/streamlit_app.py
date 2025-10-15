import streamlit as st
from app.nlp import CompanionNLP
from app.avatars import render_dot_avatar, render_emotional_indicator
import datetime

# Page configuration
st.set_page_config(
    page_title="Mindful Companion - Your AI Friend",
    page_icon="💫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .companion-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
        font-weight: 700;
    }
    .companion-subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0 10px 15%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        line-height: 1.5;
    }
    .message-companion {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 14px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 15% 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        line-height: 1.5;
        border: 1px solid rgba(255,255,255,0.3);
    }
    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 5px;
    }
    .conversation-stats {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize companion
@st.cache_resource
def load_companion():
    return CompanionNLP()

companion = load_companion()

# Session state initialization
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "emotional_state" not in st.session_state:
    st.session_state.emotional_state = {
        'dominant_emotion': 'neutral',
        'emotion_scores': {},
        'crisis_level': 'low',
        'confidence': 0
    }
if "processing" not in st.session_state:
    st.session_state.processing = False
if "show_stats" not in st.session_state:
    st.session_state.show_stats = False

# Header
st.markdown('<h1 class="companion-header">Mindful Companion</h1>', unsafe_allow_html=True)
st.markdown('<p class="companion-subtitle">Your AI friend who listens, remembers, and cares</p>', unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💫 Your Conversation")
    
    # Conversation display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.conversation:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="message-user">'
                    f'<div><strong>You:</strong> {msg["text"]}</div>'
                    f'<div class="message-time">{msg.get("time", "")}</div>'
                    f'</div>', 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="message-companion">'
                    f'<div><strong>Bot:</strong> {msg["text"]}</div>'
                    f'<div class="message-time">{msg.get("time", "")}</div>'
                    f'</div>', 
                    unsafe_allow_html=True
                )

    # User input
    st.markdown("### 💭 Share what's on your mind")
    
    # Use form to prevent auto-rerun issues
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "What would you like to talk about?",
            placeholder="Hey Bot, I've been thinking about...",
            height=100,
            key="user_input_field",
            label_visibility="collapsed"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn1:
            submit = st.form_submit_button("💫 Send to Bot", use_container_width=True, type="primary")
        with col_btn2:
            # Can't have regular buttons in forms, moved outside
            pass
        with col_btn3:
            pass
    
    # Buttons outside form
    col_act1, col_act2, col_act3 = st.columns([1, 1, 1])
    with col_act1:
        pass  # Submit button is in form
    with col_act2:
        if st.button("🔄 Fresh Start", use_container_width=True):
            st.session_state.conversation = []
            st.session_state.emotional_state = {
                'dominant_emotion': 'neutral',
                'emotion_scores': {},
                'crisis_level': 'low',
                'confidence': 0
            }
            st.rerun()
    with col_act3:
        if st.button("📊 Conversation Stats", use_container_width=True):
            st.session_state.show_stats = not st.session_state.show_stats
            st.rerun()
    
    # Process submission
    if submit and user_input and user_input.strip():
        text = user_input.strip()
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        # Add user message
        st.session_state.conversation.append({
            "role": "user", 
            "text": text,
            "time": current_time
        })
        
        # Generate response immediately
        with st.spinner("💫 Bot is thinking..."):
            try:
                # Analyze sentiment
                sentiment_info = companion.analyze_sentiment(text)
                st.session_state.emotional_state = sentiment_info
                
                # Generate response
                response = companion.generate_companion_response(text, sentiment_info)
                
                # Add bot response
                st.session_state.conversation.append({
                    "role": "companion", 
                    "text": response,
                    "emotion": sentiment_info['dominant_emotion'],
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                
                # Show insight
                emotion_emoji = {
                    'joy': '😊', 'sadness': '😢', 'anger': '😠', 
                    'fear': '😨', 'surprise': '😲', 'neutral': '🤗'
                }.get(sentiment_info['dominant_emotion'].lower(), '🤗')
                
                st.success(f"{emotion_emoji} **Bot noticed**: You seem to be feeling **{sentiment_info['dominant_emotion'].title()}**")
                
                # Crisis warnings
                if sentiment_info['crisis_level'] == 'high':
                    st.error("""
                    🚨 **Immediate Support Needed**
                    Your safety is the most important thing. Please contact:
                    • **988** Suicide Prevention Lifeline
                    • **911** Emergency Services
                    • Text **HOME** to **741741**
                    """)
                elif sentiment_info['crisis_level'] == 'medium':
                    st.warning("""
                    ⚠️ **Additional Support Available**
                    Consider reaching out to a mental health professional for comprehensive support.
                    """)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                # Add fallback response
                st.session_state.conversation.append({
                    "role": "companion",
                    "text": "I'm here with you. Could you tell me more about what's on your mind?",
                    "emotion": "neutral",
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
        
        st.rerun()

with col2:
    st.markdown("### 🎭 Bot's Reactions")
    
    # Avatar
    if st.session_state.emotional_state:
        render_dot_avatar(st.session_state.emotional_state)
        render_emotional_indicator(st.session_state.emotional_state)
    
    st.markdown("---")
    
    # Conversation insights
    st.markdown("### 🧠 Conversation Insights")
    
    if st.session_state.conversation:
        summary = companion.get_conversation_summary()
        st.markdown(f"""
        <div class="conversation-stats">
            <strong>Conversation Depth:</strong><br>
            • {summary['history_length']} exchanges<br>
            • {len(summary['topics_discussed'])} topics<br>
            • Current mood: {summary['current_emotion_trend']}
        </div>
        """, unsafe_allow_html=True)
        
        if summary['topics_discussed']:
            st.markdown("**Topics discussed:**")
            for topic in summary['topics_discussed']:
                st.caption(f"• {topic.replace('_', ' ').title()}")
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("""
    - **Be yourself** - Bot is here to listen
    - **Share feelings** - "I felt..."
    - **Ask questions** - Bot loves conversations
    - **Take your time** - No rush
    """)

# Show stats
if st.session_state.show_stats and st.session_state.conversation:
    st.markdown("---")
    st.markdown("### 📈 Conversation Analytics")
    
    summary = companion.get_conversation_summary()
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("Exchanges", summary['history_length'])
    with col_stat2:
        st.metric("Topics", len(summary['topics_discussed']))
    with col_stat3:
        st.metric("Mood", summary['current_emotion_trend'].title())

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>💫 Mindful Companion</strong> - Your AI friend who genuinely cares</p>
    <p><small>Not a replacement for professional mental health care.</small></p>
</div>
""", unsafe_allow_html=True)