#!/usr/bin/env python3

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def check_database_status():
    print("🔍 Checking database status after import...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.mental_health_db
    
    # Check each collection
    collections = [
        'problems',
        'assessments', 
        'suggestions',
        'feedback_prompts',
        'next_actions',
        'training_examples'
    ]
    
    total_documents = 0
    
    for collection_name in collections:
        collection = db[collection_name]
        count = await collection.count_documents({})
        total_documents += count
        print(f"📊 {collection_name}: {count} documents")
        
        # Show a sample document if any exist
        if count > 0:
            sample = await collection.find_one()
            if sample:
                # Remove _id for cleaner output
                sample.pop('_id', None)
                print(f"   Sample: {str(sample)[:100]}...")
    
    print(f"\n📈 Total documents across all collections: {total_documents}")
    
    if total_documents > 0:
        print("✅ Database import was successful!")
        
        # Check for specific domains in problems collection
        problems_collection = db['problems']
        domains = ['stress', 'anxiety', 'trauma', 'mental_health']
        
        print("\n🏷️ Problems by domain:")
        for domain in domains:
            domain_count = await problems_collection.count_documents({'domain': domain})
            print(f"   {domain}: {domain_count} problems")
            
    else:
        print("❌ No data found in database - import may have failed")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(check_database_status())