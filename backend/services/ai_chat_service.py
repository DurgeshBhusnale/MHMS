"""
✨ AI Chat Service — MHMS Chatbot Integration

Goal:
Build a lightweight empathetic AI + NLP chatbot service for a Mental Health Management System.
The bot should:
1. Use a pre-downloaded conversational model (e.g., microsoft/DialoGPT-small or medium).
2. Maintain smooth, friendly, and empathetic conversation flow.
3. Use a predefined question flow from `backend/api/question_flow.json`.
4. Detect simple moods using keywords (happy, sad, depressed, anxious, etc.).
5. Dynamically choose the next question node from JSON and generate a natural response.
6. Should run fully offline (no API keys, no external services).
7. Should expose one function: `get_chat_response(user_input: str, session_id: str)` returning chatbot reply text.

Architecture:
- Preload DialoGPT model and tokenizer globally using transformers.
- Load question_flow.json once when service starts.
- Maintain per-session conversation context (store last node in a dict).
- For each user input:
    -> detect keywords to choose next question node
    -> combine user input + empathy tone + next question into one prompt
    -> generate natural language reply from the model
- Use torch.no_grad() for inference.
- Optimize for low memory: only keep one model in memory.
"""

import json
import os
import re
import random
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Set environment variables for offline/PyTorch-only operation
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TRANSFORMERS_NO_FLAX"] = "1" 
os.environ["HF_HUB_OFFLINE"] = "1"

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
except ImportError:
    print("Warning: transformers/torch not available. AI chat will use fallback responses.")
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIChatService:
    """
    Empathetic AI Chat Service for Mental Health Support
    
    Features:
    - Conversational AI using DialoGPT
    - Mood detection through keyword analysis
    - Structured question flow for mental health support
    - Session-based conversation context
    - Empathetic response generation
    """
    
    def __init__(self, model_path: str = None, question_flow_path: str = None):
        """
        Initialize the AI Chat Service
        
        Args:
            model_path: Path to DialoGPT model directory
            question_flow_path: Path to question_flow.json file
        """
        self.model_path = model_path or "microsoft/DialoGPT-medium"
        self.question_flow_path = question_flow_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "api", "question_flow.json"
        )
        
        # Model components
        self.tokenizer = None
        self.model = None
        self.conversation_pipeline = None
        
        # Question flow and session data
        self.question_flow = {}
        self.session_contexts = {}  # session_id -> context dict
        self.model_loaded = False
        
        # Load question flow
        self._load_question_flow()
        
        # Initialize model (will be lazy-loaded)
        self._initialize_model()
    
    def _load_question_flow(self):
        """Load the question flow JSON configuration"""
        try:
            with open(self.question_flow_path, 'r', encoding='utf-8') as f:
                self.question_flow = json.load(f)
            logger.info(f"Loaded question flow with {len(self.question_flow.get('nodes', {}))} nodes")
        except Exception as e:
            logger.error(f"Failed to load question flow: {e}")
            # Create minimal fallback question flow
            self.question_flow = {
                "nodes": {
                    "greeting": {
                        "id": "greeting",
                        "questions": ["Hello! How are you feeling today?"],
                        "keywords": ["hello", "hi"],
                        "next_nodes": ["general_wellbeing"]
                    },
                    "general_wellbeing": {
                        "id": "general_wellbeing", 
                        "questions": ["I'm here to listen. Can you tell me more about how you're feeling?"],
                        "keywords": ["feeling", "mood"],
                        "next_nodes": ["general_wellbeing"]
                    }
                },
                "default_responses": {
                    "empathy": ["I understand how you're feeling."],
                    "encouragement": ["You're taking a positive step by talking about this."]
                },
                "mood_keywords": {
                    "depression": ["sad", "depressed", "down"],
                    "anxiety": ["anxious", "worried", "nervous"],
                    "positive": ["good", "fine", "happy"]
                }
            }
    
    def _initialize_model(self):
        """Initialize the DialoGPT model and tokenizer"""
        if torch is None:
            logger.warning("PyTorch not available. Using fallback responses.")
            return
            
        try:
            logger.info(f"Loading DialoGPT model from: {self.model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
                padding_side="left"
            )
            
            # Add pad token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                local_files_only=True,
                torch_dtype=torch.float32,
                device_map="cpu"
            )
            
            # Create conversation pipeline
            self.conversation_pipeline = pipeline(
                "conversational",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # CPU
                return_full_text=False,
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            self.model_loaded = True
            logger.info("DialoGPT model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load DialoGPT model: {e}")
            self.model_loaded = False
    
    def _detect_mood_and_keywords(self, user_input: str) -> Tuple[str, List[str]]:
        """
        Detect mood and extract keywords from user input
        
        Args:
            user_input: User's message
            
        Returns:
            Tuple of (detected_mood, matching_keywords)
        """
        user_input_lower = user_input.lower()
        mood_keywords = self.question_flow.get("mood_keywords", {})
        
        detected_mood = "neutral"
        matching_keywords = []
        
        # Check for mood keywords
        for mood, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    detected_mood = mood
                    matching_keywords.append(keyword)
        
        # Also extract general keywords for node selection
        all_nodes = self.question_flow.get("nodes", {})
        for node_id, node_data in all_nodes.items():
            node_keywords = node_data.get("keywords", [])
            for keyword in node_keywords:
                if keyword.lower() in user_input_lower:
                    matching_keywords.append(keyword)
        
        return detected_mood, matching_keywords
    
    def _select_next_node(self, current_node: str, detected_mood: str, keywords: List[str]) -> str:
        """
        Select the next conversation node based on context
        
        Args:
            current_node: Current conversation node ID
            detected_mood: Detected mood from user input
            keywords: Keywords found in user input
            
        Returns:
            Next node ID to use
        """
        nodes = self.question_flow.get("nodes", {})
        
        # Priority 1: Crisis detection
        if detected_mood == "crisis":
            return "crisis_support"
        
        # Priority 2: Specific mood-based routing
        mood_to_node = {
            "depression": "depression_check",
            "anxiety": "anxiety_check",
            "positive": "general_wellbeing"
        }
        
        if detected_mood in mood_to_node:
            target_node = mood_to_node[detected_mood]
            if target_node in nodes:
                return target_node
        
        # Priority 3: Keyword-based routing
        for keyword in keywords:
            for node_id, node_data in nodes.items():
                if keyword in node_data.get("keywords", []):
                    return node_id
        
        # Priority 4: Follow current node's next_nodes
        if current_node and current_node in nodes:
            next_nodes = nodes[current_node].get("next_nodes", [])
            if next_nodes:
                return random.choice(next_nodes)
        
        # Default: general wellbeing check
        return "general_wellbeing"
    
    def _get_empathetic_prefix(self) -> str:
        """Get a random empathetic response prefix"""
        empathy_responses = self.question_flow.get("default_responses", {}).get("empathy", [
            "I hear you, and I want you to know that your feelings are valid."
        ])
        return random.choice(empathy_responses)
    
    def _get_node_question(self, node_id: str) -> str:
        """Get a question from the specified node"""
        nodes = self.question_flow.get("nodes", {})
        node = nodes.get(node_id, {})
        questions = node.get("questions", ["How can I help you today?"])
        return random.choice(questions)
    
    def _generate_ai_response(self, conversation_context: str, session_id: str) -> str:
        """
        Generate AI response using DialoGPT
        
        Args:
            conversation_context: Context for the conversation
            session_id: Session identifier
            
        Returns:
            Generated response text
        """
        if not self.model_loaded or self.conversation_pipeline is None:
            # Fallback to template responses
            return "I'm here to listen and support you. Please tell me more about how you're feeling."
        
        try:
            with torch.no_grad():
                # Get or create conversation for this session
                if session_id not in self.session_contexts:
                    from transformers import Conversation
                    self.session_contexts[session_id] = {
                        "conversation": Conversation(),
                        "turn_count": 0
                    }
                
                session_context = self.session_contexts[session_id]
                conversation = session_context["conversation"]
                
                # Add user input to conversation
                conversation.add_user_input(conversation_context)
                
                # Generate response
                response = self.conversation_pipeline(conversation)
                
                # Extract the bot's response
                if hasattr(response, 'generated_responses') and response.generated_responses:
                    ai_response = response.generated_responses[-1]
                else:
                    ai_response = "I understand. Can you tell me more about that?"
                
                # Update session context
                session_context["turn_count"] += 1
                self.session_contexts[session_id] = session_context
                
                return ai_response
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm here to listen. Please share more about what's on your mind."
    
    def _create_conversation_context(self, user_input: str, empathy_prefix: str, 
                                   next_question: str) -> str:
        """
        Create a conversation context combining user input, empathy, and guidance
        
        Args:
            user_input: User's message
            empathy_prefix: Empathetic acknowledgment
            next_question: Follow-up question
            
        Returns:
            Combined conversation context
        """
        # Create a natural conversation flow
        context_parts = []
        
        if empathy_prefix:
            context_parts.append(empathy_prefix)
        
        # Add transition phrase
        transition_responses = self.question_flow.get("default_responses", {}).get("transition", [
            "Let's explore this a bit more."
        ])
        context_parts.append(random.choice(transition_responses))
        
        if next_question:
            context_parts.append(next_question)
        
        return " ".join(context_parts)
    
    def get_session_context(self, session_id: str) -> Dict:
        """Get current session context"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                "current_node": "greeting",
                "conversation_history": [],
                "detected_moods": [],
                "turn_count": 0
            }
        return self.session_contexts[session_id]
    
    def get_chat_response(self, user_input: str, session_id: str) -> str:
        """
        Main function to get chatbot response
        
        Args:
            user_input: User's message
            session_id: Session identifier for conversation context
            
        Returns:
            Chatbot's empathetic response
        """
        try:
            # Get session context
            context = self.get_session_context(session_id)
            
            # Detect mood and keywords
            detected_mood, keywords = self._detect_mood_and_keywords(user_input)
            
            # Update session context
            context["conversation_history"].append({
                "user_input": user_input,
                "detected_mood": detected_mood,
                "keywords": keywords
            })
            context["detected_moods"].append(detected_mood)
            context["turn_count"] += 1
            
            # Select next conversation node
            current_node = context.get("current_node", "greeting")
            next_node = self._select_next_node(current_node, detected_mood, keywords)
            context["current_node"] = next_node
            
            # Get empathetic prefix and next question
            empathy_prefix = self._get_empathetic_prefix()
            next_question = self._get_node_question(next_node)
            
            # Create conversation context
            conversation_context = self._create_conversation_context(
                user_input, empathy_prefix, next_question
            )
            
            # Generate AI response
            ai_response = self._generate_ai_response(conversation_context, session_id)
            
            # For crisis situations, prioritize safety
            if detected_mood == "crisis":
                crisis_response = (
                    "I'm very concerned about you right now. Your life has value and meaning. "
                    "If you're having thoughts of hurting yourself, please reach out for immediate help. "
                    "You can call emergency services (911) or a crisis helpline like 988 (Suicide & Crisis Lifeline). "
                    f"{ai_response}"
                )
                return crisis_response
            
            # Check for crisis keywords even if not detected as primary mood
            crisis_keywords = self.question_flow.get("mood_keywords", {}).get("crisis", [])
            user_input_lower = user_input.lower()
            for crisis_word in crisis_keywords:
                if crisis_word.lower() in user_input_lower:
                    crisis_response = (
                        "I'm very concerned about you right now. Your life has value and meaning. "
                        "If you're having thoughts of hurting yourself, please reach out for immediate help. "
                        "You can call emergency services (911) or a crisis helpline like 988 (Suicide & Crisis Lifeline). "
                        f"{ai_response}"
                    )
                    return crisis_response
            
            # Combine empathy with AI-generated response
            if empathy_prefix not in ai_response:
                final_response = f"{empathy_prefix} {ai_response}"
            else:
                final_response = ai_response
                
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return (
                "I'm here to listen and support you. Sometimes I have technical difficulties, "
                "but I want you to know that your feelings matter and there are people who care about you."
            )
    
    def get_health_status(self) -> Dict:
        """Get service health status"""
        return {
            "model_loaded": self.model_loaded,
            "model_path": self.model_path,
            "question_flow_loaded": bool(self.question_flow),
            "active_sessions": len(self.session_contexts),
            "torch_available": torch is not None
        }


# Global service instance
_ai_chat_service = None

def get_ai_chat_service() -> AIChatService:
    """Get or create the global AI chat service instance"""
    global _ai_chat_service
    if _ai_chat_service is None:
        # Try to get model path from config
        try:
            from config.settings import settings
            model_path = getattr(settings, 'CHATBOT_MODEL_DIR', None)
        except:
            model_path = None
            
        _ai_chat_service = AIChatService(model_path=model_path)
    return _ai_chat_service

def get_chat_response(user_input: str, session_id: str) -> str:
    """
    Main entry point for getting chat responses
    
    Args:
        user_input: User's message
        session_id: Session identifier
        
    Returns:
        Empathetic chatbot response
    """
    service = get_ai_chat_service()
    return service.get_chat_response(user_input, session_id)