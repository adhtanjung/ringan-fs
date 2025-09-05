import asyncio
import motor.motor_asyncio

async def clear_database():
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["mental_health_db"]
    
    collections = ["problems", "assessments", "suggestions", "feedback_prompts", "next_actions", "training_examples"]
    
    print("=== Clearing Database ===")
    
    for collection_name in collections:
        collection = db[collection_name]
        result = await collection.delete_many({})
        print(f"Cleared {collection_name}: {result.deleted_count} documents")
    
    print("\n=== Database cleared successfully ===")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_database())