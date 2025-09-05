import asyncio
import sys
import os
import pandas as pd

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service
from app.services.dataset_validation_service import DatasetValidationService

async def test_import_validation():
    print("🧪 Testing import validation with actual data...")
    
    # Initialize services
    await data_import_service.initialize()
    
    # Initialize validation service without database to avoid foreign key validation
    dataset_validation_service = DatasetValidationService()
    dataset_validation_service.db = None  # Disable database validation
    print("✅ Services initialized")
    
    # Load actual data from the anxiety domain
    try:
        df = pd.read_excel('data/anxiety.xlsx', sheet_name='1.1 Problems')
        print(f"📊 Loaded {len(df)} problems from anxiety domain")
        
        # Test with the first row
        if len(df) > 0:
            first_row = df.iloc[0]
            print(f"🔍 Testing first row: {dict(first_row)}")
            
            # Apply the same transformations as data_import_service
            original_category_id = str(first_row.get('category_id', ''))
            original_sub_category_id = str(first_row.get('sub_category_id', ''))
            
            # Transform IDs using the same logic as data_import_service
            domain = 'anxiety'
            import re
            
            # Transform category_id (P001 -> ANX_001)
            cat_match = re.search(r'(\d+)', original_category_id)
            if cat_match:
                cat_num = cat_match.group(1).zfill(3)
                transformed_category_id = f"ANX_{cat_num}"
            else:
                transformed_category_id = "ANX_001"
            
            # Transform sub_category_id (P001-1 -> ANX_001_01)
            sub_match = re.search(r'(\d+)[-_](\d+)', original_sub_category_id)
            if sub_match:
                main_num = sub_match.group(1)
                sub_num = sub_match.group(2).zfill(2)
                if len(main_num) <= 3:
                    main_num = main_num.zfill(3)
                transformed_sub_category_id = f"ANX_{main_num}_{sub_num}"
            else:
                transformed_sub_category_id = "ANX_001_01"
            
            print(f"🔍 ID Transformations:")
            print(f"  category_id: {original_category_id} -> {transformed_category_id}")
            print(f"  sub_category_id: {original_sub_category_id} -> {transformed_sub_category_id}")
            
            # Convert to the format expected by validation
            test_data = {
                'domain': domain,
                'category': first_row.get('category', ''),
                'category_id': transformed_category_id,
                'sub_category_id': transformed_sub_category_id,
                'problem_name': first_row.get('problem_name', ''),
                'description': first_row.get('description', ''),
                'severity_level': first_row.get('severity_level', 1)
            }
            
            print(f"🔍 Formatted data: {test_data}")
            
            # Test validation
            validation_result = await dataset_validation_service.validate_problem_category(test_data)
            print(f"🔍 is_valid: {validation_result.is_valid}")
            print(f"🔍 errors: {validation_result.errors}")
            print(f"🔍 warnings: {validation_result.warnings}")
            print(f"🔍 field_errors: {validation_result.field_errors}")
            
            if validation_result.is_valid:
                print("✅ Validation passed!")
            else:
                print("❌ Validation failed!")
                
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        
    # Also test assessment data
    try:
        # Check available sheet names first
        xl_file = pd.ExcelFile('data/anxiety.xlsx')
        assessment_sheet_name = None
        for sheet in xl_file.sheet_names:
            if 'assessment' in sheet.lower():
                assessment_sheet_name = sheet
                break
        
        if not assessment_sheet_name:
            print(f"📊 No assessment sheet found. Available sheets: {xl_file.sheet_names}")
        else:
            print(f"📊 Using assessment sheet: {assessment_sheet_name}")
            df_assess = pd.read_excel('data/anxiety.xlsx', sheet_name=assessment_sheet_name)
            print(f"📊 Loaded {len(df_assess)} assessments from anxiety domain")
            
            if len(df_assess) > 0:
                first_assess = df_assess.iloc[0]
                print(f"🔍 Testing first assessment: {dict(first_assess)}")
                
                # Apply the same sub_category_id transformation
                original_sub_category_id = str(first_assess.get('sub_category_id', ''))
                domain = 'anxiety'
                
                # Transform sub_category_id (P001-1 -> ANX_001_01)
                sub_match = re.search(r'(\d+)[-_](\d+)', original_sub_category_id)
                if sub_match:
                    main_num = sub_match.group(1)
                    sub_num = sub_match.group(2).zfill(2)
                    if len(main_num) <= 3:
                        main_num = main_num.zfill(3)
                    transformed_sub_category_id = f"ANX_{main_num}_{sub_num}"
                else:
                    transformed_sub_category_id = "ANX_001_01"
                
                print(f"🔍 Sub-category ID transformation: {original_sub_category_id} -> {transformed_sub_category_id}")
                
                # Clean response_type like data_import_service does
                raw_response_type = str(first_assess.get('response_type', 'text')).strip().lower()
                
                # Extract just the response type (e.g., 'scale (0–4)' -> 'scale')
                if 'scale' in raw_response_type:
                    cleaned_response_type = 'scale'
                elif 'multiple_choice' in raw_response_type:
                    cleaned_response_type = 'multiple_choice'
                elif 'text' in raw_response_type:
                    cleaned_response_type = 'text'
                elif 'boolean' in raw_response_type:
                    cleaned_response_type = 'boolean'
                else:
                    cleaned_response_type = 'text'  # Default
                
                print(f"🔍 Response type cleaning: '{raw_response_type}' -> '{cleaned_response_type}'")
                
                # Convert to the format expected by validation
                assess_data = {
                    'question_id': first_assess.get('question_id', ''),
                    'sub_category_id': transformed_sub_category_id,
                    'batch_id': first_assess.get('batch_id', ''),
                    'question_text': first_assess.get('question_text', ''),
                    'response_type': cleaned_response_type,
                    'scale_min': first_assess.get('scale_min', 0),
                    'scale_max': first_assess.get('scale_max', 4),
                    'domain': domain
                }
                
                print(f"🔍 Formatted assessment data: {assess_data}")
                
                # Test validation
                validation_result = await dataset_validation_service.validate_assessment_question(assess_data)
                print(f"🔍 Assessment is_valid: {validation_result.is_valid}")
                print(f"🔍 Assessment errors: {validation_result.errors}")
                print(f"🔍 Assessment warnings: {validation_result.warnings}")
                print(f"🔍 Assessment field_errors: {validation_result.field_errors}")
            
    except Exception as e:
        print(f"❌ Error loading assessment data: {e}")

if __name__ == "__main__":
    asyncio.run(test_import_validation())