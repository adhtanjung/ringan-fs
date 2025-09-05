import pandas as pd
import sys
from pathlib import Path

def examine_excel_file(file_path):
    """Examine the structure of an Excel file"""
    try:
        print(f"\n=== Examining {file_path} ===")
        
        # Get all sheet names
        xl_file = pd.ExcelFile(file_path)
        print(f"Sheet names: {xl_file.sheet_names}")
        
        # Examine the problems sheet
        if '1.1 Problems' in xl_file.sheet_names:
            print("\n--- 1.1 Problems Sheet ---")
            df = pd.read_excel(file_path, sheet_name='1.1 Problems')
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print("\nFirst few rows:")
            print(df.head())
            
            # Check if severity_level column exists
            if 'severity_level' in df.columns:
                print("\nSeverity level values:")
                print(df['severity_level'].value_counts())
            else:
                print("\n❌ No 'severity_level' column found")
        
    except Exception as e:
        print(f"Error examining {file_path}: {e}")

if __name__ == "__main__":
    # Examine anxiety.xlsx
    examine_excel_file("data/anxiety.xlsx")
    
    # Also check stress.xlsx for comparison
    examine_excel_file("data/stress.xlsx")