import re
import random
import datetime
from typing import Dict, List
import time

class CompanionNLP:
    def __init__(self):
        print("Loading ultra-light companion AI...")
        
        # Simple sentiment analysis using keyword matching
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'good', 'wonderful', 'amazing', 'love', 'joy', 'fantastic'],
            'sadness': ['sad', 'depressed', 'unhappy', 'miserable', 'cry', 'tears', 'hurt', 'lonely', 'down'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'rage', 'upset'],
            'fear': ['scared', 'afraid', 'anxious', 'worried', 'nervous', 'panic', 'fear', 'terrified'],
            'surprise': ['surprised', 'shocked', 'amazed', 'unexpected', 'wow', 'astonished'],
            'disgust': ['disgusted', 'gross', 'dislike', 'hate', 'awful', 'revolting']
        }
        
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
        
        # Advanced empathetic response system
        self.response_system = AdvancedResponseSystem()

    def analyze_sentiment(self, text: str) -> Dict:
        """Lightweight sentiment analysis using keyword matching"""
        text_lower = text.lower()
        
        # Special case for greetings and simple messages
        if self._is_greeting(text_lower):
            return {
                'dominant_emotion': 'neutral',
                'emotion_scores': {'neutral': 1.0},
                'crisis_level': 'low',
                'confidence': 1.0
            }
        
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score
        
        # Find dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        # Crisis detection
        crisis_level = self._detect_crisis_level(text)
        
        return {
            'dominant_emotion': dominant_emotion[0] if dominant_emotion[1] > 0 else 'neutral',
            'emotion_scores': emotion_scores,
            'crisis_level': crisis_level,
            'confidence': min(1.0, dominant_emotion[1] / 5.0)
        }

    def _is_greeting(self, text: str) -> bool:
        """Check if message is a simple greeting"""
        greetings = [
            'hi', 'hello', 'hey', 'hi there', 'hello there', 'hey there',
            'good morning', 'good afternoon', 'good evening'
        ]
        return any(greeting in text for greeting in greetings) and len(text.split()) <= 4

    def _detect_crisis_level(self, text: str) -> str:
        """Crisis detection"""
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

    def _extract_conversation_insights(self, message: str):
        """Extract topics and user interests"""
        message_lower = message.lower()
        
        # Topics
        topics = {
            'work': ['work', 'job', 'career', 'office', 'boss', 'colleague', 'workplace'],
            'projects': ['project', 'assignment', 'task', 'deadline', 'homework'],
            'relationships': ['friend', 'partner', 'family', 'relationship', 'boyfriend', 'girlfriend', 'husband', 'wife'],
            'health': ['health', 'sick', 'tired', 'sleep', 'exercise', 'doctor', 'hospital'],
            'hobbies': ['hobby', 'interest', 'game', 'music', 'sport', 'art', 'reading', 'movie'],
            'school': ['school', 'college', 'university', 'class', 'exam', 'test', 'study']
        }
        
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                self.companion_traits["topics_discussed"].add(topic)
        
        # User interests (specific things mentioned)
        interests = ['book', 'movie', 'music', 'game', 'sport', 'travel', 'food', 'art', 'reading', 'writing']
        for interest in interests:
            if interest in message_lower:
                self.companion_traits["user_interests"].add(interest)

    def generate_companion_response(self, text: str, sentiment_info: Dict) -> str:
        """Generate natural, contextual companion responses"""
        
        # Handle crisis first
        if sentiment_info['crisis_level'] == 'high':
            return self._get_crisis_response()
        elif sentiment_info['crisis_level'] == 'medium':
            return self._get_support_response()

        emotion = sentiment_info['dominant_emotion']
        
        # Generate contextual response
        response = self.response_system.generate_response(
            text, 
            emotion, 
            self.conversation_history,
            self.companion_traits
        )
        
        # Update first interaction flag
        if self.companion_traits["first_interaction"]:
            self.companion_traits["first_interaction"] = False
        
        # Update conversation history
        self.update_conversation_history(text, response, emotion)
        
        return response

    def _get_crisis_response(self) -> str:
        return """I'm really concerned about what you're sharing. Your safety is the most important thing.

Please reach out immediately:
• Suicide Prevention: 988
• Crisis Text Line: Text HOME to 741741  
• Emergency Services: 911

You deserve professional support right now."""

    def _get_support_response(self) -> str:
        return """I hear how much you're struggling. This sounds incredibly difficult.

Consider speaking with a mental health professional. I'm here with you in the meantime.

Would you like to talk about what's feeling most overwhelming?"""

    def get_conversation_summary(self) -> Dict:
        return {
            'history_length': len(self.conversation_history),
            'topics_discussed': list(self.companion_traits["topics_discussed"]),
            'user_interests': list(self.companion_traits["user_interests"]),
            'current_emotion_trend': self._get_emotion_trend(),
            'first_interaction': self.companion_traits["first_interaction"]
        }

    def _get_emotion_trend(self) -> str:
        if len(self.conversation_history) < 2:
            return "neutral"
        recent_emotions = [exchange['emotion'] for exchange in self.conversation_history[-3:]]
        return max(set(recent_emotions), key=recent_emotions.count)


class AdvancedResponseSystem:
    """Advanced template-based response system with contextual awareness"""
    
    def __init__(self):
        self.response_templates = self._build_response_templates()
    
    def _build_response_templates(self):
        return {
            # Greeting responses
            'greetings': [
                "Hi there! 😊 It's really nice to meet you. How are you feeling today?",
                "Hello! Thanks for reaching out. What's on your mind?",
                "Hey! I'm glad you're here. How has your day been?",
                "Hi! It's good to connect with you. What would you like to talk about?",
                "Hello there! I'm here to listen. How are things going for you?"
            ],
            
            # Emotional responses
            'emotional': {
                'sadness': [
                    "I hear the sadness in your words. That sounds really heavy to carry. What's been the most difficult part?",
                    "Thank you for trusting me with this. I'm sitting with you in this sadness. Want to share more about what's weighing on you?",
                    "That sounds incredibly tough. Your feelings are completely valid. How long has this been affecting you?",
                    "I can feel the weight in what you're sharing. You're not alone in this. What kind of support would feel helpful right now?"
                ],
                'joy': [
                    "I love hearing this! Your joy is contagious. What's making this feel so special?",
                    "That's wonderful! Celebrating these moments is so important. Tell me more about what's bringing you happiness!",
                    "This is so great to hear! Positive energy like this is precious. What's been the highlight for you?",
                    "Your happiness shines through! Thanks for sharing this beautiful moment. What thoughts come up when you feel this way?"
                ],
                'anger': [
                    "I can feel the intensity of your frustration. That sounds really challenging to navigate. What's been the most upsetting part?",
                    "That would make anyone feel angry. Your feelings make complete sense. What would help you feel heard right now?",
                    "I hear the anger in your words. This sounds genuinely difficult to deal with. What aspect feels most unfair?",
                    "That sounds incredibly frustrating. Anger often comes from real pain. Want to explore what's underneath these feelings?"
                ],
                'fear': [
                    "That sounds scary. I'm here with you in this uncertainty. What feels most overwhelming right now?",
                    "I can hear the worry in your voice. Fear can be so consuming. What kind of reassurance would help?",
                    "That sounds really frightening. You're brave for sharing this. What support would feel most comforting?",
                    "I hear the anxiety in what you're saying. Let's break this down together - what's the smallest step forward?"
                ],
                'neutral': [
                    "Thanks for sharing that. What's coming up for you as you think about this?",
                    "I appreciate you telling me this. How are you feeling about it now?",
                    "That's really interesting. What thoughts does this bring up for you?",
                    "Thanks for opening up. What would you like to explore about this?"
                ]
            },
            
            # Contextual follow-ups
            'contextual': {
                'work': [
                    "Work stress can be really draining. How's your work-life balance been lately?",
                    "That sounds challenging. What aspects of work are most demanding right now?",
                    "I remember you mentioned work before. Has anything changed since we last talked?",
                    "Work pressures can build up. What would make your work environment feel more supportive?"
                ],
                'projects': [
                    "Projects can feel overwhelming. What part has been most challenging for you?",
                    "That sounds tough. How long have you been working on this project?",
                    "Project deadlines can create so much pressure. What would help make it more manageable?",
                    "I recall you were working on this. Has anything gotten easier or harder recently?"
                ],
                'relationships': [
                    "Relationships can be complicated. How are you feeling about this situation now?",
                    "That sounds difficult. What do you need most in this relationship right now?",
                    "I remember this was on your mind. Any new developments since we spoke?",
                    "Relationship dynamics can shift. How has your perspective changed over time?"
                ],
                'health': [
                    "Health concerns can be worrying. How has this been affecting your daily life?",
                    "That sounds concerning. What kind of support are you getting for this?",
                    "Physical health really impacts everything. What small steps feel manageable?",
                    "I hear the concern in your voice. What would ideal support look like for you?"
                ]
            },
            
            # Continuation phrases
            'continuation': [
                "I remember you mentioned something similar before. How are things developing?",
                "This reminds me of our previous conversation. What's changed since then?",
                "You've been exploring this topic for a while. How has your understanding evolved?",
                "I recall this was important to you. What new insights have emerged?",
                "We've touched on this before. What feels different about it now?"
            ],
            
            # Simple acknowledgment
            'acknowledgment': [
                "I hear you. Tell me more about what that's like for you.",
                "Thanks for sharing that. What's that experience been like?",
                "I'm listening. What else comes to mind when you think about this?",
                "That makes sense. How are you feeling as you share this?"
            ]
        }
    
    def generate_response(self, user_text: str, emotion: str, history: List, traits: Dict) -> str:
        """Generate sophisticated contextual response"""
        
        user_text_lower = user_text.lower()
        
        # 1. Handle greetings (first message or simple hello)
        if self._is_greeting(user_text_lower, traits):
            return random.choice(self.response_templates['greetings'])
        
        # 2. Handle very short messages that aren't greetings
        if len(user_text.split()) <= 2 and not self._contains_emotion_words(user_text_lower):
            return random.choice(self.response_templates['acknowledgment'])
        
        # 3. Check for contextual follow-up based on content
        contextual_response = self._get_contextual_follow_up(user_text_lower, traits)
        if contextual_response:
            return contextual_response
        
        # 4. Check for conversation continuation
        if len(history) > 1:
            continuation_response = self._get_continuation_response(user_text_lower, history)
            if continuation_response:
                return continuation_response
        
        # 5. Return emotional response
        emotional_responses = self.response_templates['emotional'].get(emotion, self.response_templates['emotional']['neutral'])
        response = random.choice(emotional_responses)
        
        return response
    
    def _is_greeting(self, text: str, traits: Dict) -> bool:
        """Check if this is a greeting situation"""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        
        # First interaction greeting
        if traits.get("first_interaction", True) and any(greeting in text for greeting in greetings):
            return True
        
        # Simple greeting in ongoing conversation
        if any(greeting in text for greeting in greetings) and len(text.split()) <= 4:
            return True
            
        return False
    
    def _contains_emotion_words(self, text: str) -> bool:
        """Check if text contains emotion-related words"""
        emotion_words = ['sad', 'happy', 'angry', 'scared', 'excited', 'worried', 'stressed']
        return any(word in text for word in emotion_words)
    
    def _get_contextual_follow_up(self, user_text: str, traits: Dict) -> str:
        """Get context-aware follow-up question"""
        
        # Check for topic matches
        topic_mapping = {
            'work': ['work', 'job', 'career', 'boss', 'colleague', 'workplace'],
            'projects': ['project', 'assignment', 'deadline', 'homework', 'task'],
            'relationships': ['friend', 'partner', 'relationship', 'boyfriend', 'girlfriend', 'family'],
            'health': ['health', 'sick', 'tired', 'sleep', 'exercise', 'doctor'],
            'school': ['school', 'college', 'university', 'class', 'exam', 'study']
        }
        
        for topic, keywords in topic_mapping.items():
            if any(keyword in user_text for keyword in keywords):
                if topic in self.response_templates['contextual']:
                    return random.choice(self.response_templates['contextual'][topic])
        
        return None
    
    def _get_continuation_response(self, current_text: str, history: List) -> str:
        """Get response that continues previous conversation"""
        if len(history) < 2:
            return None
        
        # Get recent user messages (excluding current one)
        previous_texts = [h['user'].lower() for h in history[:-1]][-2:]  # Last 2 previous messages
        
        # Check for common topics between current and previous messages
        common_topics = ['work', 'project', 'friend', 'family', 'health', 'school', 'relationship']
        
        for topic in common_topics:
            current_has_topic = topic in current_text
            previous_has_topic = any(topic in prev_text for prev_text in previous_texts)
            
            if current_has_topic and previous_has_topic:
                if random.random() > 0.5:  # 50% chance to reference past
                    return random.choice(self.response_templates['continuation'])
        
        return None