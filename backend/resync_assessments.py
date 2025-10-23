#!/usr/bin/env python3
"""
Re-sync assessment data to vector database with scale information
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.vector_sync_service import VectorSyncService
from app.core.database import get_mongodb

async def resync_assessments():
    """Re-sync assessment data to vector database"""
    print("🔄 Starting assessment data re-sync...")

    try:
        # Initialize sync service
        sync_service = VectorSyncService()
        await sync_service.initialize()

        # Sync only assessments collection
        print("📝 Syncing assessments collection...")
        result = await sync_service.sync_collection('assessments', 'mental-health-assessments')

        print(f"✅ Sync result: {result}")

        if result.get('success'):
            print(f"🎉 Successfully synced {result.get('synced_count', 0)} assessment questions")
        else:
            print(f"❌ Sync failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error during sync: {str(e)}")
        return False

    return True

async def main():
    """Main function"""
    print("🚀 Assessment Data Re-sync Tool")
    print("=" * 50)

    success = await resync_assessments()

    if success:
        print("\n✅ Re-sync completed successfully!")
        print("You can now test the assessment workflow with scale questions.")
    else:
        print("\n❌ Re-sync failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())





















