import asyncio
import websockets
import json

async def test_simple_websocket():
    uri = "ws://localhost:8000/api/v1/chat/ws/test-client-123"
    
    try:
        print(f"Connecting to {uri}...")
        
        # Use a shorter timeout for connection
        websocket = await asyncio.wait_for(
            websockets.connect(uri), 
            timeout=5.0
        )
        
        print("✅ Connected successfully!")
        
        # Send a very simple message
        test_message = {
            "message": "Hi"
        }
        
        print("📤 Sending simple message...")
        await websocket.send(json.dumps(test_message))
        
        # Wait for first response
        print("📥 Waiting for response...")
        response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
        
        print(f"✅ Received response: {response[:200]}...")
        
        await websocket.close()
        return True
        
    except asyncio.TimeoutError:
        print("❌ Connection timeout")
        return False
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple WebSocket Test")
    print("=" * 30)
    
    success = asyncio.run(test_simple_websocket())
    
    if success:
        print("\n✅ Test passed!")
    else:
        print("\n❌ Test failed!")