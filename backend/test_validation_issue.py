#!/usr/bin/env python3
"""
Test validation issue with problems import
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.dataset_validation_service import DatasetValidationService
from app.core.database import get_mongodb

async def test_validation_issue():
    """Test validation issue with problems import"""
    
    print("🧪 Testing validation issue...")
    
    # Initialize validation service
    validation_service = DatasetValidationService()
    await validation_service.initialize()
    
    print(f"🔍 Validation service DB initialized: {validation_service.db is not None}")
    
    # Test problem data (similar to what's being imported)
    test_problem = {
        "domain": "stress",
        "category": "Work Stress", 
        "category_id": "STR_04",
        "sub_category_id": "STR_04_01",
        "problem_name": "Workplace Pressure",
        "description": "High levels of stress due to workplace demands",
        "severity_level": 3
    }
    
    print(f"\n🔄 Testing problem validation...")
    print(f"Test data: {test_problem}")
    
    try:
        validation_result = await validation_service.validate_problem_category(test_problem)
        print(f"\n✅ Validation completed")
        print(f"🔍 Is valid: {validation_result.is_valid}")
        print(f"🔍 Errors: {validation_result.errors}")
        print(f"🔍 Field errors: {validation_result.field_errors}")
        if hasattr(validation_result, 'foreign_key_errors'):
            print(f"🔍 Foreign key errors: {validation_result.foreign_key_errors}")
            
        # Check if there are existing problems in the database
        if validation_service.db:
            existing_count = await validation_service.db.problems.count_documents({})
            print(f"\n🔍 Existing problems in database: {existing_count}")
            
            # Check for specific ID conflicts
            existing_category = await validation_service.db.problems.find_one({"category_id": "STR_04"})
            existing_sub_category = await validation_service.db.problems.find_one({"sub_category_id": "STR_04_01"})
            
            print(f"🔍 Existing category_id 'STR_04': {existing_category is not None}")
            print(f"🔍 Existing sub_category_id 'STR_04_01': {existing_sub_category is not None}")
            
            if existing_category:
                print(f"🔍 Existing category data: {existing_category}")
            if existing_sub_category:
                print(f"🔍 Existing sub-category data: {existing_sub_category}")
                
    except Exception as e:
        print(f"❌ Validation failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_validation_issue())