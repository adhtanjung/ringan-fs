#!/usr/bin/env python3
"""
Clear All Collections and Reimport Script
Clears all MongoDB collections and vector database collections, then runs a fresh import
"""

import asyncio
import logging
from app.services.data_import_service import DataImportService
from app.services.dataset_management_service import dataset_management_service
from app.services.vector_service import vector_service
from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def clear_all_collections():
    """Clear all MongoDB and vector database collections"""
    try:
        logger.info("🧹 Starting to clear all collections...")
        
        # Initialize services
        await init_db()
        await dataset_management_service.initialize()
        await vector_service.connect()
        
        # Clear MongoDB collections
        collections_to_clear = [
            "problems", "assessments", "suggestions", 
            "feedback_prompts", "next_actions", "training_examples"
        ]
        
        for collection_name in collections_to_clear:
            try:
                collection = dataset_management_service.db[collection_name]
                result = await collection.delete_many({})
                logger.info(f"🗑️  Cleared {collection_name}: {result.deleted_count} documents")
            except Exception as e:
                logger.warning(f"⚠️  Failed to clear {collection_name}: {str(e)}")
        
        # Clear vector database collections
        vector_collections = [
            "mental-health-problems", 
            "mental-health-assessments", 
            "mental-health-suggestions"
        ]
        
        for collection_name in vector_collections:
            try:
                # Delete and recreate collection to clear all data
                try:
                    vector_service.client.delete_collection(collection_name)
                    logger.info(f"🗑️  Deleted vector collection: {collection_name}")
                except Exception:
                    logger.info(f"ℹ️  Vector collection {collection_name} didn't exist")
            except Exception as e:
                logger.warning(f"⚠️  Failed to clear vector collection {collection_name}: {str(e)}")
        
        # Recreate vector collections
        await vector_service.create_collections()
        logger.info("✅ All collections cleared and recreated")
        
    except Exception as e:
        logger.error(f"❌ Failed to clear collections: {str(e)}")
        raise

async def main():
    """Clear all collections and run fresh import"""
    try:
        logger.info("🚀 Starting clear and reimport process...")
        
        # Step 1: Clear all collections
        await clear_all_collections()
        
        # Step 2: Run fresh import
        logger.info("\n" + "="*60)
        logger.info("🔄 Starting fresh data import...")
        logger.info("="*60)
        
        data_import_service = DataImportService()
        results = await data_import_service.import_all_data()
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("📊 IMPORT RESULTS SUMMARY")
        logger.info("="*60)
        
        if results.get("success", False):
            total_stats = results.get("total", {})
            logger.info(f"✅ Overall Status: SUCCESS")
            logger.info(f"📋 Problems imported: {total_stats.get('problems', 0)}")
            logger.info(f"📝 Assessments imported: {total_stats.get('assessments', 0)}")
            logger.info(f"💡 Suggestions imported: {total_stats.get('suggestions', 0)}")
            logger.info(f"💬 Feedback prompts imported: {total_stats.get('feedback', 0)}")
            logger.info(f"🎯 Training examples imported: {total_stats.get('training', 0)}")
            
            # Show domain-specific results
            logger.info("\n📁 Domain-specific results:")
            for domain, result in results.items():
                if domain != "total":
                    status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
                    logger.info(f"  {domain}: {status}")
                    if not result.get("success", False) and "error" in result:
                        logger.error(f"    Error: {result['error']}")
        else:
            logger.error(f"❌ Overall Status: FAILED")
            if "error" in results:
                logger.error(f"Error: {results['error']}")
        
        logger.info("="*60)
        logger.info("🏁 Clear and reimport process completed")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to run clear and reimport process: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())