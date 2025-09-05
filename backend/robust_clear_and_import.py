#!/usr/bin/env python3
import asyncio
import logging
from app.core.database import init_db, get_mongodb
from app.services.data_import_service import data_import_service
from app.services.dataset_management_service import dataset_management_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def robust_clear_collections():
    """Robustly clear all collections and drop indexes"""
    await init_db()
    db = get_mongodb().mental_health_db
    
    collections = ['problems', 'assessments', 'suggestions', 'feedback_prompts', 'next_actions', 'training_examples']
    
    for collection_name in collections:
        try:
            # Drop the entire collection (this removes all data and indexes)
            await db[collection_name].drop()
            logger.info(f"Dropped collection {collection_name}")
        except Exception as e:
            logger.warning(f"Failed to drop {collection_name}: {e}")
    
    # Wait a moment for the drops to complete
    await asyncio.sleep(1)
    
    # Recreate collections (they will be created automatically when data is inserted)
    for collection_name in collections:
        try:
            # Create the collection explicitly
            await db.create_collection(collection_name)
            logger.info(f"Created collection {collection_name}")
        except Exception as e:
            logger.warning(f"Collection {collection_name} might already exist: {e}")

async def main():
    logger.info("Starting robust clear and import...")
    
    # Robust clear collections
    await robust_clear_collections()
    
    # Initialize services (this will recreate indexes)
    await data_import_service.initialize()
    
    # Run import
    results = await data_import_service.import_all_data()
    
    logger.info(f"Import results: {results}")
    
    # Print summary
    for domain, result in results.items():
        if result.get('success'):
            logger.info(f"✅ {domain}: SUCCESS")
        else:
            logger.error(f"❌ {domain}: FAILED - {result.get('error', 'Unknown error')}")
    
if __name__ == "__main__":
    asyncio.run(main())