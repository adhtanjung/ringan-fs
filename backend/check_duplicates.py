#!/usr/bin/env python3
import pandas as pd
import os

def check_all_duplicates():
    data_dir = 'd:/AITek/ringan-landing/backend/data'
    files = ['stress.xlsx', 'anxiety.xlsx', 'trauma.xlsx']
    
    sheets_to_check = {
        '1.1 Problems': 'category_id',
        '1.2 Self Assessment': 'question_id', 
        '1.3 Suggestions': 'suggestion_id',
        '1.4 Feedback Prompts': 'prompt_id',
        '1.5 Next Actions': 'action_id',
        '1.6 FineTuning Examples': 'example_id'
    }
    
    for file in files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f'\n=== {file} ===')
            
            for sheet_name, id_column in sheets_to_check.items():
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    if df.empty:
                        print(f'  {sheet_name}: Empty sheet')
                        continue
                        
                    if id_column not in df.columns:
                        print(f'  {sheet_name}: Column "{id_column}" not found')
                        continue
                        
                    total_rows = len(df)
                    unique_ids = df[id_column].nunique()
                    
                    print(f'  {sheet_name}:')
                    print(f'    Total rows: {total_rows}')
                    print(f'    Unique {id_column}s: {unique_ids}')
                    
                    if total_rows > unique_ids:
                        duplicates = df[id_column].value_counts()[df[id_column].value_counts() > 1]
                        print(f'    Duplicates: {duplicates.to_dict()}')
                        
                        # Show sample duplicate rows
                        for dup_id in list(duplicates.index)[:2]:  # Show first 2 duplicate IDs
                            dup_rows = df[df[id_column] == dup_id]
                            print(f'      {dup_id}: {len(dup_rows)} rows')
                    else:
                        print(f'    No duplicates')
                        
                except Exception as e:
                    print(f'  {sheet_name}: Error - {e}')
        else:
            print(f'  File not found: {file_path}')

if __name__ == '__main__':
    check_all_duplicates()