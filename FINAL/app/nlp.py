import typing as t

from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)


class NLPModels:
    def __init__(self) -> None:
        # Sentiment (multilingual)
        self.sentiment = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
        )
        # Empathy generator (FLAN-T5)
        self.tok = AutoTokenizer.from_pretrained("google/flan-t5-base")
        self.gen_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
        # Optional: NLI for emotion inference or safety checks
        self.nli = pipeline(
            "text-classification",
            model="joeddav/xlm-roberta-large-xnli",
        )

    def detect_sentiment(self, text: str) -> str:
        try:
            result = self.sentiment(text)[0]
            return result.get("label", "neutral")
        except Exception:
            return "neutral"

    def _generate(self, prompt: str, max_new_tokens: int = 160) -> str:
        inputs = self.tok(prompt, return_tensors="pt")
        outputs = self.gen_model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tok.decode(outputs[0], skip_special_tokens=True)

    def generate_empathetic_reply(self, user_text: str, emotion_hint: t.Optional[str] = None) -> str:
        sentiment_label = emotion_hint or self.detect_sentiment(user_text)
        prompt = (
            "You are a compassionate, non-judgmental mental health support bot. "
            "Goals: reflect feelings, validate, normalize, and offer gentle hope. "
            "Avoid medical claims or diagnosis. Keep tone warm, brief, and culturally sensitive.\n\n"
            f"User message (may be multilingual): {user_text}\n"
            f"Detected emotion: {sentiment_label}\n\n"
            "Write a supportive, empathetic response in the same language as the user. "
            "Use simple language and 2-4 sentences."
        )
        return self._generate(prompt, max_new_tokens=140)

    def generate_support_plan(self, user_text: str) -> t.List[str]:
        prompt = (
            "You are a supportive assistant. Create a brief, safe, actionable plan with 3-5 bullet points "
            "to help the user cope right now. Include self-care, grounding, and optional social/pro help. "
            "Avoid medical advice, diagnosis, or unsafe instructions. Keep steps simple and feasible.\n\n"
            f"User message: {user_text}\n\n"
            "Return only bullet points starting with '- '. Keep each under 18 words."
        )
        text = self._generate(prompt, max_new_tokens=160)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        bullets = [l[2:].strip() for l in lines if l.startswith("- ")]
        # Fallback if model returns a paragraph
        if not bullets:
            bullets = [text.strip()[:140]]
        # Cap 5 items
        return bullets[:5]

    def nli_emotion(self, premise: str) -> str:
        # Simple wrapper; could map NLI labels to emotions
        try:
            result = self.nli(premise)[0]
            return result.get("label", "UNKNOWN")
        except Exception:
            return "UNKNOWN"
