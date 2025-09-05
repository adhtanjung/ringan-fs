#!/usr/bin/env python3
"""
Quick script to check document counts in MongoDB collections
"""

import pymongo
from pymongo import MongoClient

def check_collections():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mental_health_db']
        
        # Get all collection names
        collections = db.list_collection_names()
        print(f"Found {len(collections)} collections:")
        
        total_docs = 0
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            total_docs += count
            print(f"  {collection_name}: {count} documents")
            
            # Show a sample document if exists
            if count > 0:
                sample = collection.find_one()
                if sample:
                    # Remove _id for cleaner output
                    if '_id' in sample:
                        del sample['_id']
                    print(f"    Sample: {sample}")
                print()
        
        print(f"\nTotal documents across all collections: {total_docs}")
        
        if total_docs == 0:
            print("\n⚠️  WARNING: No data found in any collections!")
            print("This explains why the API is returning mock data.")
            print("You need to run the data import process.")
        
        client.close()
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on localhost:27017")

if __name__ == "__main__":
    check_collections()