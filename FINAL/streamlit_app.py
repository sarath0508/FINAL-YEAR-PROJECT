import os
import tempfile
import streamlit as st

from app.nlp import NLPModels
from app.crisis import detect_crisis, crisis_helpline
from app.avatars import pick_avatar_from_sentiment
from app.voice import Speech

st.set_page_config(page_title="Mental Health Chatbot (Prototype)", page_icon="🧠")

@st.cache_resource
def get_models():
    return NLPModels()

@st.cache_resource
def get_speech():
    return Speech()

st.title("🧠 Multilingual Mental Health Chatbot (Prototype)")

with st.sidebar:
    st.markdown("**Modes**")
    enable_stt = st.toggle("Voice input (Whisper)", value=False)
    enable_tts = st.toggle("Voice output (pyttsx3)", value=False)
    locale = st.selectbox("Locale (for helpline)", ["en", "es", "fr", "hi", "ar", "sw"], index=0)
    st.info("This is a research prototype. Not a medical device.")

models = get_models()
speech = get_speech()

st.write("Type a message in your language. The bot replies empathetically.")

# Low-literacy mode: optional audio upload for STT
user_text = ""
if enable_stt:
    audio_file = st.file_uploader("Upload audio (wav/mp3)", type=["wav", "mp3", "m4a", "ogg"]) 
    if audio_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{audio_file.name}") as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name
        with st.spinner("Transcribing..."):
            try:
                user_text = speech.transcribe(tmp_path)
                st.success("Transcription complete")
            except Exception as e:
                st.error(f"STT failed: {e}")
        os.unlink(tmp_path)

# Text input fallback
user_text = st.text_input("Your message", value=user_text)

if st.button("Send") and user_text.strip():
    with st.spinner("Thinking empathetically..."):
        crisis, hits = detect_crisis(user_text)
        sentiment_label = models.detect_sentiment(user_text)
        avatar, mood = pick_avatar_from_sentiment(sentiment_label)
        reply = models.generate_empathetic_reply(user_text, emotion_hint=sentiment_label)
        plan = models.generate_support_plan(user_text)

    st.markdown(f"{avatar} {reply}")

    if plan:
        st.markdown("**Here are a few gentle next steps you could try:**")
        for item in plan:
            st.markdown(f"- {item}")

    if crisis:
        st.warning("High-risk content detected: " + ", ".join(hits))
        st.info(crisis_helpline(locale))

    if enable_tts:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpw:
                out_path = tmpw.name
            out_wav = speech.synthesize(reply, out_path)
            audio_bytes = open(out_wav, "rb").read()
            st.audio(audio_bytes, format="audio/wav")
            os.unlink(out_wav)
        except Exception as e:
            st.error(f"TTS failed: {e}")

st.caption("Not a medical device. If you're in danger, contact local emergency services.")
st.caption("Models: cardiffnlp/twitter-xlm-roberta-base-sentiment, google/flan-t5-base, joeddav/xlm-roberta-large-xnli. TTS: pyttsx3.")
