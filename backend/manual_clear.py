#!/usr/bin/env python3
import asyncio
import logging
from app.core.database import init_db, get_mongodb
from app.services.data_import_service import data_import_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_collections():
    """Manually clear all collections"""
    await init_db()
    db = get_mongodb().mental_health_db
    
    collections = ['problems', 'assessments', 'suggestions', 'feedback_prompts', 'next_actions', 'training_examples']
    
    for collection_name in collections:
        try:
            result = await db[collection_name].delete_many({})
            logger.info(f"Cleared {collection_name}: {result.deleted_count} documents")
        except Exception as e:
            logger.error(f"Failed to clear {collection_name}: {e}")

async def main():
    logger.info("Starting manual clear and import...")
    
    # Clear collections
    await clear_collections()
    
    # Run import
    await data_import_service.initialize()
    results = await data_import_service.import_all_data()
    
    logger.info(f"Import results: {results}")
    
if __name__ == "__main__":
    asyncio.run(main())