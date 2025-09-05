#!/usr/bin/env python3
"""
Script to consolidate imported data into the expected collection names
"""

import pymongo
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def consolidate_collections():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mental_health_db']
        
        # Mapping from imported collection patterns to target collections
        collection_mappings = {
            'problems': ['_1_1_Problems'],
            'assessments': ['_1_2_Self_Assessment'],
            'suggestions': ['_1_3_Suggestions'],
            'feedback_prompts': ['_1_4_Feedback_Prompts'],
            'next_actions': ['_1_5_Next_Action_After_Feedback'],
            'training_examples': ['_1_6_FineTuning_Examples']
        }
        
        # Get all existing collections
        existing_collections = db.list_collection_names()
        logger.info(f"Found {len(existing_collections)} existing collections")
        
        for target_collection, patterns in collection_mappings.items():
            logger.info(f"\nConsolidating data for {target_collection}...")
            
            # Find source collections that match the patterns
            source_collections = []
            for collection_name in existing_collections:
                for pattern in patterns:
                    if pattern in collection_name:
                        source_collections.append(collection_name)
                        break
            
            if not source_collections:
                logger.warning(f"No source collections found for {target_collection}")
                continue
                
            logger.info(f"Found source collections: {source_collections}")
            
            # Create or get target collection
            target_coll = db[target_collection]
            
            # Clear existing data in target collection
            result = target_coll.delete_many({})
            logger.info(f"Cleared {result.deleted_count} existing documents from {target_collection}")
            
            total_docs = 0
            # Copy data from source collections to target
            for source_name in source_collections:
                source_coll = db[source_name]
                docs = list(source_coll.find({}))
                
                if docs:
                    # Clean up documents (remove MongoDB-specific fields if needed)
                    cleaned_docs = []
                    for doc in docs:
                        # Keep the original _id or let MongoDB generate a new one
                        cleaned_docs.append(doc)
                    
                    # Insert into target collection
                    target_coll.insert_many(cleaned_docs)
                    total_docs += len(cleaned_docs)
                    logger.info(f"Copied {len(cleaned_docs)} documents from {source_name}")
            
            logger.info(f"Total documents in {target_collection}: {total_docs}")
        
        # Verify the consolidation
        logger.info("\n=== Consolidation Results ===")
        for target_collection in collection_mappings.keys():
            count = db[target_collection].count_documents({})
            logger.info(f"{target_collection}: {count} documents")
            
            # Show a sample document
            if count > 0:
                sample = db[target_collection].find_one()
                if sample and '_id' in sample:
                    del sample['_id']
                logger.info(f"  Sample: {sample}")
        
        client.close()
        logger.info("\nConsolidation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during consolidation: {e}")
        raise

if __name__ == "__main__":
    consolidate_collections()