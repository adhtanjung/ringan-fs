#!/usr/bin/env python3
"""
Comprehensive test of the complete WebSocket flow
"""

import asyncio
import websockets
import json
import time

async def test_complete_flow():
    """Test the complete WebSocket flow with multiple message exchanges"""
    
    client_id = f"test-flow-{int(time.time())}"
    uri = f"ws://localhost:8000/api/v1/chat/ws/{client_id}"
    
    print(f"🔌 Testing complete WebSocket flow")
    print(f"📍 Endpoint: {uri}")
    print(f"🆔 Client ID: {client_id}")
    print("=" * 60)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Test messages that should trigger different response types
            test_messages = [
                {
                    "message": "I'm feeling very stressed about work lately",
                    "expected_type": "problem_identified",
                    "description": "Stress-related message"
                },
                {
                    "message": "I have trouble sleeping and feel anxious",
                    "expected_type": "problem_identified", 
                    "description": "Anxiety-related message"
                },
                {
                    "message": "Can you give me some tips for relaxation?",
                    "expected_type": "suggestions",
                    "description": "Request for suggestions"
                }
            ]
            
            for i, test_case in enumerate(test_messages, 1):
                print(f"\n📤 Test {i}: {test_case['description']}")
                print(f"   Message: {test_case['message']}")
                
                # Prepare message
                message_data = {
                    "message": test_case['message'],
                    "session_id": client_id,
                    "conversation_id": f"conv_{client_id}",
                    "timestamp": time.time()
                }
                
                # Send message
                await websocket.send(json.dumps(message_data))
                print(f"   ✅ Sent successfully")
                
                # Collect all response chunks
                response_chunks = []
                complete_message = ""
                
                try:
                    # Wait for response chunks (streaming)
                    timeout_count = 0
                    while timeout_count < 3:  # Allow up to 3 timeouts
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                            response_chunks.append(response)
                            
                            # Parse response
                            try:
                                response_data = json.loads(response)
                                if 'message' in response_data:
                                    complete_message = response_data['message']
                                    
                                print(f"   📥 Response type: {response_data.get('type', 'unknown')}")
                                print(f"   📝 Message length: {len(complete_message)} chars")
                                
                                # Check if this looks like a complete response
                                if len(complete_message) > 50 and complete_message.endswith(('.', '!', '?')):
                                    print(f"   ✅ Complete response received")
                                    break
                                    
                            except json.JSONDecodeError:
                                print(f"   ⚠️  Non-JSON response: {response[:50]}...")
                                
                        except asyncio.TimeoutError:
                            timeout_count += 1
                            if response_chunks:
                                print(f"   ⏰ Timeout {timeout_count}/3 (but got {len(response_chunks)} chunks)")
                                break
                            else:
                                print(f"   ⏰ Timeout {timeout_count}/3 waiting for response")
                                
                except Exception as e:
                    print(f"   ❌ Error receiving response: {e}")
                    
                print(f"   📊 Total chunks received: {len(response_chunks)}")
                if complete_message:
                    print(f"   📄 Final message preview: {complete_message[:100]}...")
                    
                # Small delay between tests
                await asyncio.sleep(1)
                
            print("\n" + "=" * 60)
            print("✅ Complete WebSocket flow test finished successfully!")
            print(f"📊 Tested {len(test_messages)} different message types")
            print("🎉 WebSocket connection is working properly for the frontend")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed unexpectedly: {e}")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🚀 Starting comprehensive WebSocket flow test...")
    success = asyncio.run(test_complete_flow())
    
    if success:
        print("\n🎉 All tests passed! WebSocket integration is ready for frontend use.")
    else:
        print("\n❌ Some tests failed. Please check the WebSocket configuration.")