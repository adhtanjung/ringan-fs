import re

test_strings = ['scale (0–4)', 'scale (1–5)', 'Likert scale (1–5)', 'scale_1_5']

for s in test_strings:
    print(f'Testing: "{s}"')
    # Try the en-dash pattern
    match = re.search(r'\((\d+)[–-](\d+)\)', s.lower())
    if match:
        print(f'  Match found: min={match.group(1)}, max={match.group(2)}')
    else:
        print(f'  No match found')
    print()