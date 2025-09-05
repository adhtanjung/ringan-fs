#!/usr/bin/env python3

import pandas as pd
import os

def main():
    excel_file = 'd:/AITek/ringan-landing/backend/data/anxiety.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ File not found: {excel_file}")
        return
        
    print(f"📊 Checking feedback data in {excel_file}:")
    
    try:
        # Check feedback prompts sheet
        feedback_sheet = '1.4 Feedback Prompts'
        df = pd.read_excel(excel_file, sheet_name=feedback_sheet)
        print(f"📊 Feedback sheet has {len(df)} rows and {len(df.columns)} columns")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Show first few rows
        print(f"📄 First 3 feedback rows:")
        for idx, row in df.head(3).iterrows():
            print(f"  Row {idx}: {dict(row)}")
            
        # Check unique next_action values
        if 'next_action' in df.columns:
            unique_actions = df['next_action'].unique()
            print(f"\n📋 Unique next_action values: {unique_actions}")
        elif 'next_action_id' in df.columns:
            unique_actions = df['next_action_id'].unique()
            print(f"\n📋 Unique next_action_id values: {unique_actions}")
            
    except Exception as e:
        print(f"❌ Error reading feedback data: {str(e)}")

if __name__ == "__main__":
    main()