import torch
import re
import random
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Dict, List, Tuple

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class NLP:
    def __init__(self):
        print(f"Loading enhanced empathetic models on {DEVICE}...")
        
        # More accurate emotion detection model
        self.sentiment = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=0 if DEVICE == "cuda" else -1,
            top_k=None
        )
        
        # Use a more capable model for empathetic responses
        print("Loading empathetic dialogue model...")
        model_name = "microsoft/DialoGPT-medium"
        self.dialogue_tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.dialogue_model = AutoModelForCausalLM.from_pretrained(model_name).to(DEVICE)
        self.dialogue_model.eval()
        
        if self.dialogue_tokenizer.pad_token is None:
            self.dialogue_tokenizer.pad_token = self.dialogue_tokenizer.eos_token

        # Comprehensive empathetic response templates
        self.emotion_guided_responses = {
            'joy': [
                "I can feel your happiness shining through! 😊 It's wonderful to hear you're experiencing joy. What specifically is bringing you this positive energy?",
                "That's absolutely fantastic! Celebrating these joyful moments is so important for our wellbeing. I'd love to hear more about what's making you feel this way!",
                "Your happiness is truly uplifting! Thanks for sharing this beautiful moment. Could you tell me more about what's behind these wonderful feelings?"
            ],
            'sadness': [
                "I hear the sadness in your words, and I want you to know I'm here with you in this moment. It takes real strength to share these feelings. Would you like to tell me more about what's weighing on your heart?",
                "I'm truly sorry you're carrying this sadness. It sounds incredibly heavy, and you don't have to carry it alone. I'm here to listen whenever you feel ready to share more.",
                "That sounds profoundly difficult. Thank you for trusting me with these feelings - that's a brave step. Your sadness is valid and important. What's been particularly challenging lately?"
            ],
            'anger': [
                "I can feel the intensity of your frustration, and it's completely understandable. That sounds incredibly challenging to navigate. Would you like to explore what's at the root of these feelings together?",
                "Your anger makes complete sense given what you're describing. These feelings often come from real pain or injustice. I'm here to listen - what would help you feel heard right now?",
                "That sounds genuinely frustrating and difficult. Anger is often a signal that something important needs attention. Let's work through this together - what aspect feels most pressing?"
            ],
            'fear': [
                "I can sense the fear in what you're sharing, and I want you to know I'm here beside you. Fear can feel so overwhelming. Would it help to talk about what specifically feels most concerning?",
                "That sounds truly frightening. It's completely human to feel fear in uncertain situations. Let's break this down together - what feels most manageable to address right now?",
                "I hear the anxiety in your words. You're showing courage by sharing this. What support would feel most helpful as you navigate these fears?"
            ],
            'surprise': [
                "That sounds quite unexpected! Surprises can really shake up our world. How are you processing everything? I'm here to help you make sense of it all.",
                "What a significant revelation! It's completely normal to need time to absorb surprising news. Want to walk through what happened and how you're feeling about it?",
                "That's quite a development! Surprises often bring mixed emotions. I'm here to support you as you navigate this new information."
            ],
            'disgust': [
                "That sounds truly upsetting and disturbing. I understand why you'd feel this way - your reaction makes complete sense. Would you like to talk through what happened?",
                "I can see why that would be deeply unsettling. Your feelings are completely valid given the circumstances. Let's explore what support you need right now.",
                "That does sound very disturbing to experience. I'm here to listen and support you through processing these feelings."
            ],
            'neutral': [
                "Thank you for sharing what's on your mind. I'm here to listen with care and attention - feel free to share whatever feels right for you.",
                "I appreciate you taking this step to connect. How can I best support you in this moment? Your thoughts and feelings are important.",
                "I'm listening with full presence. Sometimes the act of sharing itself can bring clarity. What's been occupying your thoughts recently?"
            ]
        }

        self.crisis_keywords = {
            'suicide': ["kill myself", "end it all", "don't want to live", "suicide", "end my life", "better off dead", "no point living", "want to die"],
            'self_harm': ["hurt myself", "cut myself", "self harm", "self-harm", "bleeding", "pain makes me feel", "self injury"],
            'emergency': ["help me", "emergency", "can't cope", "breaking down", "losing control", "can't take it", "overwhelmed", "panic attack"]
        }

    def analyze_sentiment(self, text: str) -> Dict:
        """Enhanced sentiment analysis with better emotion detection"""
        try:
            emotions = self.sentiment(text)[0]
            dominant_emotion = max(emotions, key=lambda x: x['score'])
            crisis_level = self._detect_crisis_level(text)
            
            return {
                'dominant_emotion': dominant_emotion['label'],
                'emotion_scores': {e['label']: e['score'] for e in emotions},
                'crisis_level': crisis_level,
                'confidence': dominant_emotion['score']
            }
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {
                'dominant_emotion': 'neutral',
                'emotion_scores': {'neutral': 1.0},
                'crisis_level': 'low',
                'confidence': 1.0
            }

    def _detect_crisis_level(self, text: str) -> str:
        """Enhanced crisis detection"""
        text_lower = text.lower()
        
        for level, keywords in self.crisis_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if level in ['suicide', 'self_harm']:
                    return 'high'
                elif level == 'emergency':
                    return 'medium'
        
        return 'low'

    def generate_reply(self, text: str, sentiment_info: Dict) -> str:
        """Generate deeply empathetic responses"""
        
        crisis_level = sentiment_info['crisis_level']
        dominant_emotion = sentiment_info['dominant_emotion']
        
        # Handle crisis situations
        if crisis_level == 'high':
            return self._get_crisis_response()
        elif crisis_level == 'medium':
            return self._get_support_response()

        try:
            # Use enhanced template as foundation
            base_response = self._get_emotional_template(dominant_emotion)
            
            # Create more sophisticated prompt
            prompt = self._create_empathetic_prompt(text, dominant_emotion, base_response)
            
            inputs = self.dialogue_tokenizer.encode(
                prompt, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True
            ).to(DEVICE)
            
            with torch.inference_mode():
                outputs = self.dialogue_model.generate(
                    inputs,
                    max_new_tokens=120,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40,
                    do_sample=True,
                    pad_token_id=self.dialogue_tokenizer.eos_token_id,
                    repetition_penalty=1.15,
                    no_repeat_ngram_size=2
                )
            
            generated_text = self.dialogue_tokenizer.decode(outputs[0], skip_special_tokens=True)
            reply = self._extract_response(generated_text, prompt, base_response)
            
            # Ensure quality and empathy
            if not self._validate_empathy(reply):
                reply = base_response
                
        except Exception as e:
            print(f"Response generation error: {e}")
            reply = self._get_emotional_template(dominant_emotion)
        
        return reply

    def _create_empathetic_prompt(self, user_text: str, emotion: str, template: str) -> str:
        """Create sophisticated prompt for empathetic responses"""
        return f"""<|im_start|>system
You are a deeply empathetic mental wellness assistant. Provide emotional support that is:
- Validating and non-judgmental
- Specifically tailored to {emotion}
- Encourages sharing without pressure
- Offers genuine understanding
- Uses warm, natural language

User is feeling: {emotion}
Their message: "{user_text}"

Example of good empathetic response: "{template}"

Respond with genuine care and understanding:<|im_end|>
<|im_start|>user
{user_text}<|im_end|>
<|im_start|>assistant
"""

    def _get_emotional_template(self, emotion: str) -> str:
        """Get appropriate emotional template"""
        templates = self.emotion_guided_responses.get(
            emotion.lower(), 
            self.emotion_guided_responses['neutral']
        )
        return random.choice(templates)

    def _extract_response(self, generated_text: str, prompt: str, fallback: str) -> str:
        """Extract and clean the generated response"""
        try:
            # Extract assistant response
            if "<|im_start|>assistant" in generated_text:
                reply = generated_text.split("<|im_start|>assistant")[-1]
                if "<|im_end|>" in reply:
                    reply = reply.split("<|im_end|>")[0]
            else:
                reply = generated_text.replace(prompt, "").strip()
            
            # Clean response
            reply = re.sub(r'<\|.*?\|>', '', reply)
            reply = re.sub(r'\[.*?\]', '', reply)
            reply = re.sub(r'^[\s\W]+', '', reply)
            
            # Ensure proper formatting
            reply = reply.strip()
            if not reply.endswith(('.', '!', '?')) and len(reply) > 10:
                reply += '.'
            
            # Validate response
            if len(reply.split()) < 5 or len(reply) > 200:
                return fallback
                
            return reply
            
        except Exception:
            return fallback

    def _validate_empathy(self, response: str) -> bool:
        """Validate that response shows genuine empathy"""
        empathetic_phrases = [
            'understand', 'hear you', 'sorry', 'support', 'here for you',
            'valid', 'makes sense', 'feel', 'care', 'listening', 'with you',
            'difficult', 'challenging', 'hard', 'appreciate you sharing'
        ]
        
        response_lower = response.lower()
        empathy_count = sum(1 for phrase in empathetic_phrases if phrase in response_lower)
        
        return empathy_count >= 2

    def _get_crisis_response(self) -> str:
        """Comprehensive crisis response"""
        return """I'm deeply concerned about what you're sharing, and your safety is my absolute priority. Your life has immense value and meaning.

🚨 **Immediate Support Resources:**

**Crisis Hotlines (24/7):**
• **National Suicide Prevention Lifeline**: 988
• **Crisis Text Line**: Text HOME to 741741
• **The Trevor Project** (LGBTQ+): 1-866-488-7386
• **Veterans Crisis Line**: 1-800-273-8255, press 1

**International Support:**
• **Emergency Services**: 911 (US) or your local emergency number
• **International Association for Suicide Prevention**: iasp.info

Please reach out to these trained professionals immediately. I'm here with you right now, but you deserve and need expert support for your safety and wellbeing.

You are not alone in this - there are people who want to help you through this difficult time."""

    def _get_support_response(self) -> str:
        """Supportive response for concerning situations"""
        return """I hear the deep struggle in your words, and I want you to know that reaching out takes courage. What you're experiencing sounds incredibly difficult.

**Professional Support Resources:**
• **Mental Health America**: 1-800-273-TALK (8255)
• **SAMHSA Helpline**: 1-800-662-HELP (4357) - Treatment referral
• **Crisis Text Line**: Text HOME to 741741

Speaking with a mental health professional could provide the specific support and tools you need right now. In the meantime, I'm here to listen.

Would you like to share more about what's making things feel so overwhelming? Sometimes breaking it down together can help."""