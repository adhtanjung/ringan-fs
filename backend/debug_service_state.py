import asyncio
import logging
from app.services.dataset_management_service import dataset_management_service
from app.core.database import get_mongodb, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_service_state():
    """Check the current state of dataset_management_service"""
    print("=== Dataset Management Service State Check ===")
    
    # Check initial state
    print(f"Initial service.db state: {dataset_management_service.db is not None}")
    print(f"Initial service.db value: {dataset_management_service.db}")
    
    # Check MongoDB client
    mongodb_client = get_mongodb()
    print(f"get_mongodb() returns: {mongodb_client is not None}")
    
    if mongodb_client is None:
        print("MongoDB client is None, initializing database...")
        await init_db()
        mongodb_client = get_mongodb()
        print(f"After init_db(), get_mongodb() returns: {mongodb_client is not None}")
    
    # Initialize the service
    print("\nInitializing dataset management service...")
    await dataset_management_service.initialize()
    
    print(f"After initialization, service.db state: {dataset_management_service.db is not None}")
    print(f"After initialization, service.db value: {dataset_management_service.db}")
    
    # Test create_item
    if dataset_management_service.db is not None:
        print("\n✅ Service is properly initialized")
        try:
            # Test data
            test_data = {
                "domain": "mental_health",
                "category_id": "test_debug_001",
                "sub_category_id": "test_debug_sub_001",
                "problem_name": "Debug Test Problem",
                "description": "A test problem for debugging",
                "category": "Debug Category"
            }
            
            result = await dataset_management_service.create_item("problems", test_data)
            print(f"✅ Successfully created test item: {result.get('id')}")
            
        except Exception as e:
            print(f"❌ Failed to create test item: {str(e)}")
    else:
        print("❌ Service is not properly initialized")

if __name__ == "__main__":
    asyncio.run(check_service_state())