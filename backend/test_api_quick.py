import requests
import json

def test_enhanced_api():
    base_url = "http://localhost:5000/api/ai-chat"
    
    # Test health endpoint
    try:
        health_resp = requests.get(f"{base_url}/health")
        print("✅ Health Check Response:")
        print(json.dumps(health_resp.json(), indent=2))
        print()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test message endpoint with different emotions
    test_messages = [
        "I'm feeling very sad and depressed today",
        "I'm having anxiety about my job",
        "I want to kill myself",
        "I'm feeling great today!",
        "Hello, I'm new here"
    ]
    
    # Create a session with auth simulation
    session = requests.Session()
    
    for i, message in enumerate(test_messages, 1):
        try:
            payload = {
                "message": message,
                "session_id": f"test_session_{i}"
            }
            
            print(f"🗣️ Test Message {i}: {message}")
            
            # Note: This will fail without authentication, but we can see the response
            resp = session.post(f"{base_url}/message", json=payload)
            
            if resp.status_code == 401:
                print("   ⚠️ Authentication required (expected)")
            else:
                print(f"   ✅ Response: {resp.json()}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()

if __name__ == "__main__":
    test_enhanced_api()