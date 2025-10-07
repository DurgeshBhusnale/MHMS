"""
🧠 Enhanced AI Mental Health Chat Service with Advanced NLP

Features:
- Advanced sentiment analysis using NLTK and TextBlob
- Emotion detection with machine learning
- Dynamic response generation based on emotional state
- Personalized mental health interventions
- Conversation memory and context tracking
- Crisis detection and intervention
- Mental health assessment scoring
"""

import json
import os
import re
import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK data...")
    nltk.download('punkt', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('stopwords', quiet=True)

from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MentalHealthNLP:
    """Advanced NLP processor for mental health analysis"""
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # Mental health keywords for emotion detection
        self.emotion_keywords = {
            'depression': {
                'severe': ['suicidal', 'worthless', 'hopeless', 'despair', 'kill myself', 'end it all'],
                'moderate': ['depressed', 'sad', 'down', 'empty', 'numb', 'lost'],
                'mild': ['low', 'blue', 'gloomy', 'melancholy', 'disappointed']
            },
            'anxiety': {
                'severe': ['panic', 'terrified', 'overwhelmed', 'catastrophic', 'uncontrollable'],
                'moderate': ['anxious', 'worried', 'nervous', 'stressed', 'tense'],
                'mild': ['concerned', 'uneasy', 'restless', 'bothered']
            },
            'anger': {
                'severe': ['furious', 'enraged', 'livid', 'explosive'],
                'moderate': ['angry', 'mad', 'irritated', 'frustrated'],
                'mild': ['annoyed', 'bothered', 'upset']
            },
            'positive': {
                'high': ['excellent', 'amazing', 'fantastic', 'wonderful', 'great'],
                'moderate': ['good', 'fine', 'okay', 'alright'],
                'mild': ['better', 'improving', 'stable']
            }
        }
        
        # Crisis keywords for immediate intervention
        self.crisis_keywords = [
            'kill myself', 'end my life', 'suicide', 'want to die', 'better off dead',
            'can\'t go on', 'end it all', 'no point living', 'harm myself'
        ]
        
        # Initialize emotion classifier
        self._train_emotion_classifier()
    
    def _train_emotion_classifier(self):
        """Train a simple emotion classifier using keyword patterns"""
        # Create training data from keywords
        training_texts = []
        training_labels = []
        
        for emotion, severity_dict in self.emotion_keywords.items():
            for severity, keywords in severity_dict.items():
                for keyword in keywords:
                    # Create variations of the keyword in sentences
                    sentences = [
                        f"I feel {keyword}",
                        f"I am {keyword}",
                        f"Feeling {keyword} today",
                        f"I'm so {keyword}",
                        keyword
                    ]
                    training_texts.extend(sentences)
                    training_labels.extend([emotion] * len(sentences))
        
        # Train classifier
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = self.vectorizer.fit_transform(training_texts)
        
        self.emotion_classifier = LogisticRegression(random_state=42)
        self.emotion_classifier.fit(X, training_labels)
        
        logger.info("Emotion classifier trained successfully")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using multiple methods"""
        # NLTK VADER sentiment
        vader_scores = self.sia.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # Combined analysis
        compound_score = vader_scores['compound']
        
        if compound_score >= 0.05:
            overall_sentiment = 'positive'
        elif compound_score <= -0.05:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'compound_score': compound_score,
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'textblob_polarity': textblob_polarity,
            'textblob_subjectivity': textblob_subjectivity,
            'confidence': abs(compound_score)
        }
    
    def detect_emotion(self, text: str) -> Dict[str, Any]:
        """Detect emotions using keyword matching and ML"""
        text_lower = text.lower()
        detected_emotions = {}
        severity_scores = {}
        
        # Keyword-based emotion detection
        for emotion, severity_dict in self.emotion_keywords.items():
            emotion_score = 0
            max_severity = 'none'
            
            for severity, keywords in severity_dict.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        if severity == 'severe':
                            emotion_score += 3
                            max_severity = 'severe'
                        elif severity == 'moderate':
                            emotion_score += 2
                            if max_severity != 'severe':
                                max_severity = 'moderate'
                        elif severity == 'mild':
                            emotion_score += 1
                            if max_severity == 'none':
                                max_severity = 'mild'
            
            if emotion_score > 0:
                detected_emotions[emotion] = max_severity
                severity_scores[emotion] = emotion_score
        
        # ML-based emotion prediction
        try:
            text_vector = self.vectorizer.transform([text])
            emotion_proba = self.emotion_classifier.predict_proba(text_vector)[0]
            emotion_classes = self.emotion_classifier.classes_
            
            # Get top predicted emotion
            top_emotion_idx = np.argmax(emotion_proba)
            ml_emotion = emotion_classes[top_emotion_idx]
            ml_confidence = emotion_proba[top_emotion_idx]
            
            if ml_confidence > 0.3:  # Confidence threshold
                detected_emotions[f'ml_{ml_emotion}'] = 'predicted'
                severity_scores[f'ml_{ml_emotion}'] = ml_confidence
        
        except Exception as e:
            logger.warning(f"ML emotion detection failed: {e}")
        
        # Determine primary emotion
        if severity_scores:
            primary_emotion = max(severity_scores.items(), key=lambda x: x[1])
            primary_emotion_name = primary_emotion[0].replace('ml_', '')
        else:
            primary_emotion_name = 'neutral'
        
        return {
            'primary_emotion': primary_emotion_name,
            'detected_emotions': detected_emotions,
            'severity_scores': severity_scores,
            'all_emotions': list(detected_emotions.keys())
        }
    
    def detect_crisis(self, text: str) -> Dict[str, Any]:
        """Detect crisis situations requiring immediate intervention"""
        text_lower = text.lower()
        crisis_indicators = []
        
        for crisis_keyword in self.crisis_keywords:
            if crisis_keyword.lower() in text_lower:
                crisis_indicators.append(crisis_keyword)
        
        # Check for severe depression indicators
        severe_depression = any(
            keyword in text_lower 
            for keyword in self.emotion_keywords['depression']['severe']
        )
        
        is_crisis = len(crisis_indicators) > 0 or severe_depression
        
        return {
            'is_crisis': is_crisis,
            'crisis_indicators': crisis_indicators,
            'severity': 'high' if len(crisis_indicators) > 1 else 'moderate' if is_crisis else 'low'
        }
    
    def calculate_mental_health_score(self, text: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Calculate a mental health wellness score based on conversation"""
        sentiment = self.analyze_sentiment(text)
        emotion = self.detect_emotion(text)
        crisis = self.detect_crisis(text)
        
        # Base score from sentiment
        base_score = 50  # Neutral baseline
        
        # Adjust based on sentiment
        sentiment_adjustment = sentiment['compound_score'] * 25
        base_score += sentiment_adjustment
        
        # Adjust based on emotions
        for emotion_name, severity in emotion['detected_emotions'].items():
            if 'depression' in emotion_name:
                if severity == 'severe':
                    base_score -= 30
                elif severity == 'moderate':
                    base_score -= 15
                elif severity == 'mild':
                    base_score -= 5
            elif 'anxiety' in emotion_name:
                if severity == 'severe':
                    base_score -= 20
                elif severity == 'moderate':
                    base_score -= 10
                elif severity == 'mild':
                    base_score -= 3
            elif 'positive' in emotion_name:
                if severity == 'high':
                    base_score += 20
                elif severity == 'moderate':
                    base_score += 10
                elif severity == 'mild':
                    base_score += 5
        
        # Crisis adjustment
        if crisis['is_crisis']:
            base_score = min(base_score, 20)  # Cap at very low score
        
        # Ensure score is within bounds
        mental_health_score = max(0, min(100, base_score))
        
        # Determine risk level
        if mental_health_score < 30:
            risk_level = 'high'
        elif mental_health_score < 50:
            risk_level = 'moderate'
        elif mental_health_score < 70:
            risk_level = 'mild'
        else:
            risk_level = 'low'
        
        return {
            'mental_health_score': mental_health_score,
            'risk_level': risk_level,
            'sentiment_impact': sentiment_adjustment,
            'emotion_impact': base_score - 50 - sentiment_adjustment,
            'crisis_detected': crisis['is_crisis']
        }


class EnhancedAIChatService:
    """Enhanced AI Chat Service with advanced NLP and mental health support"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), '..', 'models', 'DialoGPT-medium'
        )
        self.question_flow = {}
        self.session_contexts = {}
        self.nlp_processor = MentalHealthNLP()
        
        # Response templates for different emotional states
        self.response_templates = {
            'crisis': {
                'immediate': [
                    "I'm very concerned about you right now. Your life has value and meaning.",
                    "I'm worried about what you're going through. You don't have to face this alone.",
                    "Thank you for sharing something so difficult with me. Your safety is my priority."
                ],
                'support': [
                    "Please reach out for immediate help. You can call emergency services (911) or a crisis helpline like 988 (Suicide & Crisis Lifeline).",
                    "There are people who want to help you through this. Crisis counselors are available 24/7 at 988.",
                    "Your life matters. Please consider calling 988 (Suicide & Crisis Lifeline) or going to your nearest emergency room."
                ]
            },
            'depression': {
                'severe': [
                    "I can hear the pain in your words, and I want you to know that what you're feeling is valid.",
                    "Depression can make everything feel hopeless, but these feelings can change with proper support.",
                    "You've taken a brave step by sharing this with me. Depression is treatable, and you don't have to suffer alone."
                ],
                'moderate': [
                    "I'm sorry you're going through such a difficult time. Depression can feel overwhelming.",
                    "Thank you for trusting me with your feelings. Many people experience depression, and there are effective ways to feel better.",
                    "What you're experiencing sounds really challenging. Have you been able to talk to anyone else about how you're feeling?"
                ],
                'mild': [
                    "I can sense that you're feeling down. It's completely normal to have low periods.",
                    "It sounds like you're going through a tough time. Sometimes talking about it can help.",
                    "I hear that you're not feeling your best. What's been weighing on your mind lately?"
                ]
            },
            'anxiety': {
                'severe': [
                    "It sounds like you're experiencing intense anxiety. That must feel overwhelming and exhausting.",
                    "Panic and anxiety can feel terrifying. You're safe right now, and these feelings will pass.",
                    "Severe anxiety is very real and very treatable. You don't have to endure this level of distress."
                ],
                'moderate': [
                    "Anxiety can make everything feel uncertain and worrying. I understand how draining that can be.",
                    "It sounds like worry has been taking up a lot of space in your mind. That's exhausting.",
                    "Many people struggle with anxiety. What situations tend to trigger these worried feelings for you?"
                ],
                'mild': [
                    "It's natural to feel concerned or uneasy sometimes. What's been on your mind?",
                    "A little anxiety is normal, but I want to make sure you're taking care of yourself.",
                    "I can sense some worry in what you're sharing. Would you like to talk about what's causing it?"
                ]
            },
            'positive': [
                "I'm so glad to hear you're feeling good! It's wonderful when we can appreciate positive moments.",
                "That's great to hear! What's been contributing to you feeling this way?",
                "It sounds like things are going well for you. I'd love to hear more about what's been positive.",
                "I'm happy you're in a good place right now. What's been helping you feel this way?"
            ],
            'neutral': [
                "I'm here to listen. How would you like to use our time together today?",
                "Thank you for sharing. What's been most on your mind lately?",
                "I appreciate you opening up. What would be most helpful to talk about?",
                "How have you been taking care of yourself recently?"
            ]
        }
        
        # Load conversation flow
        self._load_question_flow()
        
        logger.info("Enhanced AI Chat Service initialized with advanced NLP")
    
    def _load_question_flow(self):
        """Load the enhanced conversation flow"""
        flow_path = os.path.join(os.path.dirname(__file__), '..', 'api', 'question_flow.json')
        try:
            with open(flow_path, 'r', encoding='utf-8') as f:
                self.question_flow = json.load(f)
            logger.info(f"Loaded question flow with {len(self.question_flow.get('nodes', {}))} nodes")
        except Exception as e:
            logger.error(f"Failed to load question flow: {e}")
            # Create enhanced fallback
            self.question_flow = self._create_enhanced_fallback_flow()
    
    def _create_enhanced_fallback_flow(self) -> Dict:
        """Create an enhanced fallback conversation flow"""
        return {
            "nodes": {
                "greeting": {
                    "id": "greeting",
                    "questions": [
                        "Hello! I'm here to provide mental health support. How are you feeling today?",
                        "Hi there! I'm a mental health support assistant. What's on your mind?",
                        "Welcome! I'm here to listen and support you. How can I help today?"
                    ],
                    "keywords": ["hello", "hi", "hey"],
                    "next_nodes": ["mood_assessment"]
                },
                "mood_assessment": {
                    "id": "mood_assessment",
                    "questions": [
                        "Can you tell me more about your current emotional state?",
                        "How would you rate your mood on a scale from 1-10?",
                        "What emotions are you experiencing right now?"
                    ],
                    "keywords": ["mood", "feeling", "emotion"],
                    "next_nodes": ["specific_support"]
                },
                "specific_support": {
                    "id": "specific_support",
                    "questions": [
                        "What kind of support would be most helpful for you right now?",
                        "Would you like to talk about coping strategies?",
                        "How have you been taking care of your mental health lately?"
                    ],
                    "keywords": ["support", "help", "coping"],
                    "next_nodes": ["follow_up"]
                }
            }
        }
    
    def get_chat_response(self, user_input: str, session_id: str) -> str:
        """
        Generate an enhanced chat response with advanced NLP analysis
        
        Args:
            user_input: User's message
            session_id: Session identifier
            
        Returns:
            Personalized empathetic response
        """
        try:
            # Get or create session context
            context = self.get_session_context(session_id)
            
            # Perform comprehensive NLP analysis
            sentiment_analysis = self.nlp_processor.analyze_sentiment(user_input)
            emotion_analysis = self.nlp_processor.detect_emotion(user_input)
            crisis_analysis = self.nlp_processor.detect_crisis(user_input)
            mental_health_score = self.nlp_processor.calculate_mental_health_score(
                user_input, context.get('conversation_history', [])
            )
            
            # Update conversation history with analysis
            conversation_entry = {
                'user_input': user_input,
                'sentiment': sentiment_analysis,
                'emotion': emotion_analysis,
                'crisis': crisis_analysis,
                'mental_health_score': mental_health_score,
                'timestamp': None  # Can add timestamp if needed
            }
            
            context['conversation_history'].append(conversation_entry)
            context['turn_count'] += 1
            context['latest_mental_health_score'] = mental_health_score['mental_health_score']
            context['risk_level'] = mental_health_score['risk_level']
            
            # Generate personalized response
            response = self._generate_personalized_response(
                user_input, sentiment_analysis, emotion_analysis, 
                crisis_analysis, mental_health_score, context
            )
            
            # Update session context
            self.session_contexts[session_id] = context
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating enhanced chat response: {e}")
            return (
                "I'm here to support you, though I'm experiencing some technical difficulties right now. "
                "Your feelings and experiences are important. How can I best help you today?"
            )
    
    def _generate_personalized_response(self, user_input: str, sentiment: Dict, 
                                      emotion: Dict, crisis: Dict, 
                                      mental_health: Dict, context: Dict) -> str:
        """Generate a personalized response based on comprehensive analysis"""
        
        # Crisis response takes priority
        if crisis['is_crisis']:
            immediate_response = random.choice(self.response_templates['crisis']['immediate'])
            support_response = random.choice(self.response_templates['crisis']['support'])
            return f"{immediate_response} {support_response}"
        
        # Choose response based on primary emotion and severity
        primary_emotion = emotion['primary_emotion']
        detected_emotions = emotion['detected_emotions']
        
        response_parts = []
        
        # Empathetic acknowledgment based on emotion
        if 'depression' in primary_emotion and any('depression' in e for e in detected_emotions):
            severity = self._get_emotion_severity(detected_emotions, 'depression')
            if severity in self.response_templates['depression']:
                response_parts.append(random.choice(self.response_templates['depression'][severity]))
            else:
                response_parts.append(random.choice(self.response_templates['depression']['moderate']))
                
        elif 'anxiety' in primary_emotion and any('anxiety' in e for e in detected_emotions):
            severity = self._get_emotion_severity(detected_emotions, 'anxiety')
            if severity in self.response_templates['anxiety']:
                response_parts.append(random.choice(self.response_templates['anxiety'][severity]))
            else:
                response_parts.append(random.choice(self.response_templates['anxiety']['moderate']))
                
        elif 'positive' in primary_emotion:
            response_parts.append(random.choice(self.response_templates['positive']))
            
        else:
            response_parts.append(random.choice(self.response_templates['neutral']))
        
        # Add follow-up based on mental health score
        if mental_health['mental_health_score'] < 30:
            follow_ups = [
                "Have you been able to talk to a mental health professional about how you're feeling?",
                "It might be helpful to reach out to a counselor or therapist who can provide additional support.",
                "Would you like information about mental health resources in your area?"
            ]
            response_parts.append(random.choice(follow_ups))
            
        elif mental_health['mental_health_score'] < 50:
            follow_ups = [
                "What coping strategies have you tried that help you feel better?",
                "How is your support system? Do you have people you can talk to?",
                "What activities usually help improve your mood?"
            ]
            response_parts.append(random.choice(follow_ups))
            
        else:
            follow_ups = [
                "What would be most helpful to focus on in our conversation?",
                "Is there anything specific you'd like support with today?",
                "How can I best support you right now?"
            ]
            response_parts.append(random.choice(follow_ups))
        
        return " ".join(response_parts)
    
    def _get_emotion_severity(self, detected_emotions: Dict, emotion_type: str) -> str:
        """Get the severity level of a specific emotion type"""
        for emotion_key, severity in detected_emotions.items():
            if emotion_type in emotion_key:
                return severity
        return 'moderate'  # Default
    
    def get_session_context(self, session_id: str) -> Dict:
        """Get or create session context"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                'conversation_history': [],
                'turn_count': 0,
                'latest_mental_health_score': 50,
                'risk_level': 'low',
                'session_start': None
            }
        return self.session_contexts[session_id]
    
    def get_health_status(self) -> Dict:
        """Get enhanced service health status"""
        return {
            'service_type': 'enhanced_nlp_chatbot',
            'nlp_processor_loaded': True,
            'emotion_classifier_trained': hasattr(self.nlp_processor, 'emotion_classifier'),
            'question_flow_loaded': bool(self.question_flow),
            'active_sessions': len(self.session_contexts),
            'features': [
                'advanced_sentiment_analysis',
                'emotion_detection',
                'crisis_intervention',
                'mental_health_scoring',
                'personalized_responses'
            ]
        }


# Singleton instance
_enhanced_ai_chat_service = None

def get_enhanced_ai_chat_service() -> EnhancedAIChatService:
    """Get the singleton enhanced AI chat service instance"""
    global _enhanced_ai_chat_service
    if _enhanced_ai_chat_service is None:
        _enhanced_ai_chat_service = EnhancedAIChatService()
    return _enhanced_ai_chat_service

def get_chat_response(user_input: str, session_id: str) -> str:
    """Enhanced chat response function with advanced NLP"""
    service = get_enhanced_ai_chat_service()
    return service.get_chat_response(user_input, session_id)