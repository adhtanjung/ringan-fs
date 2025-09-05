import asyncio
import logging
from app.core.database import init_db, get_mongodb
from app.services.dataset_management_service import dataset_management_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_global_service():
    """Test the global dataset_management_service instance"""
    print("=== Testing Global Service Instance ===")
    
    # Check initial state
    print(f"1. Initial service.db state: {dataset_management_service.db is not None}")
    print(f"   Service object ID: {id(dataset_management_service)}")
    
    # Initialize database
    print("\n2. Initializing database...")
    await init_db()
    mongodb_client = get_mongodb()
    print(f"   MongoDB client available: {mongodb_client is not None}")
    
    if mongodb_client:
        print(f"   MongoDB client type: {type(mongodb_client)}")
        try:
            # Test connection
            await mongodb_client.admin.command('ping')
            print("   ✅ MongoDB ping successful")
        except Exception as e:
            print(f"   ❌ MongoDB ping failed: {e}")
    
    # Initialize the service
    print("\n3. Initializing dataset management service...")
    await dataset_management_service.initialize()
    print(f"   After init, service.db state: {dataset_management_service.db is not None}")
    
    if dataset_management_service.db is not None:
        print(f"   Database name: {dataset_management_service.db.name}")
        print(f"   Database type: {type(dataset_management_service.db)}")
    
    # Test create_item
    print("\n4. Testing create_item...")
    test_data = {
        "domain": "stress",
        "category": "Work Stress", 
        "category_id": "STR_01",
        "sub_category_id": "STR_01_01",
        "problem_name": "Test Global Service Problem",
        "description": "Testing global service instance",
        "severity_level": 3
    }
    
    try:
        result = await dataset_management_service.create_item("problems", test_data)
        print(f"   ✅ create_item successful: {result.get('id')}")
    except Exception as e:
        print(f"   ❌ create_item failed: {e}")
        print(f"   Service db state during error: {dataset_management_service.db is not None}")

if __name__ == "__main__":
    asyncio.run(test_global_service())