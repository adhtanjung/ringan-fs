import asyncio
import websockets
import json

async def test_websocket_connection():
    uri = "ws://localhost:8000/api/v1/chat/ws/test-client-456"
    
    try:
        print(f"Connecting to {uri}...")
        
        websocket = await asyncio.wait_for(
            websockets.connect(uri), 
            timeout=10.0
        )
        
        print("✅ Connected successfully!")
        
        # Send a simple test message
        test_message = "Hello, how are you?"
        
        print(f"📤 Sending: {test_message}")
        await websocket.send(test_message)
        
        # Wait for response
        print("📥 Waiting for response...")
        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
        
        print(f"✅ Received: {response[:200]}...")
        
        await websocket.close()
        return True
        
    except asyncio.TimeoutError:
        print("❌ Timeout error")
        return False
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 External WebSocket Test")
    print("=" * 40)
    
    success = asyncio.run(test_websocket_connection())
    
    if success:
        print("\n✅ WebSocket test passed!")
    else:
        print("\n❌ WebSocket test failed!")