import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    try:
        client = AsyncIOMotorClient('mongodb://admin:password123@localhost:27017/?authSource=admin')
        await client.admin.command('ping')
        print('✅ MongoDB connection successful with admin')
        
        # Test database access
        db = client.mental_health_chat
        collections = await db.list_collection_names()
        print(f'📊 Available collections: {collections}')
        
        client.close()
        return True
    except Exception as e:
        print(f'❌ MongoDB connection failed: {str(e)}')
        return False

if __name__ == '__main__':
    asyncio.run(test_connection())