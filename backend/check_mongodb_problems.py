import asyncio
import motor.motor_asyncio

async def check_mongodb_problems():
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["mental_health_db"]
    
    # Check problems collection
    problems_collection = db["problems"]
    
    print("=== MongoDB Problems Collection Analysis ===")
    
    # Count total documents
    total_count = await problems_collection.count_documents({})
    print(f"Total problems: {total_count}")
    
    if total_count > 0:
        # Get sample documents
        print("\n=== Sample Problems ===")
        async for problem in problems_collection.find().limit(10):
            print(f"ID: {problem.get('_id')}, Category: {problem.get('category_id')}, Sub-category: {problem.get('sub_category_id')}")
        
        # Check for specific sub_category_id patterns
        print("\n=== Sub-category ID Analysis ===")
        
        # Check for 2-digit format (STR_04_08)
        two_digit_count = await problems_collection.count_documents({"sub_category_id": {"$regex": "^[A-Z]{3}_\\d{2}_\\d{2}$"}})
        print(f"2-digit format (STR_04_08): {two_digit_count}")
        
        # Check for 3-digit format (STR_004_08)
        three_digit_count = await problems_collection.count_documents({"sub_category_id": {"$regex": "^[A-Z]{3}_\\d{3}_\\d{2}$"}})
        print(f"3-digit format (STR_004_08): {three_digit_count}")
        
        # Check for specific failing IDs
        failing_ids = ["STR_04_08", "ANX_01_09", "TRA_05_08"]
        for failing_id in failing_ids:
            exists = await problems_collection.count_documents({"sub_category_id": failing_id})
            print(f"'{failing_id}' exists: {exists > 0}")
        
        # Show all unique sub_category_id patterns
        print("\n=== All Sub-category IDs ===")
        pipeline = [
            {"$group": {"_id": "$sub_category_id", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        async for result in problems_collection.aggregate(pipeline):
            print(f"'{result['_id']}': {result['count']}")
    else:
        print("No problems found in MongoDB collection!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_mongodb_problems())