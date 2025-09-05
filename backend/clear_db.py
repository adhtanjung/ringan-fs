import asyncio
from app.core.database import get_mongodb, init_db

async def clear_database():
    """Clear all collections in the database"""
    await init_db()
    client = get_mongodb()
    db = client.mental_health_db
    
    collections = [
        'problems', 'assessments', 'suggestions', 
        'feedback_prompts', 'training_examples', 'next_actions'
    ]
    
    for collection_name in collections:
        collection = db[collection_name]
        result = await collection.delete_many({})
        print(f"Cleared {result.deleted_count} documents from {collection_name}")
    
    print("✅ Database cleared successfully")

if __name__ == "__main__":
    asyncio.run(clear_database())