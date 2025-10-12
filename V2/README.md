Project: Multilingual Empathy Chatbot (dot-matrix avatar speaking)

Steps:
1. Create a new venv (recommended Python 3.12 or 3.13):
   python -m venv venv
   venv\Scripts\activate   # Windows
2. pip install -r requirements.txt
3. streamlit run streamlit_app.py

Notes:
- Uses google/flan-t5-small for responses (fast). If GPU present, torch detects it.
- TTS: offline via pyttsx3 (Windows SAPI5). On Linux, pyttsx3 uses espeak; voice quality differs.
- ASR (whisper) is optional — toggled in UI; whisper can be slow on CPU.
- If you run Python 3.13 and hit audio shims, sitecustomize.py helps. Prefer Python 3.12 for audio stack stability.
- This prototype is NOT clinical. Risk detection is basic (keywords + sentiment). Replace with clinical models before production.
