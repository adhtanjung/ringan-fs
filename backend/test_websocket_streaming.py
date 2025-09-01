#!/usr/bin/env python3
"""
Test script for WebSocket streaming endpoint
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
                "message": "Halo, bagaimana kabarmu hari ini?",
                "session_data": {
                    "user_name": "Test User",
                    "session_id": "test_session_123"
                }
            }

            print(f"Sending message: {test_message}")
            await websocket.send(json.dumps(test_message))

            # Receive streaming response
            print("Receiving streaming response...")
            full_response = ""

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)

                    if data.get("type") == "chunk":
                        chunk = data.get("content", "")
                        full_response += chunk
                        print(f"Chunk: {chunk}", end="", flush=True)
                    elif data.get("type") == "complete":
                        print(f"\n✅ Stream completed!")
                        break
                    elif data.get("type") == "error":
                        print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
                        break
                    else:
                        print(f"\nUnknown message type: {data}")

                except asyncio.TimeoutError:
                    print("\n⏰ Timeout waiting for response")
                    break

            print(f"\n📝 Full response: {full_response}")

    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    print("🧪 Testing WebSocket Streaming Endpoint")
    print("=" * 50)

    success = asyncio.run(test_websocket_streaming())

    if success:
        print("\n✅ WebSocket streaming test completed successfully!")
    else:
        print("\n❌ WebSocket streaming test failed!")
        sys.exit(1)

