"""
Flask routes for AI Chat Service
Provides RESTful API endpoints for the empathetic mental health chatbot
"""

from flask import Blueprint, request, jsonify, session
from services.enhanced_ai_chat_service import get_chat_response, get_enhanced_ai_chat_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('ai_chat', __name__)

def _require_login():
    """Check if user is logged in"""
    return 'user_id' in session

@chat_bp.route('/message', methods=['POST'])
def send_message():
    """
    Send a message to the AI chatbot
    
    Expected JSON payload:
    {
        "message": "User's message text",
        "session_id": "optional session identifier"
    }
    
    Returns:
    {
        "response": "Chatbot's empathetic response",
        "session_id": "session identifier used",
        "status": "success"
    }
    """
    # Check authentication
    if not _require_login():
        return jsonify({
            "error": "Authentication required. Please log in to access the chat service.",
            "status": "unauthorized"
        }), 401
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                "error": "Message is required",
                "status": "error"
            }), 400
        
        # Get or generate session ID
        session_id = data.get('session_id')
        if not session_id:
            # Use user ID from session as default session ID
            user_id = session.get('user_id', 'anonymous')
            session_id = f"user_{user_id}"
        
        # Get chatbot response
        logger.info(f"Processing chat message for session {session_id}: {user_message[:50]}...")
        chatbot_response = get_chat_response(user_message, session_id)
        
        # Log successful response
        logger.info(f"Generated response for session {session_id}")
        
        return jsonify({
            "response": chatbot_response,
            "session_id": session_id,
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({
            "error": "An error occurred while processing your message. Please try again.",
            "status": "error"
        }), 500

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    Check the health status of the AI chat service
    
    Returns:
    {
        "status": "healthy" | "degraded" | "unhealthy",
        "model_loaded": boolean,
        "details": {...}
    }
    """
    try:
        service = get_enhanced_ai_chat_service()
        health_info = service.get_health_status()
        
        # Determine overall status
        if health_info.get('nlp_processor_loaded', False):
            status = "healthy"
        elif health_info.get('question_flow_loaded', False):
            status = "degraded"  # Can function with basic responses
        else:
            status = "unhealthy"
        
        return jsonify({
            "status": status,
            "nlp_processor_loaded": health_info.get('nlp_processor_loaded', False),
            "details": health_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking health status: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@chat_bp.route('/sessions/<session_id>/context', methods=['GET'])
def get_session_context(session_id: str):
    """
    Get conversation context for a specific session
    (Admin/debugging endpoint)
    
    Returns:
    {
        "session_id": "session identifier",
        "context": {...},
        "status": "success"
    }
    """
    # Check authentication
    if not _require_login():
        return jsonify({
            "error": "Authentication required",
            "status": "unauthorized"
        }), 401
    
    try:
        service = get_enhanced_ai_chat_service()
        context = service.get_session_context(session_id)
        
        # Remove sensitive conversation details for privacy
        safe_context = {
            "turn_count": context.get("turn_count", 0),
            "latest_mental_health_score": context.get("latest_mental_health_score", 50),
            "risk_level": context.get("risk_level", "low"),
            "conversation_summary": {
                "total_turns": len(context.get("conversation_history", [])),
                "recent_emotions": [
                    entry.get("emotion", {}).get("primary_emotion", "neutral") 
                    for entry in context.get("conversation_history", [])[-3:]
                ]
            }
        }
        
        return jsonify({
            "session_id": session_id,
            "context": safe_context,
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting session context: {e}")
        return jsonify({
            "error": "Error retrieving session context",
            "status": "error"
        }), 500

@chat_bp.route('/test', methods=['POST'])
def test_endpoint():
    """
    Test endpoint for development and debugging
    
    Expected JSON payload:
    {
        "message": "Test message",
        "session_id": "test_session"
    }
    """
    try:
        data = request.get_json() or {}
        message = data.get('message', 'Hello, how are you today?')
        session_id = data.get('session_id', 'test_session')
        
        response = get_chat_response(message, session_id)
        
        return jsonify({
            "test_input": message,
            "test_response": response,
            "test_session": session_id,
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500