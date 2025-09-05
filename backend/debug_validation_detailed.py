import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service
from app.services.dataset_validation_service import dataset_validation_service

async def test_validation_detailed():
    print("🧪 Testing detailed validation...")
    
    # Initialize services
    await data_import_service.initialize()
    print("✅ Services initialized")
    
    # Test problem validation
    import time
    unique_id = int(time.time() % 1000)
    test_data = {
        "domain": "stress",
        "category": "Work Stress", 
        "category_id": f"STR_{unique_id:03d}",
        "sub_category_id": f"STR_{unique_id:03d}_01",
        "problem_name": "Test Problem",
        "description": "Test description",
        "severity_level": 3
    }
    
    print(f"🔍 Testing with data: {test_data}")
    
    try:
        validation_result = await dataset_validation_service.validate_problem_category(test_data)
        print(f"✅ Validation completed")
        print(f"🔍 is_valid: {validation_result.is_valid}")
        print(f"🔍 errors: {validation_result.errors}")
        print(f"🔍 warnings: {validation_result.warnings}")
        print(f"🔍 field_errors: {validation_result.field_errors}")
        
        if not validation_result.is_valid:
            print(f"❌ Validation failed with errors: {validation_result.errors}")
            print(f"❌ Field errors: {validation_result.field_errors}")
        else:
            print("✅ Validation passed!")
            
    except Exception as e:
        print(f"❌ Validation exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_validation_detailed())