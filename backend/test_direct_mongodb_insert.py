import asyncio
import motor.motor_asyncio
from datetime import datetime
from app.models.vector_models import ProblemCategory

async def test_direct_mongodb_insert():
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["mental_health_db"]
    
    print("=== Testing Direct MongoDB Insert ===")
    
    # Create a test problem
    test_problem = ProblemCategory(
        category_id="STR_04",
        sub_category_id="STR_04_01",
        category="Stress",
        problem_name="Test Problem",
        description="This is a test problem for debugging",
        domain="stress",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    print(f"Test problem data: {test_problem.model_dump()}")
    
    try:
        # Insert into problems collection
        problems_collection = db["problems"]
        result = await problems_collection.insert_one(test_problem.model_dump(exclude={'id'}))
        
        print(f"✅ Insert successful! Inserted ID: {result.inserted_id}")
        
        # Verify the insert
        inserted_item = await problems_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Retrieved item: {inserted_item}")
        
        # Check total count
        total_count = await problems_collection.count_documents({})
        print(f"Total problems in collection: {total_count}")
        
    except Exception as e:
        print(f"❌ Insert failed: {str(e)}")
        print(f"Error type: {type(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_direct_mongodb_insert())