#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service
from app.services.dataset_management_service import dataset_management_service
from app.services.dataset_validation_service import dataset_validation_service

async def test_validation():
    print("🧪 Testing validation fix...")
    
    # Initialize services
    await data_import_service.initialize()
    print("✅ Services initialized")
    
    # Test problem validation
    import time
    unique_id = int(time.time() % 1000)  # Generate unique ID
    test_data = {
        "domain": "stress",
        "category": "Work Stress", 
        "category_id": f"STR_{unique_id:03d}",
        "sub_category_id": f"STR_{unique_id:03d}_01",
        "problem_name": "Test Problem",
        "description": "Test description",
        "severity_level": 3
    }
    
    print("🔄 Testing validation...")
    result = await dataset_validation_service.validate_problem_category(test_data)
    print(f"✅ Validation result: {result.is_valid}")
    print(f"🔍 Errors: {result.errors}")
    print(f"🔍 Field errors: {result.field_errors}")
    
    if result.is_valid:
        print("🔄 Testing dataset management service create_item...")
        try:
            created_item = await dataset_management_service.create_item("problems", test_data)
            print(f"✅ Successfully created item: {created_item.get('id')}")
        except Exception as e:
            print(f"❌ Failed to create item: {str(e)}")
    
if __name__ == "__main__":
    asyncio.run(test_validation())