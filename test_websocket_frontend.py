#!/usr/bin/env python3
"""
Test WebSocket connection to verify frontend configuration
"""

import asyncio
import websockets
import json

async def test_websocket_connection():
    # Test the WebSocket endpoint that the frontend should be using
    client_id = "test-frontend-client-123"
    uri = f"ws://localhost:8000/api/v1/chat/ws/{client_id}"
    
    print(f"Testing WebSocket connection to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            test_message = {
                "message": "Hello from frontend test",
                "session_id": client_id,
                "conversation_id": f"conv_{client_id}"
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent message: {test_message['message']}")
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📥 Received response: {response[:200]}...")
                
                # Try to parse the response
                try:
                    response_data = json.loads(response)
                    print(f"✅ Response parsed successfully")
                    print(f"   - Type: {response_data.get('type', 'unknown')}")
                    print(f"   - Has message: {'message' in response_data}")
                except json.JSONDecodeError:
                    print(f"⚠️  Response is not JSON: {response[:100]}...")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e}")
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    print("Testing WebSocket connection for frontend...")
    asyncio.run(test_websocket_connection())
    print("Test completed.")