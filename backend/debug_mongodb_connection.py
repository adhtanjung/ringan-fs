import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.database import get_mongodb, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mongodb_connection():
    """Test MongoDB connection directly"""
    print(f"Testing MongoDB connection with URL: {settings.MONGODB_URL}")
    
    try:
        # Test direct connection
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await client.admin.command('ping')
        print("✅ Direct MongoDB connection successful")
        
        # Test database access
        db = client.mental_health_db
        collections = await db.list_collection_names()
        print(f"✅ Database access successful. Collections: {collections}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Direct MongoDB connection failed: {str(e)}")
    
    # Test through init_db
    print("\nTesting through init_db()...")
    await init_db()
    
    mongodb_client = get_mongodb()
    if mongodb_client:
        print("✅ get_mongodb() returned a client")
        try:
            db = mongodb_client.mental_health_db
            collections = await db.list_collection_names()
            print(f"✅ Database access through get_mongodb() successful. Collections: {collections}")
        except Exception as e:
            print(f"❌ Database access through get_mongodb() failed: {str(e)}")
    else:
        print("❌ get_mongodb() returned None")

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())