#!/usr/bin/env python3
"""
Debug validation issues
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service
from app.services.dataset_validation_service import dataset_validation_service

async def debug_validation():
    """Debug validation service"""
    
    print("🧪 Debugging validation service...\n")
    
    # Initialize services
    print("🔄 Initializing services...")
    success = await data_import_service.initialize()
    if not success:
        print("❌ Failed to initialize data import service")
        return
    
    print(f"✅ Services initialized")
    print(f"🔍 Validation service DB: {dataset_validation_service.db is not None}")
    
    # Test problem validation
    test_problem = {
        "domain": "stress",
        "category": "Work Stress", 
        "category_id": "STR_01",
        "sub_category_id": "STR_01_01",
        "problem_name": "Workplace Pressure",
        "description": "High levels of stress due to workplace demands",
        "severity_level": 3  # Fixed: using integer instead of string
    }
    
    print("\n🔄 Testing problem validation...")
    try:
        validation_result = await dataset_validation_service.validate_problem_category(test_problem)
        print(f"✅ Validation completed")
        print(f"🔍 Is valid: {validation_result.is_valid}")
        print(f"🔍 Errors: {validation_result.errors}")
        print(f"🔍 Field errors: {validation_result.field_errors}")
        if hasattr(validation_result, 'foreign_key_errors'):
            print(f"🔍 Foreign key errors: {validation_result.foreign_key_errors}")
    except Exception as e:
        print(f"❌ Validation failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_validation())