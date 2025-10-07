# ✨ AI Chat Service — MHMS Chatbot Integration

## Overview

The AI Chat Service provides an empathetic conversational AI chatbot designed specifically for mental health support within the MHMS (Mental Health Management System). The service combines structured psychological questioning with natural language generation to provide supportive, empathetic responses.

## Key Features

### 🤖 Conversational AI
- Uses DialoGPT (Microsoft) for natural language generation
- Maintains conversation context across multiple turns
- Generates empathetic, supportive responses

### 🧠 Mental Health Focus
- Structured question flow based on psychological principles
- Mood detection through keyword analysis
- Crisis intervention with emergency resource guidance
- Empathetic response templates

### 🔒 Privacy & Security
- Fully offline operation (no external API calls)
- Session-based conversation tracking
- Authentication required for access
- No sensitive data stored permanently

### 🎯 Intelligent Routing
- Keyword-based mood detection (depression, anxiety, crisis, positive)
- Dynamic conversation flow based on user responses
- Escalation paths for crisis situations
- Contextual follow-up questions

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Frontend Chat     │    │   Flask API Routes   │    │   AI Chat Service   │
│                     │────│                      │────│                     │
│ - Chat UI           │    │ /api/ai-chat/message │    │ - DialoGPT Model    │
│ - Session handling  │    │ /api/ai-chat/health  │    │ - Question Flow     │
│ - Error handling    │    │ /api/ai-chat/test    │    │ - Mood Detection    │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
                                      │
                           ┌──────────────────────┐
                           │  Question Flow JSON  │
                           │                      │
                           │ - Conversation nodes │
                           │ - Empathy templates  │
                           │ - Crisis responses   │
                           └──────────────────────┘
```

## Installation

### Prerequisites
```bash
pip install torch transformers flask flask-cors
```

### Model Setup
1. Download DialoGPT model to `backend/models/DialoGPT-medium/`
2. Ensure question_flow.json is in `backend/api/`
3. Configure model path in `backend/config/settings.py`

### Quick Start
```bash
# Test the service
cd backend
python test_ai_chat.py

# Start the full Flask application
python app.py
```

## API Endpoints

### `POST /api/ai-chat/message`
Send a message to the chatbot.

**Request:**
```json
{
    "message": "I'm feeling really anxious today",
    "session_id": "optional_session_id"
}
```

**Response:**
```json
{
    "response": "I hear you, and I want you to know that your feelings are valid. I can sense you're feeling anxious. Are you experiencing worry or fear about specific things?",
    "session_id": "user_12345",
    "status": "success"
}
```

### `GET /api/ai-chat/health`
Check service health status.

**Response:**
```json
{
    "status": "healthy",
    "model_loaded": true,
    "details": {
        "model_loaded": true,
        "model_path": "backend/models/DialoGPT-medium",
        "question_flow_loaded": true,
        "active_sessions": 3,
        "torch_available": true
    }
}
```

### `POST /api/ai-chat/test`
Test endpoint for development.

**Request:**
```json
{
    "message": "Hello, how are you?",
    "session_id": "test_session"
}
```

## Question Flow Structure

The conversation is guided by a structured JSON file (`question_flow.json`) that defines:

### Conversation Nodes
```json
{
    "greeting": {
        "id": "greeting",
        "questions": ["Hello! How are you feeling today?"],
        "keywords": ["hello", "hi", "start"],
        "next_nodes": ["mood_check", "general_wellbeing"]
    }
}
```

### Mood Detection
```json
{
    "mood_keywords": {
        "depression": ["sad", "depressed", "down", "hopeless"],
        "anxiety": ["anxious", "worried", "nervous", "panic"],
        "crisis": ["suicide", "kill", "death", "hurt myself"]
    }
}
```

### Response Templates
```json
{
    "default_responses": {
        "empathy": ["I hear you, and your feelings are valid."],
        "encouragement": ["You're taking a positive step."]
    }
}
```

## Session Management

Each conversation maintains context:
- **Current Node**: Where in the question flow
- **Conversation History**: Previous exchanges
- **Detected Moods**: Mood analysis over time
- **Turn Count**: Number of exchanges

## Crisis Handling

The service includes built-in crisis intervention:
- Detects crisis keywords automatically
- Provides immediate safety resources
- Includes emergency contact information
- Prioritizes user safety over conversation flow

**Example Crisis Response:**
```
"I'm very concerned about you right now. Your life has value and meaning. 
If you're having thoughts of hurting yourself, please reach out for immediate help. 
You can call emergency services (911) or a crisis helpline like 988 (Suicide & Crisis Lifeline)."
```

## Configuration

### Model Configuration
```python
# backend/config/settings.py
CHATBOT_MODEL_DIR = "backend/models/DialoGPT-medium"
MODELS_BASE_DIR = "backend/models"
```

### Service Parameters
```python
# In ai_chat_service.py
max_new_tokens=100      # Response length
temperature=0.7         # Response creativity
top_p=0.9              # Response diversity
```

## Development

### Testing
```bash
# Run comprehensive tests
python backend/test_ai_chat.py

# Test specific scenarios
curl -X POST http://localhost:5000/api/ai-chat/test \
  -H "Content-Type: application/json" \
  -d '{"message": "I need help"}'
```

### Adding New Conversation Nodes
1. Edit `question_flow.json`
2. Add node with questions, keywords, next_nodes
3. Test with `test_ai_chat.py`
4. Deploy changes

### Customizing Responses
- Modify empathy templates in `default_responses`
- Add new mood keywords for better detection
- Adjust conversation flow paths

## Monitoring

### Health Checks
- Model loading status
- Question flow validation
- Active session count
- Resource utilization

### Logging
- Conversation flows (anonymized)
- Error conditions
- Performance metrics
- Crisis interventions

## Security Considerations

### Data Privacy
- No conversation content stored permanently
- Session data cleared periodically
- No external API calls
- Local model inference only

### Access Control
- Authentication required
- Session-based access
- Role-based permissions available

## Production Deployment

### Resource Requirements
- RAM: 4GB minimum (for DialoGPT-medium)
- CPU: Multi-core recommended
- Storage: 2GB for model files

### Scaling Considerations
- Stateless design allows horizontal scaling
- Session data can be moved to Redis
- Model loading optimized for startup time

## Troubleshooting

### Common Issues

**Model not loading:**
```bash
# Check model path
ls backend/models/DialoGPT-medium/

# Verify dependencies
pip install torch transformers
```

**Service degraded:**
- Service runs with template responses if model fails
- Check health endpoint for detailed status
- Review logs for specific errors

**Memory issues:**
- Use DialoGPT-small for lower memory usage
- Implement model quantization
- Clear old sessions periodically

## Contributing

1. Test changes with `test_ai_chat.py`
2. Update question flow if adding new conversation paths
3. Document new features in this README
4. Ensure crisis handling remains functional

## License

Part of the MHMS (Mental Health Management System) project.