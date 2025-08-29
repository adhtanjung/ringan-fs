#!/usr/bin/env python3
"""
Test script for stress domain import
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service

async def test_stress():
    """Test stress domain import"""

    print("🧪 Testing stress domain import...\n")

    try:
        # Initialize the service
        print("🔄 Initializing data import service...")
        success = await data_import_service.initialize()
        if not success:
            print("❌ Failed to initialize data import service")
            return

        print("✅ Data import service initialized")

        # Test stress domain
        print("\n🔄 Testing stress domain import...")
        result = await data_import_service.import_domain_data("stress")

        print(f"📊 Stress result: {result}")

        if result.get("success", False):
            print("✅ Stress domain import successful!")
            print(f"   - Problems: {result.get('problems', 0)}")
            print(f"   - Assessments: {result.get('assessments', 0)}")
            print(f"   - Suggestions: {result.get('suggestions', 0)}")
            print(f"   - Feedback: {result.get('feedback', 0)}")
            print(f"   - Training: {result.get('training', 0)}")
        else:
            print(f"❌ Stress domain import failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error during import test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stress())


