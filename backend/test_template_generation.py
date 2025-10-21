#!/usr/bin/env python3
"""
Quick test for template generation
"""

import asyncio
from app.services.import_export_service import import_export_service

async def test_template_generation():
    """Test template generation without full initialization"""
    print("🧪 Testing template generation...")

    try:
        # Test CSV template generation
        csv_template = import_export_service.generate_template('problems', 'csv')
        print(f"✅ CSV template generated: {len(csv_template)} bytes")

        # Test JSON template generation
        json_template = import_export_service.generate_template('problems', 'json')
        print(f"✅ JSON template generated: {len(json_template)} bytes")

        # Save templates for inspection
        with open('test_problems_template.csv', 'wb') as f:
            f.write(csv_template)
        print("💾 CSV template saved to test_problems_template.csv")

        with open('test_problems_template.json', 'wb') as f:
            f.write(json_template)
        print("💾 JSON template saved to test_problems_template.json")

        print("✅ Template generation test completed successfully!")

    except Exception as e:
        print(f"❌ Template generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_template_generation())








