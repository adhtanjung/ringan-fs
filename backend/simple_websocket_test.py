import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/chat/ws/chat/stream"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Send a test message
            test_message = {
                "message": "Hello, I'm feeling anxious today",
                "session_data": {
                    "preferredLanguage": "en"
                }
            }
            
            print("📤 Sending test message...")
            await websocket.send(json.dumps(test_message))
            
            # Receive responses
            response_count = 0
            while response_count < 5:  # Limit to 5 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    print(f"📥 Response {response_count + 1}: {data.get('type', 'unknown')} - {data.get('content', '')[:100]}...")
                    
                    if data.get('type') == 'complete':
                        print("✅ Stream completed successfully!")
                        break
                        
                    response_count += 1
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break
                    
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing WebSocket Connection")
    print("=" * 40)
    
    success = asyncio.run(test_websocket())
    
    if success:
        print("\n✅ WebSocket test completed successfully!")
    else:
        print("\n❌ WebSocket test failed!")