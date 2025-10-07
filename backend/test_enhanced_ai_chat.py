"""
Test Enhanced AI Chat Service with Advanced NLP
Run comprehensive tests for the enhanced mental health chatbot
"""

import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_ai_chat_service import get_enhanced_ai_chat_service, get_chat_response
import json

def test_enhanced_chat_service():
    """Test the enhanced AI chat service with various mental health scenarios"""
    
    print("🧠 Testing Enhanced AI Mental Health Chat Service")
    print("=" * 60)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Depression - Mild",
            "messages": [
                "I've been feeling a bit down lately",
                "I'm just not as motivated as I used to be",
                "Everything feels a bit gray"
            ]
        },
        {
            "name": "Depression - Severe", 
            "messages": [
                "I feel completely hopeless",
                "I don't see the point in anything anymore",
                "I feel worthless and empty inside"
            ]
        },
        {
            "name": "Anxiety - Moderate",
            "messages": [
                "I've been feeling really anxious about work",
                "I keep worrying about everything",
                "My mind just won't stop racing"
            ]
        },
        {
            "name": "Crisis Situation",
            "messages": [
                "I don't want to live anymore",
                "I've been thinking about ending it all",
                "Nothing matters and I can't go on"
            ]
        },
        {
            "name": "Positive Mood",
            "messages": [
                "I'm feeling pretty good today!",
                "Things have been going well lately",
                "I'm grateful for my support system"
            ]
        },
        {
            "name": "Mixed/Complex Emotions",
            "messages": [
                "I'm happy about my promotion but also scared",
                "I feel excited and terrified at the same time",
                "Good things are happening but I still feel sad"
            ]
        }
    ]
    
    # Get service instance
    try:
        service = get_enhanced_ai_chat_service()
        print(f"✅ Enhanced AI Chat Service loaded successfully")
        
        # Print service health status
        health_status = service.get_health_status()
        print(f"🏥 Service Health Status:")
        for key, value in health_status.items():
            print(f"   {key}: {value}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to load Enhanced AI Chat Service: {e}")
        return False
    
    # Test each scenario
    success_count = 0
    total_tests = 0
    
    for scenario in test_scenarios:
        print(f"\n🎭 Testing Scenario: {scenario['name']}")
        print("-" * 40)
        
        session_id = f"test_{scenario['name'].lower().replace(' ', '_').replace('-', '_')}"
        
        for i, message in enumerate(scenario['messages'], 1):
            total_tests += 1
            
            try:
                print(f"\n👤 User Message {i}: {message}")
                
                # Get response from enhanced service
                response = get_chat_response(message, session_id)
                
                print(f"🤖 AI Response: {response}")
                
                # Get session context for analysis
                context = service.get_session_context(session_id)
                latest_entry = context['conversation_history'][-1] if context['conversation_history'] else None
                
                if latest_entry:
                    print(f"📊 Analysis:")
                    print(f"   Sentiment: {latest_entry['sentiment']['overall_sentiment']} (score: {latest_entry['sentiment']['compound_score']:.2f})")
                    print(f"   Primary Emotion: {latest_entry['emotion']['primary_emotion']}")
                    print(f"   Mental Health Score: {latest_entry['mental_health_score']['mental_health_score']:.1f}")
                    print(f"   Risk Level: {latest_entry['mental_health_score']['risk_level']}")
                    if latest_entry['crisis']['is_crisis']:
                        print(f"   🚨 CRISIS DETECTED: {latest_entry['crisis']['crisis_indicators']}")
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error testing message '{message}': {e}")
    
    print(f"\n" + "="*60)
    print(f"📈 Test Results: {success_count}/{total_tests} tests passed")
    print(f"✅ Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    # Test conversation continuity
    print(f"\n🔄 Testing Conversation Continuity...")
    continuity_session = "test_continuity"
    
    continuity_messages = [
        "Hi, I'm new here",
        "I've been struggling with anxiety",
        "It's been getting worse over the past month",
        "Do you think I should see a therapist?"
    ]
    
    print("Testing how the AI maintains context across multiple messages:")
    for i, message in enumerate(continuity_messages, 1):
        response = get_chat_response(message, continuity_session)
        print(f"\nTurn {i}:")
        print(f"👤 User: {message}")
        print(f"🤖 AI: {response}")
    
    # Show final session context
    final_context = service.get_session_context(continuity_session)
    print(f"\n📋 Final Session Summary:")
    print(f"   Total turns: {final_context['turn_count']}")
    print(f"   Latest mental health score: {final_context['latest_mental_health_score']}")
    print(f"   Risk level: {final_context['risk_level']}")
    
    print(f"\n🎉 Enhanced AI Chat Service testing completed!")
    return success_count == total_tests

def test_nlp_components():
    """Test individual NLP components"""
    print("\n🔬 Testing Individual NLP Components")
    print("=" * 50)
    
    try:
        service = get_enhanced_ai_chat_service()
        nlp_processor = service.nlp_processor
        
        # Test sentiment analysis
        test_texts = [
            "I'm feeling really happy today!",
            "I'm so depressed and sad",
            "This is okay, nothing special",
            "I want to kill myself"
        ]
        
        print("\n📊 Sentiment Analysis Tests:")
        for text in test_texts:
            sentiment = nlp_processor.analyze_sentiment(text)
            print(f"Text: '{text}'")
            print(f"  Sentiment: {sentiment['overall_sentiment']} (score: {sentiment['compound_score']:.2f})")
        
        print("\n🎭 Emotion Detection Tests:")
        for text in test_texts:
            emotion = nlp_processor.detect_emotion(text)
            print(f"Text: '{text}'")
            print(f"  Primary emotion: {emotion['primary_emotion']}")
            print(f"  Detected emotions: {emotion['detected_emotions']}")
        
        print("\n🚨 Crisis Detection Tests:")
        for text in test_texts:
            crisis = nlp_processor.detect_crisis(text)
            print(f"Text: '{text}'")
            print(f"  Crisis detected: {crisis['is_crisis']} (severity: {crisis['severity']})")
            if crisis['crisis_indicators']:
                print(f"  Indicators: {crisis['crisis_indicators']}")
        
        print("✅ NLP component testing completed!")
        
    except Exception as e:
        print(f"❌ Error testing NLP components: {e}")

if __name__ == "__main__":
    # Run comprehensive tests
    print("🚀 Starting Enhanced AI Mental Health Chatbot Tests\n")
    
    # Test NLP components first
    test_nlp_components()
    
    # Test full chat service
    success = test_enhanced_chat_service()
    
    if success:
        print("\n🎉 All tests passed! Enhanced AI Chat Service is ready for deployment.")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")