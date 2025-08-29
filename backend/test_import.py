#!/usr/bin/env python3
"""
Test script for data import
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service

async def test_import():
    """Test the data import service directly"""

    print("🧪 Testing data import service...\n")

    try:
        # Initialize the service
        print("🔄 Initializing data import service...")
        success = await data_import_service.initialize()
        if not success:
            print("❌ Failed to initialize data import service")
            return

        print("✅ Data import service initialized")

        # Test anxiety domain import
        print("\n🔄 Testing anxiety domain import...")
        result = await data_import_service.import_domain_data("anxiety")

        print(f"📊 Import result: {result}")

        if result.get("success", False):
            print("✅ Anxiety domain import successful!")
        else:
            print(f"❌ Anxiety domain import failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error during import test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_import())
