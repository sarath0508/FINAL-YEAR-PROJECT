## 🧠 FINAL YEAR PROJECT — Multilingual Mental Health Chatbot (Free-First)

A compassionate, multilingual chatbot prototype for supportive conversations. It responds with empathy, detects crisis keywords, offers brief actionable steps, supports voice input/output, and displays avatar-style emojis to aid low-literacy users.

> Not a medical device. For emergencies, contact your local emergency number immediately.

---

### ✨ Highlights
- **Multilingual**: Understands and replies in the user’s language
- **Empathetic responses**: FLAN-T5 with an empathy-tuned prompt
- **Actionable support plan**: 3–5 gentle, feasible next steps
- **Crisis awareness**: Keyword trigger → show helpline guidance
- **Voice I/O**: Whisper STT, `pyttsx3` TTS (offline, Windows-friendly)
- **Accessible UI**: Emoji/Bitmoji-like avatars via OpenMoji
- **Free-first stack**: Colab, Streamlit, Hugging Face models

---

### 🏗️ Architecture (Free-first)
- **Input**: Text (Streamlit), voice upload (Whisper)
- **NLP**:
  - Sentiment: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
  - Empathy/NLG: `google/flan-t5-base`
  - Optional NLI: `joeddav/xlm-roberta-large-xnli`
- **Decision**: Basic crisis keywords → helpline
- **Output**: Text + emoji avatar; optional TTS with `pyttsx3`
- **Deploy**: Local, Colab, or Hugging Face Spaces (Streamlit)

---

### 📦 Repo Structure
- `app/nlp.py` — sentiment, empathetic reply, support plan
- `app/crisis.py` — crisis keyword detection + helpline
- `app/avatars.py` — emoji avatar mapping
- `app/voice.py` — Whisper STT + `pyttsx3` TTS
- `streamlit_app.py` — Streamlit chatbot UI
- `notebooks/colab_prototype.ipynb` — quick Colab demo

---

### 🚀 Quickstart (Local)
1) Install dependencies
```bash
pip install -r requirements.txt
```
2) Run the app
```bash
streamlit run streamlit_app.py
```
3) Optional: Enable STT/TTS in the sidebar
- STT uses Whisper (CPU ok, first run downloads weights)
- TTS uses `pyttsx3` (offline; Windows uses SAPI5 voices)

Requirements: Python 3.10–3.13, ffmpeg available in PATH (for audio handling)

---

### 🧪 Colab Prototype
Open `notebooks/colab_prototype.ipynb` in Colab and run cells. Or install minimal deps directly in Colab:
```python
!pip install transformers datasets openai-whisper pyttsx3 emoji ffmpeg-python soundfile pydub
```

---

### 🧩 How It Works
- The bot detects a coarse sentiment label and crafts a warm, validating response in the same language.
- It proposes a short support plan (3–5 bullet points) with simple, immediate steps (grounding, self-care, optional social/pro support).
- If high-risk keywords are present, it surfaces a neutral, non-diagnostic helpline prompt.

---

### 🔒 Privacy & Safety
- No PII storage by default. Add an explicit opt‑in before logging any data.
- No medical claims or diagnoses. Crisis prompts suggest contacting local services.
- For production, add locale-aware helplines and human-in-the-loop review.

---

### 🛠️ Tuning & Extensibility
- Adjust tone/length in `NLPModels.generate_empathetic_reply` and `generate_support_plan`.
- Replace models with distilled or quantized variants for offline/rural devices.
- Swap STT with `whisper.cpp` for ultra‑light CPU inference.
- Add multi-country helpline localization in `app/crisis.py`.

---

### 🗺️ Roadmap
- Emotion taxonomy beyond sentiment (multi-label)
- Session memory + safety rails (content filters)
- UI polish (theming, larger emoji avatars, voice recorder)
- Model caching and ONNX/ggml exports for offline

---

### 🙏 Acknowledgements
- Hugging Face models and datasets
- OpenMoji project (`https://openmoji.org`)
- Whisper (OpenAI) and pyttsx3 community

---

### 📄 License
Research prototype. Ensure compliance with local laws and platform policies when deploying.
