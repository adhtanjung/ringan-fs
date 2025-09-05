import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from app.services.data_import_service import DataImportService
from app.services.data_cleaning_service import DataCleaningService
import asyncio

async def debug_id_transformation():
    print("🔍 Debugging ID transformation process...")
    
    # Initialize services
    import_service = DataImportService()
    cleaning_service = DataCleaningService()
    
    # Test with stress domain
    domain = 'stress'
    file_path = 'data/stress.xlsx'
    
    print(f"\n📊 Testing {domain} domain from {file_path}")
    
    # Read and clean problems sheet
    problems_df = pd.read_excel(file_path, sheet_name='1.1 Problems')
    print(f"\n🔍 Problems sheet - Original data:")
    print(f"Shape: {problems_df.shape}")
    print(f"Columns: {list(problems_df.columns)}")
    if len(problems_df) > 0:
        first_problem = problems_df.iloc[0]
        print(f"First row: {dict(first_problem)}")
        
        # Test transformation
        original_category_id = str(first_problem.get('category_id', ''))
        original_sub_category_id = str(first_problem.get('sub_category_id', ''))
        
        transformed_category_id = import_service._transform_category_id(original_category_id, domain)
        transformed_sub_category_id = import_service._transform_sub_category_id(original_sub_category_id, domain)
        
        print(f"\n🔄 Problems ID Transformations:")
        print(f"  category_id: {original_category_id} -> {transformed_category_id}")
        print(f"  sub_category_id: {original_sub_category_id} -> {transformed_sub_category_id}")
    
    # Read and clean assessments sheet
    assessments_df = pd.read_excel(file_path, sheet_name='1.2 Self Assessment')
    print(f"\n🔍 Assessments sheet - Original data:")
    print(f"Shape: {assessments_df.shape}")
    print(f"Columns: {list(assessments_df.columns)}")
    
    # Clean the assessments data
    cleaned_assessments = cleaning_service._clean_assessment_sheet(assessments_df)
    print(f"\n🧹 After cleaning:")
    print(f"Shape: {cleaned_assessments.shape}")
    print(f"Rows removed: {len(assessments_df) - len(cleaned_assessments)}")
    
    if len(cleaned_assessments) > 0:
        first_assessment = cleaned_assessments.iloc[0]
        print(f"First cleaned row: {dict(first_assessment)}")
        
        # Test transformation
        original_sub_category_id = str(first_assessment.get('sub_category_id', ''))
        original_question_id = str(first_assessment.get('question_id', ''))
        
        transformed_sub_category_id = import_service._transform_sub_category_id(original_sub_category_id, domain)
        transformed_question_id = import_service._transform_question_id(original_question_id, domain)
        
        print(f"\n🔄 Assessments ID Transformations:")
        print(f"  sub_category_id: {original_sub_category_id} -> {transformed_sub_category_id}")
        print(f"  question_id: {original_question_id} -> {transformed_question_id}")
    
    # Check for unique sub_category_ids in both sheets
    problems_sub_ids = set()
    if len(problems_df) > 0:
        for _, row in problems_df.iterrows():
            original_id = str(row.get('sub_category_id', ''))
            transformed_id = import_service._transform_sub_category_id(original_id, domain)
            problems_sub_ids.add(transformed_id)
    
    assessments_sub_ids = set()
    if len(cleaned_assessments) > 0:
        for _, row in cleaned_assessments.iterrows():
            original_id = str(row.get('sub_category_id', ''))
            transformed_id = import_service._transform_sub_category_id(original_id, domain)
            assessments_sub_ids.add(transformed_id)
    
    print(f"\n📋 Summary:")
    print(f"Problems sub_category_ids: {sorted(problems_sub_ids)}")
    print(f"Assessments sub_category_ids: {sorted(assessments_sub_ids)}")
    
    missing_ids = assessments_sub_ids - problems_sub_ids
    print(f"\n⚠️  Assessment IDs not in Problems: {len(missing_ids)}")
    if missing_ids:
        print(f"Missing IDs: {sorted(missing_ids)}")
    
    # Test the actual processing methods
    print(f"\n🧪 Testing actual processing methods...")
    try:
        problems = await import_service.process_problems_sheet(problems_df, domain)
        print(f"✅ Processed {len(problems)} problems successfully")
        if problems:
            print(f"First problem sub_category_id: {problems[0].sub_category_id}")
    except Exception as e:
        print(f"❌ Error processing problems: {e}")
    
    try:
        assessments = await import_service.process_assessments_sheet(cleaned_assessments, domain)
        print(f"✅ Processed {len(assessments)} assessments successfully")
        if assessments:
            print(f"First assessment sub_category_id: {assessments[0].sub_category_id}")
    except Exception as e:
        print(f"❌ Error processing assessments: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_id_transformation())