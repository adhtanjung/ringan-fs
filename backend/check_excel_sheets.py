#!/usr/bin/env python3

import pandas as pd
import os

def main():
    excel_files = [
        'd:/AITek/ringan-landing/backend/data/anxiety.xlsx',
        'd:/AITek/ringan-landing/backend/data/stress.xlsx',
        'd:/AITek/ringan-landing/backend/data/trauma.xlsx',
        'd:/AITek/ringan-landing/backend/data/mentalhealthdata.xlsx'
    ]
    
    for excel_file in excel_files:
        if not os.path.exists(excel_file):
            print(f"❌ File not found: {excel_file}")
            continue
            
        print(f"\n📊 Checking {excel_file}:")
        
        try:
            # Get all sheet names
            xl_file = pd.ExcelFile(excel_file)
            sheet_names = xl_file.sheet_names
            print(f"📋 Available sheets: {sheet_names}")
            
            # Check if next actions sheet exists
            next_action_sheet = '1.5 Next Action After Feedback'
            if next_action_sheet in sheet_names:
                print(f"✅ Found '{next_action_sheet}' sheet")
                
                # Load the sheet and check its structure
                df = pd.read_excel(excel_file, sheet_name=next_action_sheet)
                print(f"📊 Sheet has {len(df)} rows and {len(df.columns)} columns")
                print(f"📋 Columns: {list(df.columns)}")
                
                # Show first few rows
                print(f"📄 First 3 rows:")
                for idx, row in df.head(3).iterrows():
                    print(f"  Row {idx}: {dict(row)}")
                    
            else:
                print(f"❌ Sheet '{next_action_sheet}' not found")
                
        except Exception as e:
            print(f"❌ Error reading {excel_file}: {str(e)}")

if __name__ == "__main__":
    main()