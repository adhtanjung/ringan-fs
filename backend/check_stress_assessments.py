import pandas as pd

# Check all sub_category_ids in stress assessments
df = pd.read_excel('data/stress.xlsx', sheet_name='1.2 Self Assessment')
all_subcats = df['sub_category_id'].unique()
print('All unique sub_category_ids in stress assessments:')
for subcat in sorted(all_subcats):
    print(f'  {subcat}')

# Check if there are any that might transform to STR_04_08 or STR_04_26
print('\nLooking for patterns that might create STR_04_08 or STR_04_26...')
for subcat in all_subcats:
    if 'P004' in str(subcat):
        # Simulate transformation
        parts = str(subcat).split('-')
        if len(parts) == 2:
            main_num = parts[0].replace('P', '')
            sub_num = parts[1]
            transformed = f'STR_{main_num}_{sub_num.zfill(2)}'
            print(f'  {subcat} -> {transformed}')