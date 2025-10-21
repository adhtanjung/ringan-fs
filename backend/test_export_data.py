#!/usr/bin/env python3
"""
Test script to check export functionality and database data
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.import_export_service import import_export_service
from app.services.dataset_management_service import dataset_management_service
from app.core.database import init_db

async def test_export_functionality():
    """Test export functionality and check database data"""
    print("🧪 Testing export functionality...")

    try:
        # Initialize database
        print("📊 Initializing database...")
        await init_db()

        # Initialize services
        print("🔧 Initializing services...")
        await dataset_management_service.initialize()
        await import_export_service.initialize()

        # Test data types
        data_types = ['problems', 'assessments', 'suggestions', 'feedback_prompts', 'next_actions', 'training_examples']

        for data_type in data_types:
            print(f"\n📋 Testing {data_type}...")

            # Check if data exists
            try:
                data = await dataset_management_service.get_all_data(data_type)
                print(f"   Found {len(data)} items in database")

                if data:
                    print(f"   Sample item keys: {list(data[0].keys()) if data else 'No data'}")

                    # Test export
                    try:
                        csv_export = await import_export_service.export_data(data_type, 'csv')
                        print(f"   CSV export: {len(csv_export)} bytes")

                        json_export = await import_export_service.export_data(data_type, 'json')
                        print(f"   JSON export: {len(json_export)} bytes")

                        # Save sample exports
                        with open(f'test_{data_type}_export.csv', 'wb') as f:
                            f.write(csv_export)
                        print(f"   💾 Saved CSV export to test_{data_type}_export.csv")

                        with open(f'test_{data_type}_export.json', 'wb') as f:
                            f.write(json_export)
                        print(f"   💾 Saved JSON export to test_{data_type}_export.json")

                    except Exception as e:
                        print(f"   ❌ Export failed: {str(e)}")

                else:
                    print(f"   ⚠️  No data found for {data_type}")

            except Exception as e:
                print(f"   ❌ Failed to get data for {data_type}: {str(e)}")

        print("\n✅ Export functionality test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_export_functionality())








