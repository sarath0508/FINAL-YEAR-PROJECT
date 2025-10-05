from __future__ import annotations

from typing import Tuple


def pick_avatar_from_sentiment(sentiment_label: str) -> Tuple[str, str]:
    label = (sentiment_label or "neutral").lower()
    if "neg" in label or "sad" in label or "fear" in label:
        return "😢", "sad"
    if "pos" in label or "joy" in label or "happy" in label:
        return "😊", "positive"
    if "ang" in label:
        return "😠", "angry"
    return "🤔", "neutral"
