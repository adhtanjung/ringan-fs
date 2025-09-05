import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from app.services.data_cleaning_service import DataCleaningService

def examine_excel_data():
    try:
        # Initialize data cleaning service
        cleaning_service = DataCleaningService()
        
        # Check stress.xlsx
        print("📊 Examining stress.xlsx:")
        stress_file = 'data/stress.xlsx'
        
        # Read problems sheet
        problems_df = pd.read_excel(stress_file, sheet_name='1.1 Problems')
        print(f"\n🔍 Problems sheet - Shape: {problems_df.shape}")
        print(f"Columns: {list(problems_df.columns)}")
        if 'sub_category_id' in problems_df.columns:
            print(f"Sample sub_category_id values: {problems_df['sub_category_id'].head(10).tolist()}")
            print(f"Unique sub_category_id count: {problems_df['sub_category_id'].nunique()}")
        
        # Read assessments sheet
        assessments_df = pd.read_excel(stress_file, sheet_name='1.2 Self Assessment')
        print(f"\n🔍 Assessments sheet - Shape: {assessments_df.shape}")
        print(f"Columns: {list(assessments_df.columns)}")
        if 'sub_category_id' in assessments_df.columns:
            print(f"Sample sub_category_id values: {assessments_df['sub_category_id'].head(10).tolist()}")
            print(f"Unique sub_category_id count: {assessments_df['sub_category_id'].nunique()}")
            
            # Check for mismatched IDs
            problems_ids = set(problems_df['sub_category_id'].dropna())
            assessment_ids = set(assessments_df['sub_category_id'].dropna())
            missing_ids = assessment_ids - problems_ids
            
            print(f"\n⚠️  Assessment IDs not in Problems: {len(missing_ids)}")
            if missing_ids:
                print(f"Missing IDs (first 10): {list(missing_ids)[:10]}")
        
        # Clean the data and see what happens
        print(f"\n🧹 Cleaning assessments data...")
        cleaned_assessments = cleaning_service._clean_assessment_sheet(assessments_df)
        print(f"Original rows: {len(assessments_df)}, Cleaned rows: {len(cleaned_assessments)}")
        
        if 'sub_category_id' in cleaned_assessments.columns:
            print(f"Cleaned unique sub_category_id count: {cleaned_assessments['sub_category_id'].nunique()}")
            print(f"Sample cleaned sub_category_id values: {cleaned_assessments['sub_category_id'].head(10).tolist()}")
            
    except Exception as e:
        print(f"❌ Error examining Excel data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    examine_excel_data()