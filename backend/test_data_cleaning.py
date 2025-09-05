import pandas as pd
from app.services.data_cleaning_service import data_cleaning_service

# Test the data cleaning service with anxiety.xlsx
print("Testing data cleaning service with anxiety.xlsx...")

# Load the original data
df = pd.read_excel('data/anxiety.xlsx', sheet_name='1.2 Self Assessment')
print(f"Original rows: {len(df)}")
print(f"Original unique sub_category_ids: {len(df['sub_category_id'].unique())}")

# Clean the data
cleaned_df = data_cleaning_service.clean_dataframe(df, '1.2 Self Assessment')
print(f"Cleaned rows: {len(cleaned_df)}")
print(f"Cleaned unique sub_category_ids: {sorted(cleaned_df['sub_category_id'].unique())}")

# Show the difference
print(f"Rows removed: {len(df) - len(cleaned_df)}")