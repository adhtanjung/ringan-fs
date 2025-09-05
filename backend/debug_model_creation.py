import asyncio
from app.models.dataset_models import ProblemCategoryModel
from app.services.dataset_management_service import dataset_management_service

async def test_model_creation():
    """Test model creation directly"""
    
    # Test data with proper ID format
    test_data = {
        "domain": "stress",
        "category": "Work Stress", 
        "category_id": "STR_01",
        "sub_category_id": "STR_01_01",
        "problem_name": "Test Problem",
        "description": "This is a test problem for validation",
        "severity_level": 3
    }
    
    try:
        print("🔍 Testing model creation...")
        
        # Test 1: Create model directly
        print("\n1. Testing direct model creation:")
        model = ProblemCategoryModel(**test_data)
        print(f"✅ Model created successfully: {model}")
        
        # Test 2: Check model_dump method
        print("\n2. Testing model serialization:")
        try:
            model_dict = model.model_dump(exclude={'id'})
            print(f"✅ model_dump() works: {model_dict}")
        except AttributeError:
            try:
                model_dict = model.dict(exclude={'id'})
                print(f"✅ dict() works: {model_dict}")
            except Exception as e:
                print(f"❌ Both model_dump() and dict() failed: {e}")
        
        # Test 3: Check dataset management service state
        print("\n3. Testing dataset management service:")
        print(f"Service db status: {dataset_management_service.db is not None}")
        print(f"Service db object: {dataset_management_service.db}")
        
        # Test 4: Try validation
        print("\n4. Testing validation:")
        from app.services.dataset_validation_service import dataset_validation_service
        validation_result = await dataset_validation_service.validate_problem_category(test_data)
        print(f"Validation result: {validation_result}")
        
        # Test 5: Try create_item if validation passes
        if validation_result.is_valid:
            print("\n5. Testing create_item:")
            try:
                result = await dataset_management_service.create_item("problems", test_data)
                print(f"✅ create_item successful: {result}")
            except Exception as e:
                print(f"❌ create_item failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Validation failed: {validation_result.errors}")
            print(f"Field errors: {validation_result.field_errors}")
        
    except Exception as e:
        print(f"🚨 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_model_creation())