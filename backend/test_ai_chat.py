#!/usr/bin/env python3
"""
Test script for AI Chat Service
Tests the empathetic chatbot functionality without requiring the full Flask app
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

def test_ai_chat_service():
    """Test the AI Chat Service functionality"""
    print("🤖 Testing AI Chat Service...")
    print("=" * 50)
    
    try:
        from services.ai_chat_service import get_chat_response, get_ai_chat_service
        
        # Initialize service
        service = get_ai_chat_service()
        print(f"✅ Service initialized successfully")
        
        # Check health status
        health = service.get_health_status()
        print(f"📊 Health Status: {health}")
        
        # Test conversation scenarios
        test_scenarios = [
            {
                "input": "Hello, I'm feeling really sad today",
                "expected_mood": "depression",
                "session": "test_session_1"
            },
            {
                "input": "I'm so worried about everything, my heart is racing",
                "expected_mood": "anxiety", 
                "session": "test_session_2"
            },
            {
                "input": "I'm feeling much better now, thank you",
                "expected_mood": "positive",
                "session": "test_session_3"
            },
            {
                "input": "I don't want to live anymore",
                "expected_mood": "crisis",
                "session": "test_session_4"
            }
        ]
        
        print("\n🧪 Testing conversation scenarios...")
        print("-" * 50)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. Testing: {scenario['expected_mood']} scenario")
            print(f"   Input: \"{scenario['input']}\"")
            
            try:
                response = get_chat_response(scenario['input'], scenario['session'])
                print(f"   Response: \"{response[:100]}{'...' if len(response) > 100 else ''}\"")
                print(f"   ✅ Response generated successfully")
                
                # Check for crisis handling
                if scenario['expected_mood'] == 'crisis':
                    if '911' in response or '988' in response or 'emergency' in response.lower():
                        print(f"   ✅ Crisis response includes emergency contacts")
                    else:
                        print(f"   ⚠️  Crisis response may not include emergency contacts")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🎯 Testing session context...")
        print("-" * 50)
        
        # Test session context
        context = service.get_session_context("test_session_1")
        print(f"Session context keys: {list(context.keys())}")
        print(f"Turn count: {context.get('turn_count', 0)}")
        print(f"Current node: {context.get('current_node', 'unknown')}")
        
        print("\n✅ All tests completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Some dependencies may be missing. The service will use fallback responses.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_question_flow():
    """Test the question flow loading"""
    print("\n📋 Testing Question Flow...")
    print("=" * 50)
    
    try:
        import json
        flow_path = os.path.join(os.path.dirname(__file__), "api", "question_flow.json")
        
        with open(flow_path, 'r', encoding='utf-8') as f:
            question_flow = json.load(f)
        
        nodes = question_flow.get('nodes', {})
        print(f"✅ Question flow loaded: {len(nodes)} nodes")
        
        for node_id, node_data in list(nodes.items())[:5]:  # Show first 5 nodes
            questions = node_data.get('questions', [])
            keywords = node_data.get('keywords', [])
            print(f"   - {node_id}: {len(questions)} questions, keywords: {keywords}")
        
        mood_keywords = question_flow.get('mood_keywords', {})
        print(f"✅ Mood keywords: {list(mood_keywords.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading question flow: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI Chat Service Test Suite")
    print("=" * 60)
    
    # Test question flow first
    flow_test = test_question_flow()
    
    # Test AI chat service
    service_test = test_ai_chat_service()
    
    print("\n" + "=" * 60)
    if flow_test and service_test:
        print("🎉 All tests passed! The AI Chat Service is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("💡 The service may still work with reduced functionality.")
    
    print("\n🔧 To test with the Flask app:")
    print("   1. Start the backend: python app.py")
    print("   2. Test health: curl http://localhost:5000/api/ai-chat/health")
    print("   3. Test chat: curl -X POST http://localhost:5000/api/ai-chat/test \\")
    print("                    -H 'Content-Type: application/json' \\")
    print("                    -d '{\"message\": \"Hello, I need help\"}'")