#!/usr/bin/env python3
"""
Script to examine Excel data format and identify validation issues
"""

import pandas as pd
import numpy as np
from pathlib import Path

def examine_excel_data():
    """Examine Excel data to understand format issues"""

    data_dir = Path("data")
    excel_files = {
        "stress": "stress.xlsx",
        "anxiety": "anxiety.xlsx",
        "trauma": "trauma.xlsx",
        "general": "mentalhealthdata.xlsx"
    }

    print("🔍 Examining Excel data format issues...\n")

    for domain, filename in excel_files.items():
        file_path = data_dir / filename
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue

        print(f"📊 Examining {domain.upper()} data from {filename}")
        print("=" * 60)

        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)

            for sheet_name in excel_file.sheet_names:
                print(f"\n📋 Sheet: {sheet_name}")
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                print(f"   Rows: {len(df)}, Columns: {len(df.columns)}")

                # Check for response_type column (assessment questions)
                if 'response_type' in df.columns:
                    print(f"   📝 Response Type values found:")
                    response_types = df['response_type'].dropna().unique()
                    for rt in response_types:
                        print(f"      - '{rt}'")

                # Check for stage column (feedback prompts)
                if 'stage' in df.columns:
                    print(f"   🎭 Stage values found:")
                    stages = df['stage'].dropna().unique()
                    for stage in stages:
                        print(f"      - '{stage}'")

                # Check for next_action column (feedback prompts)
                if 'next_action' in df.columns:
                    print(f"   ⏭️ Next Action values found:")
                    next_actions = df['next_action'].dropna().unique()
                    for na in next_actions[:5]:  # Show first 5 to avoid spam
                        print(f"      - '{na}'")
                    if len(next_actions) > 5:
                        print(f"      ... and {len(next_actions) - 5} more")

                # Check for empty/NaN values
                nan_counts = df.isna().sum()
                if nan_counts.sum() > 0:
                    print(f"   ⚠️ NaN/Empty values:")
                    for col, count in nan_counts.items():
                        if count > 0:
                            print(f"      - {col}: {count} empty values")

                print()

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

        print("-" * 60)

if __name__ == "__main__":
    examine_excel_data()
