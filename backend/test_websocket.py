"""
Test WebSocket functionality
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket():
    """Test WebSocket connection"""
    try:
        # Test connection to the expected WebSocket URL
        uri = "ws://localhost:8000/api/v1/chat/ws/test_client_123"
        logger.info(f"Attempting to connect to {uri}")

        async with websockets.connect(uri) as websocket:
            logger.info("✅ WebSocket connected successfully!")

            # Send a test message
            test_message = "Hello from test client!"
            await websocket.send(test_message)
            logger.info(f"✅ Sent message: {test_message}")

            # Wait for response
            response = await websocket.recv()
            logger.info(f"✅ Received response: {response}")

            # Parse JSON response
            try:
                response_data = json.loads(response)
                logger.info(f"✅ Parsed JSON response: {response_data}")
            except json.JSONDecodeError:
                logger.warning("⚠️ Response is not valid JSON")

    except websockets.exceptions.ConnectionRefused:
        logger.error("❌ Connection refused - server not running or wrong port")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_websocket())









