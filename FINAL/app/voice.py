from __future__ import annotations

import os
import tempfile
from typing import Optional

import soundfile as sf

try:
    import whisper  # openai-whisper
except Exception:
    whisper = None

try:
    import pyttsx3  # offline TTS, Windows-friendly
except Exception:
    pyttsx3 = None


class Speech:
    def __init__(self) -> None:
        self._whisper_model = None
        self._tts_engine = None

    def load_whisper(self, model_name: str = "small") -> None:
        if whisper is None:
            raise RuntimeError("openai-whisper not installed")
        self._whisper_model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str) -> str:
        if self._whisper_model is None:
            self.load_whisper("small")
        result = self._whisper_model.transcribe(audio_path)
        return result.get("text", "").strip()

    def load_tts(self, rate: Optional[int] = None, voice_id: Optional[str] = None) -> None:
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 not installed")
        self._tts_engine = pyttsx3.init()
        if rate is not None:
            self._tts_engine.setProperty("rate", int(rate))
        if voice_id is not None:
            self._tts_engine.setProperty("voice", voice_id)

    def synthesize(self, text: str, out_wav: str) -> str:
        if self._tts_engine is None:
            self.load_tts()
        os.makedirs(os.path.dirname(out_wav) or ".", exist_ok=True)
        # pyttsx3 can save directly to file via driver
        # Use a temp wav to ensure consistency
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpw:
            tmp_path = tmpw.name
        try:
            self._tts_engine.save_to_file(text, tmp_path)
            self._tts_engine.runAndWait()
            # Validate and rewrite
            data, sr = sf.read(tmp_path)
            sf.write(out_wav, data, sr)
            return out_wav
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
