#!/usr/bin/env python3
"""
Force Clear Database Script
Forces a complete database reset by dropping collections and recreating them
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.database import init_db, get_mongodb
from app.services.vector_service import vector_service
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def force_clear_database():
    """Force clear all database collections"""
    try:
        logger.info("🧹 Force clearing database...")
        
        # Initialize database connection
        await init_db()
        client = get_mongodb()
        db = client.mental_health_db
        
        # Get all collection names
        collection_names = await db.list_collection_names()
        logger.info(f"📋 Found collections: {collection_names}")
        
        # Drop all collections
        for collection_name in collection_names:
            try:
                await db[collection_name].drop()
                logger.info(f"🗑️  Dropped collection: {collection_name}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to drop {collection_name}: {str(e)}")
        
        # Clear vector database
        try:
            await vector_service.connect()
            
            # Get all vector collections
            collections_info = vector_service.client.get_collections()
            vector_collections = [col.name for col in collections_info.collections]
            logger.info(f"📋 Found vector collections: {vector_collections}")
            
            # Delete all vector collections
            for collection_name in vector_collections:
                try:
                    vector_service.client.delete_collection(collection_name)
                    logger.info(f"🗑️  Deleted vector collection: {collection_name}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to delete vector collection {collection_name}: {str(e)}")
            
            # Recreate vector collections
            await vector_service.create_collections()
            logger.info("✅ Vector collections recreated")
            
        except Exception as e:
            logger.error(f"❌ Failed to clear vector database: {str(e)}")
        
        logger.info("✅ Database force cleared successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to force clear database: {str(e)}")
        raise

async def main():
    """Main function"""
    try:
        await force_clear_database()
        logger.info("🏁 Force clear completed")
    except Exception as e:
        logger.error(f"❌ Force clear failed: {str(e)}")
        return False
    return True

if __name__ == "__main__":
    asyncio.run(main())