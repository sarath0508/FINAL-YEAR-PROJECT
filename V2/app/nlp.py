import torch
import re
import random
import datetime
import requests
import json
from typing import Dict, List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class CompanionNLP:
    def __init__(self):
        print(f"Loading enhanced companion AI on {DEVICE}...")
        
        # Initialize AI models
        self.setup_ai_models()
        
        # Internet knowledge integration
        self.setup_internet_integration()
        
        # Conversation memory
        self.conversation_history = []
        self.max_history = 8
        
        # Companion personality
        self.companion_traits = {
            "name": "Alex",
            "topics_discussed": set(),
            "user_interests": set(),
            "first_interaction": True
        }
        
        # Enhanced response system
        self.response_system = AIEnhancedResponseSystem()

    def setup_ai_models(self):
        """Setup lightweight but powerful AI models"""
        try:
            # Enhanced sentiment analysis
            self.sentiment_analyzer = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if DEVICE == "cuda" else -1,
                max_length=512,
                truncation=True
            )
            print("✓ Loaded enhanced sentiment analyzer")
            
            # Lightweight but capable chat model
            self.chat_model = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium", 
                device=0 if DEVICE == "cuda" else -1,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                model_kwargs={"load_in_8bit": True} if DEVICE == "cuda" else {}
            )
            print("✓ Loaded AI chat model")
            
        except Exception as e:
            print(f"AI model loading failed: {e}")
            print("Falling back to template-only mode")
            self.chat_model = None
            self.sentiment_analyzer = None

    def setup_internet_integration(self):
        """Setup internet knowledge sources"""
        # Free APIs for knowledge (no key required for basic usage)
        self.knowledge_sources = {
            "mental_health_tips": "https://api.adviceslip.com/advice",
            "quotes": "https://api.quotable.io/random",
            "self_help": "https://zenquotes.io/api/random"
        }
        
        # Optional: Add Serper API for web search (get free key from serper.dev)
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.enable_web_search = self.serper_api_key is not None

    def analyze_sentiment(self, text: str) -> Dict:
        """Enhanced sentiment analysis with AI model"""
        text_lower = text.lower()
        
        # Handle greetings
        if self._is_greeting(text_lower):
            return {
                'dominant_emotion': 'neutral',
                'emotion_scores': {'neutral': 1.0},
                'crisis_level': 'low',
                'confidence': 1.0
            }
        
        # Use AI model if available, otherwise fallback to keyword matching
        if self.sentiment_analyzer:
            try:
                result = self.sentiment_analyzer(text)[0]
                sentiment_map = {
                    'positive': 'joy',
                    'negative': 'sadness', 
                    'neutral': 'neutral'
                }
                
                return {
                    'dominant_emotion': sentiment_map.get(result['label'], 'neutral'),
                    'emotion_scores': {result['label']: result['score']},
                    'crisis_level': self._detect_crisis_level(text),
                    'confidence': result['score']
                }
            except Exception as e:
                print(f"AI sentiment analysis failed: {e}")
        
        # Fallback to keyword-based sentiment
        return self._keyword_sentiment_analysis(text)

    def _keyword_sentiment_analysis(self, text: str) -> Dict:
        """Fallback keyword-based sentiment analysis"""
        emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'good', 'wonderful', 'amazing', 'love', 'joy'],
            'sadness': ['sad', 'depressed', 'unhappy', 'miserable', 'cry', 'tears', 'hurt', 'lonely'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'rage'],
            'fear': ['scared', 'afraid', 'anxious', 'worried', 'nervous', 'panic', 'fear'],
            'surprise': ['surprised', 'shocked', 'amazed', 'unexpected', 'wow'],
            'disgust': ['disgusted', 'gross', 'dislike', 'hate', 'awful']
        }
        
        emotion_scores = {}
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score
        
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        return {
            'dominant_emotion': dominant_emotion[0] if dominant_emotion[1] > 0 else 'neutral',
            'emotion_scores': emotion_scores,
            'crisis_level': self._detect_crisis_level(text),
            'confidence': min(1.0, dominant_emotion[1] / 5.0)
        }

    def _is_greeting(self, text: str) -> bool:
        """Check if message is a simple greeting"""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in text for greeting in greetings) and len(text.split()) <= 4

    def _detect_crisis_level(self, text: str) -> str:
        """Enhanced crisis detection"""
        crisis_keywords = {
            'high': ["kill myself", "end it all", "suicide", "end my life", "want to die", "not worth living"],
            'medium': ["hurt myself", "self harm", "can't cope", "breaking down", "overwhelmed", "panic attack"]
        }
        
        text_lower = text.lower()
        for level, keywords in crisis_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        return 'low'

    def get_internet_knowledge(self, topic: str) -> Optional[str]:
        """Get helpful information from internet APIs"""
        try:
            # Mental health advice
            if any(word in topic.lower() for word in ['stress', 'anxiety', 'worry', 'sad', 'depressed']):
                response = requests.get(self.knowledge_sources["mental_health_tips"], timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return f"Here's a helpful perspective: {data['slip']['advice']}"
            
            # Motivational quotes for encouragement
            if any(word in topic.lower() for word in ['motivation', 'encouragement', 'inspired', 'hope']):
                response = requests.get(self.knowledge_sources["quotes"], timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return f"\"{data['content']}\" - {data['author']}"
            
            # General wisdom
            response = requests.get(self.knowledge_sources["self_help"], timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return f"Some wisdom to consider: {data[0]['q']} - {data[0]['a']}"
                    
        except Exception as e:
            print(f"Internet knowledge fetch failed: {e}")
        
        return None

    def web_search(self, query: str) -> Optional[str]:
        """Search the web for relevant information"""
        if not self.enable_web_search:
            return None
            
        try:
            url = "https://google.serper.dev/search"
            payload = {
                "q": query + " mental health tips advice",
                "gl": "us",
                "hl": "en"
            }
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json()
                if 'organic' in results and len(results['organic']) > 0:
                    # Return the most relevant snippet
                    return results['organic'][0].get('snippet', '')
        except Exception as e:
            print(f"Web search error: {e}")
        
        return None

    def generate_companion_response(self, text: str, sentiment_info: Dict) -> str:
        """Generate response using AI + Internet knowledge + templates"""
        
        # Handle crisis first
        if sentiment_info['crisis_level'] == 'high':
            return self._get_crisis_response()
        elif sentiment_info['crisis_level'] == 'medium':
            return self._get_support_response()

        emotion = sentiment_info['dominant_emotion']
        
        # Try AI model with internet knowledge
        ai_response = self._generate_ai_enhanced_response(text, emotion)
        if ai_response and self._is_quality_response(ai_response):
            self._update_conversation_history(text, ai_response, emotion)
            return ai_response
        
        # Fallback to enhanced template system
        template_response = self.response_system.generate_response(
            text, emotion, self.conversation_history, self.companion_traits
        )
        self._update_conversation_history(text, template_response, emotion)
        return template_response

    def _generate_ai_enhanced_response(self, text: str, emotion: str) -> Optional[str]:
        """Generate response using AI model enhanced with internet knowledge"""
        if not self.chat_model:
            return None
            
        try:
            # Get conversation context
            context = self._get_conversation_context()
            
            # Get relevant internet knowledge
            knowledge = self.get_internet_knowledge(text)
            knowledge_context = f"Relevant insight: {knowledge}\n" if knowledge else ""
            
            prompt = f"""You are Alex, a compassionate, empathetic companion. Provide warm, supportive responses that show genuine care.

{context}
{knowledge_context}
User: {text}
Alex:"""

            # Generate response
            response = self.chat_model(
                prompt,
                max_new_tokens=100,
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.chat_model.tokenizer.eos_token_id,
                repetition_penalty=1.1,
                num_return_sequences=1
            )[0]['generated_text']
            
            # Extract just the assistant's response
            response = response.replace(prompt, "").strip()
            
            # Clean up response
            response = re.sub(r'<\|.*?\|>', '', response)
            response = re.sub(r'\[.*?\]', '', response)
            response = response.split('\n')[0].strip()
            
            return response if self._is_quality_response(response) else None
                
        except Exception as e:
            print(f"AI generation error: {e}")
            return None

    def _get_conversation_context(self) -> str:
        """Get conversation context for AI model"""
        if not self.conversation_history:
            return "This is the start of a conversation. Be warm and welcoming."
        
        context_parts = ["Previous conversation:"]
        for exchange in self.conversation_history[-3:]:
            context_parts.append(f"User: {exchange['user']}")
            context_parts.append(f"Alex: {exchange['bot']}")
        
        return "\n".join(context_parts)

    def _is_quality_response(self, response: str) -> bool:
        """Check if response is of good quality"""
        if not response or len(response.strip()) == 0:
            return False
        
        words = response.split()
        if len(words) < 3 or len(words) > 150:
            return False
            
        # Check for common AI failure patterns
        failure_indicators = [
            "I cannot", "I'm unable to", "As an AI", "I don't have", 
            "I'm not programmed", "I don't understand the question"
        ]
        
        return not any(indicator in response for indicator in failure_indicators)

    def _update_conversation_history(self, user_message: str, bot_response: str, emotion: str):
        """Update conversation history and extract insights"""
        self.conversation_history.append({
            'user': user_message,
            'bot': bot_response,
            'emotion': emotion,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        # Extract topics and interests
        self._extract_conversation_insights(user_message)
        
        # Update first interaction flag
        if self.companion_traits["first_interaction"]:
            self.companion_traits["first_interaction"] = False

    def _extract_conversation_insights(self, message: str):
        """Extract topics and user interests"""
        message_lower = message.lower()
        
        topics = {
            'work': ['work', 'job', 'career', 'office', 'boss', 'colleague', 'workplace'],
            'projects': ['project', 'assignment', 'task', 'deadline', 'homework'],
            'relationships': ['friend', 'partner', 'family', 'relationship', 'boyfriend', 'girlfriend'],
            'health': ['health', 'sick', 'tired', 'sleep', 'exercise', 'doctor', 'hospital'],
            'hobbies': ['hobby', 'interest', 'game', 'music', 'sport', 'art', 'reading', 'movie'],
            'school': ['school', 'college', 'university', 'class', 'exam', 'test', 'study']
        }
        
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                self.companion_traits["topics_discussed"].add(topic)
        
        interests = ['book', 'movie', 'music', 'game', 'sport', 'travel', 'food', 'art', 'reading']
        for interest in interests:
            if interest in message_lower:
                self.companion_traits["user_interests"].add(interest)

    def _get_crisis_response(self) -> str:
        return """I'm deeply concerned about what you're sharing. Your safety is the absolute priority.

Immediate help:
• Suicide Prevention: 988
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911

Please reach out now. You deserve professional support."""

    def _get_support_response(self) -> str:
        return """I hear how much you're struggling. This sounds incredibly difficult.

Speaking with a mental health professional could provide the support you need. I'm here with you in the meantime.

Would you like to talk about what's feeling most overwhelming?"""

    def get_conversation_summary(self) -> Dict:
        return {
            'history_length': len(self.conversation_history),
            'topics_discussed': list(self.companion_traits["topics_discussed"]),
            'user_interests': list(self.companion_traits["user_interests"]),
            'current_emotion_trend': self._get_emotion_trend(),
            'using_ai': self.chat_model is not None,
            'internet_enabled': self.enable_web_search
        }

    def _get_emotion_trend(self) -> str:
        if len(self.conversation_history) < 2:
            return "neutral"
        recent_emotions = [exchange['emotion'] for exchange in self.conversation_history[-3:]]
        return max(set(recent_emotions), key=recent_emotions.count)


class AIEnhancedResponseSystem:
    """Enhanced response system that combines AI with templates"""
    
    def __init__(self):
        self.responses = self._build_enhanced_responses()
    
    def _build_enhanced_responses(self):
        return {
            'greetings': [
                "Hi there! 😊 It's wonderful to connect with you. How are you feeling today?",
                "Hello! Thanks for reaching out. I'm here to listen and support you.",
                "Hey! I'm really glad you're here. What's been on your mind lately?",
                "Hi! It's good to meet you. I'm here whenever you need someone to talk to."
            ],
            
            'emotional': {
                'sadness': [
                    "I hear the sadness in your words, and I want you to know I'm here with you. This sounds really heavy to carry.",
                    "Thank you for trusting me with these feelings. Sadness can be so profound. What's been the most difficult part?",
                    "I can feel the weight in what you're sharing. Your feelings are completely valid and important.",
                    "That sounds incredibly tough. You're showing courage by sharing this. What kind of support would feel helpful?"
                ],
                'joy': [
                    "Your joy is absolutely beautiful to witness! 😊 What's making this moment feel so special?",
                    "I love hearing this! Positive energy like yours is truly uplifting. Tell me more!",
                    "This is wonderful! Celebrating these good moments is so important for our wellbeing.",
                    "Your happiness shines through! Thanks for sharing this beautiful energy with me."
                ],
                'anger': [
                    "I can feel the intensity of your frustration. That sounds really challenging to sit with.",
                    "Your anger makes complete sense given what you're describing. These feelings often come from real pain.",
                    "I hear the frustration in your words. This sounds genuinely difficult to navigate.",
                    "That sounds incredibly upsetting. Anger is often a signal that something important needs attention."
                ],
                'fear': [
                    "That sounds scary. I'm right here with you in this uncertainty. What feels most overwhelming?",
                    "I can hear the worry in what you're sharing. Fear can be so consuming.",
                    "That sounds really frightening. You're brave for facing these feelings.",
                    "I hear the anxiety in your words. Let's breathe through this together."
                ]
            },
            
            'with_internet_knowledge': [
                "I found this perspective that might help: {knowledge} What are your thoughts?",
                "This insight came to mind: {knowledge} How does that resonate with you?",
                "Here's something to consider: {knowledge} What's your take on this?",
                "This might be helpful: {knowledge} How are you feeling about this approach?"
            ]
        }
    
    def generate_response(self, text: str, emotion: str, history: List, traits: Dict) -> str:
        """Generate response with potential internet knowledge integration"""
        text_lower = text.lower()
        
        # Handle greetings
        if self._is_greeting(text_lower, traits):
            return random.choice(self.responses['greetings'])
        
        # Get emotional response
        emotional_responses = self.responses['emotional'].get(emotion, self.responses['emotional']['sadness'])
        response = random.choice(emotional_responses)
        
        return response
    
    def _is_greeting(self, text: str, traits: Dict) -> bool:
        """Check if this is a greeting"""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        
        if traits.get("first_interaction", True) and any(greeting in text for greeting in greetings):
            return True
        
        if any(greeting in text for greeting in greetings) and len(text.split()) <= 4:
            return True
            
        return False