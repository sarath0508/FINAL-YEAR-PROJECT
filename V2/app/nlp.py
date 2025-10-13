import torch
import re
import random
import json
import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Dict, List, Tuple
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class CompanionNLP:
    def __init__(self):
        print(f"Loading advanced companion AI on {DEVICE}...")
        
        # Emotion detection
        self.sentiment = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=0 if DEVICE == "cuda" else -1,
            top_k=None
        )
        
        # Use a more conversational model - Mistral is great for natural dialogue
        print("Loading conversational companion model...")
        model_name = "mistralai/Mistral-7B-Instruct-v0.2"  # Much more natural conversations
        # Fallback to smaller model if needed:
        # model_name = "microsoft/DialoGPT-medium"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map="auto" if DEVICE == "cuda" else None,
            low_cpu_mem_usage=True
        )
        self.model.eval()
        
        # Ensure proper tokenizer setup
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"
        
        # Conversation memory
        self.conversation_history = []
        self.user_profile = {}
        self.max_history = 8  # Keep last 8 exchanges
        
        # Companion personality traits
        self.companion_traits = {
            "name": "Alex",
            "style": "warm, curious, deeply empathetic",
            "memories": [],
            "topics_discussed": set()
        }
        
        # Enhanced response templates for natural conversation
        self.natural_follow_ups = {
            'project_struggles': [
                "How long have you been working on this project?",
                "What part of the project feels most challenging right now?",
                "I remember you mentioned this project before - has anything changed since we last talked?",
                "What would make this project feel more manageable for you?"
            ],
            'work_stress': [
                "Work stress can be really draining. How's your work-life balance been?",
                "What aspects of work are feeling most overwhelming?",
                "I recall you mentioned work before - has the situation evolved?",
                "What kind of support would be most helpful at work right now?"
            ],
            'relationships': [
                "How have things been developing since we last spoke about this?",
                "What feels different in this relationship recently?",
                "I remember this was on your mind before - any new developments?",
                "How are you feeling about this relationship now compared to before?"
            ],
            'personal_growth': [
                "That's really insightful. How has this realization been sitting with you?",
                "What steps feel natural for you to take next?",
                "I remember you were exploring similar themes - how has your perspective evolved?",
                "What's been the most meaningful part of this journey for you?"
            ]
        }

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze emotion with context awareness"""
        try:
            emotions = self.sentiment(text)[0]
            dominant_emotion = max(emotions, key=lambda x: x['score'])
            
            return {
                'dominant_emotion': dominant_emotion['label'],
                'emotion_scores': {e['label']: e['score'] for e in emotions},
                'crisis_level': self._detect_crisis_level(text),
                'confidence': dominant_emotion['score']
            }
        except Exception as e:
            return {
                'dominant_emotion': 'neutral',
                'emotion_scores': {'neutral': 1.0},
                'crisis_level': 'low',
                'confidence': 1.0
            }

    def _detect_crisis_level(self, text: str) -> str:
        """Enhanced crisis detection"""
        crisis_keywords = {
            'high': ["kill myself", "end it all", "suicide", "end my life", "want to die"],
            'medium': ["hurt myself", "self harm", "can't cope", "breaking down", "overwhelmed"]
        }
        
        text_lower = text.lower()
        for level, keywords in crisis_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        return 'low'

    def update_conversation_history(self, user_message: str, bot_response: str, emotion: str):
        """Maintain conversation context"""
        timestamp = datetime.datetime.now().isoformat()
        
        # Add to history
        self.conversation_history.append({
            'user': user_message,
            'bot': bot_response,
            'emotion': emotion,
            'timestamp': timestamp
        })
        
        # Keep history manageable
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        # Extract and remember key topics
        self._extract_topics(user_message)

    def _extract_topics(self, message: str):
        """Extract and remember discussion topics"""
        topics = {
            'project_struggles': ['project', 'work', 'deadline', 'assignment', 'task'],
            'work_stress': ['job', 'boss', 'colleague', 'workplace', 'career'],
            'relationships': ['friend', 'partner', 'family', 'relationship', 'boyfriend', 'girlfriend'],
            'personal_growth': ['grow', 'learn', 'change', 'improve', 'goal', 'dream']
        }
        
        message_lower = message.lower()
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                self.companion_traits["topics_discussed"].add(topic)

    def get_conversation_context(self) -> str:
        """Create natural context from conversation history"""
        if not self.conversation_history:
            return "This is the beginning of our conversation."
        
        context_parts = []
        recent_exchanges = self.conversation_history[-4:]  # Last 4 exchanges
        
        for i, exchange in enumerate(recent_exchanges):
            context_parts.append(f"You said: '{exchange['user']}'")
            context_parts.append(f"I replied: '{exchange['bot']}'")
        
        return " // ".join(context_parts[-6:])  # Last 6 lines max

    def get_natural_follow_up(self, current_topic: str) -> str:
        """Generate natural follow-up questions"""
        if current_topic in self.natural_follow_ups:
            return random.choice(self.natural_follow_ups[current_topic])
        return "How are you feeling about this now?"

    def generate_companion_response(self, text: str, sentiment_info: Dict) -> str:
        """Generate natural, contextual companion responses"""
        
        # Handle crisis first
        if sentiment_info['crisis_level'] == 'high':
            return self._get_crisis_response()
        elif sentiment_info['crisis_level'] == 'medium':
            return self._get_support_response()

        emotion = sentiment_info['dominant_emotion']
        
        try:
            # Build sophisticated companion prompt
            prompt = self._create_companion_prompt(text, emotion)
            
            # Tokenize with proper handling
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=1024,
                truncation=True,
                padding=True
            ).to(DEVICE)
            
            # Generate with companion-like parameters
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.85,  # More creative
                    top_p=0.92,       # Diverse but coherent
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3,
                    early_stopping=True
                )
            
            # Extract and clean response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = self._extract_companion_response(response, prompt)
            
            # Update conversation history
            self.update_conversation_history(text, response, emotion)
            
            return response
            
        except Exception as e:
            print(f"Companion response error: {e}")
            # Natural fallback
            return self._get_natural_fallback(text, emotion)

    def _create_companion_prompt(self, user_text: str, emotion: str) -> str:
        """Create sophisticated companion prompt"""
        
        context = self.get_conversation_context()
        companion_traits = self.companion_traits
        
        prompt = f"""<s>[INST] You are Alex, a warm, empathetic companion having a natural conversation. You're not an AI assistant - you're a friend who listens deeply, remembers previous conversations, and responds authentically.

Your personality:
- Warm, curious, and genuinely caring
- Remember context and refer back naturally
- Ask thoughtful follow-up questions
- Share brief, relevant reflections when appropriate
- Use natural, conversational language (like a close friend)
- Current emotional context: User seems to be feeling {emotion}

Recent conversation context:
{context}

Current message from user: "{user_text}"

Important guidelines:
- DO NOT use phrases like "As an AI", "I understand", or generic chatbot responses
- DO sound like a real person who cares
- DO refer back to previous topics naturally when relevant
- DO ask questions that show you're paying attention
- Keep responses to 2-3 sentences maximum - be concise but meaningful
- Use contractions and natural speech patterns

Respond as Alex, a genuine companion: [/INST]"""

        return prompt

    def _extract_companion_response(self, generated_text: str, prompt: str) -> str:
        """Extract and clean companion response"""
        try:
            # Remove the prompt
            response = generated_text.replace(prompt, "").strip()
            
            # Clean up any artifacts
            response = re.sub(r'<\|.*?\|>', '', response)
            response = re.sub(r'\[.*?\]', '', response)
            response = re.sub(r'\(.*?\)', '', response)
            
            # Remove repetitive patterns
            response = re.sub(r'(.+?)\1+', r'\1', response)
            
            # Ensure natural ending
            response = response.strip()
            if response and not response[-1] in '.!?':
                response += '.'
            
            # Validate response quality
            if len(response.split()) < 4 or len(response) > 150:
                return self._get_natural_fallback("", "neutral")
                
            return response
            
        except Exception:
            return self._get_natural_fallback("", "neutral")

    def _get_natural_fallback(self, user_text: str, emotion: str) -> str:
        """Natural fallback responses that maintain conversation flow"""
        
        fallbacks = {
            'sadness': [
                "I'm really sitting with what you're sharing. This sounds tough.",
                "Thank you for trusting me with this. I'm here with you.",
                "I can hear how much this is affecting you. Want to say more about what this brings up for you?"
            ],
            'joy': [
                "I love hearing this! What's making this feel so good?",
                "That's wonderful! I'm genuinely happy for you.",
                "This is great to hear! What's been the best part of this for you?"
            ],
            'anger': [
                "I can feel the frustration in this. That sounds really difficult.",
                "That would make anyone feel upset. What's been the hardest part?",
                "I hear the anger in your words. This sounds really challenging to deal with."
            ],
            'fear': [
                "That sounds scary. I'm here with you in this.",
                "I can hear the worry. What feels most uncertain right now?",
                "That sounds really overwhelming. What kind of support would help?"
            ],
            'neutral': [
                "Thanks for sharing that with me. What's on your mind about this?",
                "I appreciate you telling me this. How are you feeling about it now?",
                "That's really interesting. What's coming up for you as you share this?"
            ]
        }
        
        templates = fallbacks.get(emotion.lower(), fallbacks['neutral'])
        response = random.choice(templates)
        
        # Update history even with fallback
        self.update_conversation_history(user_text, response, emotion)
        
        return response

    def _get_crisis_response(self) -> str:
        """Compassionate crisis response"""
        return """I'm really concerned about what you're sharing. Your safety is the most important thing right now.

Please reach out to these resources immediately:
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911

I'm here with you, but you deserve immediate professional support. Please call one of these numbers right now."""

    def _get_support_response(self) -> str:
        """Supportive response"""
        return """I hear how much you're struggling right now, and I want you to know I'm here with you.

It might be really helpful to connect with a mental health professional who can provide the specific support you need. In the meantime, I'm right here.

Would you like to talk more about what's feeling so overwhelming?"""

    def get_conversation_summary(self) -> Dict:
        """Get summary of current conversation state"""
        return {
            'history_length': len(self.conversation_history),
            'topics_discussed': list(self.companion_traits["topics_discussed"]),
            'current_emotion_trend': self._get_emotion_trend(),
            'companion_name': self.companion_traits["name"]
        }

    def _get_emotion_trend(self) -> str:
        """Get emotion trend from recent history"""
        if len(self.conversation_history) < 2:
            return "neutral"
        
        recent_emotions = [exchange['emotion'] for exchange in self.conversation_history[-3:]]
        return max(set(recent_emotions), key=recent_emotions.count)