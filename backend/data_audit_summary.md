# Data Audit Summary Report

**Generated**: 2025-09-03T01:20:42.220637

## Summary Statistics

- **Files Analyzed**: 4
- **Sheets Analyzed**: 28
- **Total Data Rows**: 2,990
- **Average Quality Score**: 0.667
- **Quality Range**: 0.000 - 1.000

## Recommendations

1. Overall data quality is low (0.67). Implement comprehensive data cleaning.
2. High null value percentages in: anxiety.xlsx:1.1 Problems, anxiety.xlsx:1.6 FineTuning Examples, stress.xlsx:1.4 Feedback Prompts. Implement null handling strategies.
3. Duplicate data issues in: anxiety.xlsx:1.1 Problems, anxiety.xlsx:1.2 Self Assessment, anxiety.xlsx:1.6 FineTuning Examples. Implement deduplication logic.
4. Implement ID format standardization (e.g., STR_04_08 pattern)
5. Ensure UTF-8 encoding consistency for Indonesian text
6. Create validation schemas for each sheet type
7. Implement data quality monitoring for ongoing maintenance

## File Analysis Breakdown

### anxiety.xlsx

- **Overall Quality Score**: 0.588
- **File Size**: 0.11 MB
- **Sheets Found**: 7

### stress.xlsx

- **Overall Quality Score**: 0.762
- **File Size**: 0.12 MB
- **Sheets Found**: 7

### trauma.xlsx

- **Overall Quality Score**: 0.599
- **File Size**: 0.12 MB
- **Sheets Found**: 7

### mentalhealthdata.xlsx

- **Overall Quality Score**: 0.718
- **File Size**: 0.10 MB
- **Sheets Found**: 7

