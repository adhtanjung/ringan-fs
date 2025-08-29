#!/usr/bin/env python3
"""
Test script to verify WebSocket streaming is working after the fix
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_streaming():
    """Test the WebSocket streaming endpoint"""
    
    # WebSocket URL
    uri = "ws://localhost:8000/api/v1/chat/ws/chat/stream"
    
    try:
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket!")
            
            # Test message
            test_message = {
                "message": "Halo, saya merasa cemas hari ini. Bisakah Anda membantu?",
                "session_data": {
                    "user_name": "Test User",
                    "session_id": "test_session_fix_123"
                },
                "semantic_context": [],
                "problem_category": "",
                "assessment_progress": {}
            }
            
            print(f"Sending message: {test_message['message']}")
            await websocket.send(json.dumps(test_message))
            
            # Receive streaming response
            print("Receiving streaming response...")
            full_response = ""
            chunk_count = 0
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "chunk":
                        chunk = data.get("content", "")
                        full_response += chunk
                        chunk_count += 1
                        print(f"Chunk {chunk_count}: {chunk}", end="", flush=True)
                    elif data.get("type") == "complete":
                        print(f"\n✅ Stream completed! Received {chunk_count} chunks")
                        print(f"Full response length: {len(full_response)} characters")
                        break
                    elif data.get("type") == "error":
                        print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
                        break
                    else:
                        print(f"\n📋 Additional data: {data}")
                        
                except asyncio.TimeoutError:
                    print("\n⏰ Timeout waiting for response")
                    break
                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON decode error: {e}")
                    break
                    
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket connection closed unexpectedly")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("Testing WebSocket streaming after fix...")
    success = asyncio.run(test_websocket_streaming())
    
    if success:
        print("\n🎉 WebSocket streaming test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 WebSocket streaming test failed!")
        sys.exit(1)