#!/usr/bin/env python3
"""
Test script for importing all domains
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service

async def test_all_domains():
    """Test importing all domains"""

    print("🧪 Testing import of all domains...\n")

    try:
        # Initialize the service
        print("🔄 Initializing data import service...")
        success = await data_import_service.initialize()
        if not success:
            print("❌ Failed to initialize data import service")
            return

        print("✅ Data import service initialized")

        # Test all domains
        domains = ["stress", "anxiety", "trauma", "general"]

        for domain in domains:
            print(f"\n🔄 Testing {domain} domain import...")
            result = await data_import_service.import_domain_data(domain)

            print(f"📊 {domain.upper()} result: {result}")

            if result.get("success", False):
                print(f"✅ {domain} domain import successful!")
                print(f"   - Problems: {result.get('problems', 0)}")
                print(f"   - Assessments: {result.get('assessments', 0)}")
                print(f"   - Suggestions: {result.get('suggestions', 0)}")
                print(f"   - Feedback: {result.get('feedback', 0)}")
                print(f"   - Training: {result.get('training', 0)}")
            else:
                print(f"❌ {domain} domain import failed: {result.get('error', 'Unknown error')}")

        print("\n🎉 All domain tests completed!")

    except Exception as e:
        print(f"❌ Error during import test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_all_domains())


