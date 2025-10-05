from __future__ import annotations

from typing import List, Tuple

HIGH_RISK_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "self harm",
    "self-harm",
    "overdose",
    "can't go on",
    "want to die",
]


def detect_crisis(text: str) -> Tuple[bool, List[str]]:
    lowered = text.lower()
    hits = [kw for kw in HIGH_RISK_KEYWORDS if kw in lowered]
    return (len(hits) > 0, hits)


def crisis_helpline(locale: str = "en") -> str:
    # Minimal non-regional guidance; in production, localize per country
    if locale.startswith("en"):
        return (
            "If you are in immediate danger, call your local emergency number. "
            "You can also contact a crisis hotline: US 988 Suicide & Crisis Lifeline, UK Samaritans 116 123."
        )
    # Fallback
    return (
        "If you are in immediate danger, call your local emergency number. "
        "Please reach out to your nearest crisis hotline for support."
    )
