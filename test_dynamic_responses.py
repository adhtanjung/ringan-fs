#!/usr/bin/env python3
"""
Test script to verify that the dynamic response system is working correctly
and all hardcoded responses have been replaced with LLM-generated ones.
"""

import asyncio
import json
import websockets
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_dynamic_responses():
    """Test the dynamic response system via WebSocket"""
    uri = "ws://localhost:8000/api/v1/chat/ws/test_dynamic_client_123"

    test_messages = [
        "Hello, I'm feeling anxious",
        "I've been having trouble sleeping",
        "Can you help me with stress management?",
        "I think I need an assessment",
        "What should I do about my depression?"
    ]

    print("🧪 Testing Dynamic Response System")
    print("=" * 50)

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")

            for i, message in enumerate(test_messages, 1):
                print(f"\n📤 Test {i}: Sending message: '{message}'")

                # Send message
                await websocket.send(json.dumps({
                    "message": message,
                    "session_id": "test_session_123",
                    "language": "en"
                }))

                # Receive response
                response_chunks = []
                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(response)

                        if data.get("type") == "chunk":
                            response_chunks.append(data.get("content", ""))
                        elif data.get("type") == "end":
                            break
                        elif data.get("type") == "error":
                            print(f"❌ Error: {data.get('content')}")
                            break

                    except asyncio.TimeoutError:
                        print("⏰ Timeout waiting for response")
                        break

                full_response = "".join(response_chunks)
                print(f"📥 Response: {full_response[:100]}{'...' if len(full_response) > 100 else ''}")

                # Check if response seems dynamic (not hardcoded)
                if len(full_response) > 20 and not any(hardcoded in full_response.lower() for hardcoded in [
                    "terima kasih telah menghubungi",
                    "maaf, saya tidak dapat",
                    "silakan coba lagi",
                    "thank you for contacting",
                    "sorry, i cannot",
                    "please try again"
                ]):
                    print("✅ Response appears to be dynamically generated")
                else:
                    print("⚠️  Response might be hardcoded or too short")

                await asyncio.sleep(1)  # Brief pause between tests

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure the backend server is running on port 8000")
        return False

    print("\n🎉 Dynamic response testing completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_dynamic_responses())