# app/voice.py — offline TTS via pyttsx3 and RMS using soundfile + numpy
import pyttsx3
import tempfile
import soundfile as sf
import numpy as np
import math
import os

class Speech:
    def __init__(self, lang="en"):
        self.lang = lang
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 165)
        self.engine.setProperty("volume", 0.95)
        # voice selection left to OS default

    def synthesize(self, text: str, out_path: str = None) -> str:
        out_path = out_path or tempfile.mktemp(suffix=".wav")
        # pyttsx3 writes to file synchronously
        self.engine.save_to_file(text, out_path)
        self.engine.runAndWait()
        return out_path

    def estimate_speaking_ms(self, text: str) -> int:
        words = max(1, len(text.split()))
        # 150 wpm ~ 400ms per word
        ms = int(words * 400)
        return min(20000, max(600, ms))

    def rms_from_wav(self, wav_path: str, chunk_ms: int = 60):
        data, sr = sf.read(wav_path, always_2d=False)
        if data.ndim > 1:
            data = data.mean(axis=1)
        chunk = int(sr * (chunk_ms/1000.0))
        rms = []
        for i in range(0, len(data), chunk):
            frame = data[i:i+chunk]
            if frame.size == 0:
                break
            rms_val = math.sqrt(np.mean(frame.astype(np.float64)**2))
            rms.append(float(rms_val))
        if rms:
            m = max(rms)
            if m > 0:
                rms = [r/m for r in rms]
        return rms
