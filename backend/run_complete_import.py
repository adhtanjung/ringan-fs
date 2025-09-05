#!/usr/bin/env python3
"""
Complete Dataset Import Script
Runs the full data import process to ensure all datasets are imported into MongoDB and vector database
"""

import asyncio
import logging
from app.services.data_import_service import DataImportService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run complete data import process"""
    try:
        logger.info("🚀 Starting complete dataset import process...")
        
        # Initialize data import service
        data_import_service = DataImportService()
        
        # Run complete import
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
        logger.info("🏁 Import process completed")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to run import process: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())