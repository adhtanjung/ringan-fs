import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.chat_service import ChatService
from app.services.vector_service import vector_service
from app.services.semantic_search_service import semantic_search_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_chat_service():
    """Direct test of ChatService with gemma3:4b"""
    try:
        # Initialize services
        logger.info("Connecting to vector service...")
        await vector_service.connect()
        
        logger.info("Initializing semantic search service...")
        await semantic_search_service.initialize()
        
        # Create chat service
        logger.info("Creating ChatService...")
        chat_service = ChatService()
        
        # Test message
        test_message = "I'm feeling very stressed and anxious lately"
        client_id = "test_client_123"
        
        logger.info(f"Testing message: '{test_message}'")
        logger.info(f"Client ID: {client_id}")
        
        # Process message
        response = await chat_service.process_message(
            message=test_message,
            client_id=client_id
        )
        
        logger.info("=== RESPONSE ===")
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            logger.info(f"Response content: {response.get('response', 'No response key')}")
            logger.info(f"Semantic context: {len(response.get('semantic_context', []))} items")
            logger.info(f"Assessment progress: {response.get('assessment_progress', 'None')}")
        else:
            logger.info(f"Full response: {response}")
            
        return response
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_chat_service())
    print("\n=== FINAL RESULT ===")
    print(result)