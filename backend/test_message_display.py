#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket_message_display():
    """Test WebSocket connection and message handling for UI display"""
    uri = "ws://localhost:8000/api/v1/chat/ws/test-ui-display-123"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Send a test message
            test_message = {
                "message": "I'm feeling anxious and need help.",
                "session_data": {
                    "emotion": None,
                    "mode": "help",
                    "sessionId": "test-ui-display-123",
                    "preferredLanguage": "en"
                },
                "semantic_context": [],
                "problem_category": "",
                "assessment_progress": {
                    "isActive": False,
                    "currentQuestion": None,
                    "completedQuestions": [],
                    "totalQuestions": 0,
                    "currentStep": 1,
                    "sessionId": "",
                    "responses": {}
                }
            }
            
            print(f"📤 Sending message: {json.dumps(test_message, indent=2)}")
            await websocket.send(json.dumps(test_message))
            print("📤 Message sent successfully")
            
            # Wait for response
            print("⏳ Waiting for response...")
            response = await websocket.recv()
            print(f"📨 Received response: {response}")
            
            # Parse and display response
            try:
                data = json.loads(response)
                print(f"📋 Parsed response data:")
                print(f"   Type: {data.get('type')}")
                print(f"   Message: {data.get('message', '')[:100]}...")
                print(f"   Stage: {data.get('stage')}")
                print(f"   Problems identified: {len(data.get('identified_problems', []))}")
                print(f"   Next stage available: {data.get('next_stage_available')}")
                
                if data.get('type') == 'problem_identified':
                    print("✅ Received 'problem_identified' response - this should now display in UI!")
                else:
                    print(f"⚠️ Unexpected response type: {data.get('type')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse response: {e}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing WebSocket message display handling...")
    result = asyncio.run(test_websocket_message_display())
    if result:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")