import pandas as pd

try:
    # Load the Excel file to see available sheets
    excel_file = pd.ExcelFile('data/anxiety.xlsx')
    print(f"📊 Available sheets in anxiety.xlsx: {excel_file.sheet_names}")
    
    # Load each sheet to see its structure
    for sheet_name in excel_file.sheet_names:
        try:
            df = pd.read_excel('data/anxiety.xlsx', sheet_name=sheet_name)
            print(f"\n📋 Sheet '{sheet_name}':")
            print(f"   - Shape: {df.shape}")
            print(f"   - Columns: {list(df.columns)}")
            if len(df) > 0:
                print(f"   - First row: {dict(df.iloc[0])}")
        except Exception as e:
            print(f"   - Error loading sheet '{sheet_name}': {e}")
            
except Exception as e:
    print(f"❌ Error loading file: {e}")