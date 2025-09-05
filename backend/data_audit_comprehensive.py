#!/usr/bin/env python3
"""
Comprehensive Data Audit Script for Mental Health Excel Files

This script performs detailed analysis of data quality issues across all Excel files
to identify problems before implementing the robust data pipeline.

Author: AI Assistant
Date: January 2025
Purpose: Phase 1 - Data Assessment & Preparation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveDataAuditor:
    """
    Comprehensive data quality auditor for mental health Excel files
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.excel_files = ["anxiety.xlsx", "stress.xlsx", "trauma.xlsx", "mentalhealthdata.xlsx"]
        self.expected_sheets = [
            "1.1 Problems",
            "1.2 Self Assessment", 
            "1.3 Suggestions",
            "1.4 Feedback Prompts",
            "1.5 Next Action After Feedback",
            "1.6 FineTuning Examples"
        ]
        self.audit_results = {}
        
    def audit_excel_files(self) -> Dict[str, Any]:
        """
        Main audit function that analyzes all Excel files
        """
        logger.info("Starting comprehensive data audit...")
        
        overall_results = {
            "audit_timestamp": datetime.now().isoformat(),
            "files_analyzed": [],
            "summary_statistics": {},
            "quality_issues": [],
            "recommendations": []
        }
        
        for file in self.excel_files:
            file_path = self.data_dir / file
            if file_path.exists():
                logger.info(f"Auditing {file}...")
                file_results = self.audit_single_file(file_path)
                overall_results["files_analyzed"].append(file)
                overall_results[file] = file_results
            else:
                logger.warning(f"File not found: {file}")
                overall_results["quality_issues"].append(f"Missing file: {file}")
        
        # Generate summary statistics
        overall_results["summary_statistics"] = self.generate_summary_statistics(overall_results)
        
        # Generate recommendations
        overall_results["recommendations"] = self.generate_recommendations(overall_results)
        
        # Save results
        self.save_audit_results(overall_results)
        
        return overall_results
    
    def audit_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Audit a single Excel file with all its sheets
        """
        file_results = {
            "file_name": file_path.name,
            "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            "sheets_found": [],
            "sheets_missing": [],
            "sheet_analysis": {},
            "overall_quality_score": 0.0
        }
        
        try:
            # Read all sheets
            sheets = pd.read_excel(file_path, sheet_name=None)
            file_results["sheets_found"] = list(sheets.keys())
            
            # Check for missing expected sheets
            file_results["sheets_missing"] = [
                sheet for sheet in self.expected_sheets 
                if sheet not in sheets.keys()
            ]
            
            # Analyze each sheet
            quality_scores = []
            for sheet_name, df in sheets.items():
                sheet_analysis = self.analyze_sheet(df, sheet_name, file_path.stem)
                file_results["sheet_analysis"][sheet_name] = sheet_analysis
                quality_scores.append(sheet_analysis["quality_score"])
            
            # Calculate overall quality score
            if quality_scores:
                file_results["overall_quality_score"] = np.mean(quality_scores)
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            file_results["error"] = str(e)
            file_results["overall_quality_score"] = 0.0
        
        return file_results
    
    def analyze_sheet(self, df: pd.DataFrame, sheet_name: str, domain: str) -> Dict[str, Any]:
        """
        Detailed analysis of a single sheet
        """
        analysis = {
            "sheet_name": sheet_name,
            "domain": domain,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "null_analysis": {},
            "duplicate_analysis": {},
            "data_quality_issues": [],
            "quality_score": 0.0
        }
        
        if len(df) == 0:
            analysis["quality_score"] = 0.0
            analysis["data_quality_issues"].append("Empty sheet")
            return analysis
        
        # Null value analysis
        analysis["null_analysis"] = self.analyze_null_values(df)
        
        # Duplicate analysis
        analysis["duplicate_analysis"] = self.analyze_duplicates(df)
        
        # Data type consistency
        analysis["type_consistency"] = self.analyze_type_consistency(df)
        
        # ID format analysis (if applicable)
        if any(col for col in df.columns if 'id' in col.lower()):
            analysis["id_format_analysis"] = self.analyze_id_formats(df)
        
        # Text encoding analysis
        analysis["encoding_analysis"] = self.analyze_text_encoding(df)
        
        # Calculate quality score
        analysis["quality_score"] = self.calculate_sheet_quality_score(analysis)
        
        return analysis
    
    def analyze_null_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze null values in the dataframe
        """
        null_counts = df.isnull().sum()
        null_percentages = (null_counts / len(df) * 100).round(2)
        
        return {
            "total_null_values": int(null_counts.sum()),
            "null_percentage_overall": round(null_counts.sum() / (len(df) * len(df.columns)) * 100, 2),
            "columns_with_nulls": null_counts[null_counts > 0].to_dict(),
            "null_percentages_by_column": null_percentages[null_percentages > 0].to_dict(),
            "completely_empty_columns": list(null_counts[null_counts == len(df)].index)
        }
    
    def analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze duplicate rows in the dataframe
        """
        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = round(duplicate_rows / len(df) * 100, 2) if len(df) > 0 else 0
        
        # Check for duplicate IDs if ID columns exist
        id_columns = [col for col in df.columns if 'id' in col.lower()]
        duplicate_ids = {}
        
        for id_col in id_columns:
            if id_col in df.columns:
                duplicates = df[df[id_col].duplicated(keep=False) & df[id_col].notna()]
                if len(duplicates) > 0:
                    duplicate_ids[id_col] = len(duplicates)
        
        return {
            "duplicate_rows_count": int(duplicate_rows),
            "duplicate_percentage": duplicate_percentage,
            "duplicate_ids": duplicate_ids
        }
    
    def analyze_type_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze data type consistency issues
        """
        type_issues = []
        
        for col in df.columns:
            # Check for mixed types in object columns
            if df[col].dtype == 'object':
                unique_types = set(type(val).__name__ for val in df[col].dropna())
                if len(unique_types) > 1:
                    type_issues.append({
                        "column": col,
                        "issue": "Mixed data types",
                        "types_found": list(unique_types)
                    })
        
        return {
            "type_consistency_issues": type_issues,
            "issues_count": len(type_issues)
        }
    
    def analyze_id_formats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze ID format consistency
        """
        id_columns = [col for col in df.columns if 'id' in col.lower()]
        id_analysis = {}
        
        for id_col in id_columns:
            if id_col in df.columns:
                non_null_ids = df[id_col].dropna().astype(str)
                
                # Check for consistent format patterns
                patterns = set()
                for id_val in non_null_ids:
                    # Simple pattern detection
                    if '_' in id_val:
                        parts = id_val.split('_')
                        pattern = '_'.join(['X' if part.isdigit() else 'A' for part in parts])
                        patterns.add(pattern)
                    else:
                        patterns.add('NO_UNDERSCORE')
                
                id_analysis[id_col] = {
                    "unique_count": len(non_null_ids.unique()),
                    "total_count": len(non_null_ids),
                    "patterns_found": list(patterns),
                    "pattern_consistency": len(patterns) == 1
                }
        
        return id_analysis
    
    def analyze_text_encoding(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze text encoding issues
        """
        text_columns = df.select_dtypes(include=['object']).columns
        encoding_issues = []
        
        for col in text_columns:
            for idx, value in df[col].dropna().items():
                if isinstance(value, str):
                    try:
                        # Check for common encoding issues
                        value.encode('utf-8')
                    except UnicodeEncodeError:
                        encoding_issues.append({
                            "column": col,
                            "row": idx,
                            "issue": "UTF-8 encoding error"
                        })
                        break  # Only report first issue per column
        
        return {
            "encoding_issues": encoding_issues,
            "issues_count": len(encoding_issues)
        }
    
    def calculate_sheet_quality_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall quality score for a sheet (0-1)
        """
        if analysis["row_count"] == 0:
            return 0.0
        
        score = 1.0
        
        # Penalize for null values
        null_penalty = analysis["null_analysis"]["null_percentage_overall"] / 100 * 0.4
        score -= null_penalty
        
        # Penalize for duplicates
        duplicate_penalty = analysis["duplicate_analysis"]["duplicate_percentage"] / 100 * 0.3
        score -= duplicate_penalty
        
        # Penalize for type inconsistencies
        type_penalty = analysis["type_consistency"]["issues_count"] / analysis["column_count"] * 0.2
        score -= type_penalty
        
        # Penalize for encoding issues
        encoding_penalty = analysis["encoding_analysis"]["issues_count"] / analysis["column_count"] * 0.1
        score -= encoding_penalty
        
        return max(0.0, score)
    
    def generate_summary_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate overall summary statistics
        """
        total_files = len(results["files_analyzed"])
        total_sheets = 0
        total_rows = 0
        quality_scores = []
        
        for file in results["files_analyzed"]:
            if file in results:
                file_data = results[file]
                if "sheet_analysis" in file_data:
                    total_sheets += len(file_data["sheet_analysis"])
                    for sheet_analysis in file_data["sheet_analysis"].values():
                        total_rows += sheet_analysis["row_count"]
                        quality_scores.append(sheet_analysis["quality_score"])
        
        return {
            "total_files_analyzed": total_files,
            "total_sheets_analyzed": total_sheets,
            "total_data_rows": total_rows,
            "average_quality_score": round(np.mean(quality_scores), 3) if quality_scores else 0.0,
            "min_quality_score": round(np.min(quality_scores), 3) if quality_scores else 0.0,
            "max_quality_score": round(np.max(quality_scores), 3) if quality_scores else 0.0
        }
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on audit results
        """
        recommendations = []
        
        # Check overall quality
        avg_quality = results["summary_statistics"].get("average_quality_score", 0)
        if avg_quality < 0.8:
            recommendations.append(f"Overall data quality is low ({avg_quality:.2f}). Implement comprehensive data cleaning.")
        
        # Check for missing files
        if len(results["files_analyzed"]) < 4:
            recommendations.append("Some expected Excel files are missing. Verify data source completeness.")
        
        # Analyze specific issues across files
        high_null_files = []
        duplicate_issues = []
        
        for file in results["files_analyzed"]:
            if file in results and "sheet_analysis" in results[file]:
                for sheet_name, sheet_data in results[file]["sheet_analysis"].items():
                    # Safely check for null analysis
                    if ("null_analysis" in sheet_data and 
                        "null_percentage_overall" in sheet_data["null_analysis"] and
                        sheet_data["null_analysis"]["null_percentage_overall"] > 20):
                        high_null_files.append(f"{file}:{sheet_name}")
                    
                    # Safely check for duplicate analysis
                    if ("duplicate_analysis" in sheet_data and 
                        "duplicate_percentage" in sheet_data["duplicate_analysis"] and
                        sheet_data["duplicate_analysis"]["duplicate_percentage"] > 5):
                        duplicate_issues.append(f"{file}:{sheet_name}")
        
        if high_null_files:
            recommendations.append(f"High null value percentages in: {', '.join(high_null_files[:3])}. Implement null handling strategies.")
        
        if duplicate_issues:
            recommendations.append(f"Duplicate data issues in: {', '.join(duplicate_issues[:3])}. Implement deduplication logic.")
        
        # Add standard recommendations
        recommendations.extend([
            "Implement ID format standardization (e.g., STR_04_08 pattern)",
            "Ensure UTF-8 encoding consistency for Indonesian text",
            "Create validation schemas for each sheet type",
            "Implement data quality monitoring for ongoing maintenance"
        ])
        
        return recommendations
    
    def save_audit_results(self, results: Dict[str, Any]) -> None:
        """
        Save audit results to JSON file
        """
        output_file = "data_audit_results.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Audit results saved to {output_file}")
            
            # Also create a summary report
            self.create_summary_report(results)
            
        except Exception as e:
            logger.error(f"Error saving audit results: {str(e)}")
    
    def create_summary_report(self, results: Dict[str, Any]) -> None:
        """
        Create a human-readable summary report
        """
        report_file = "data_audit_summary.md"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# Data Audit Summary Report\n\n")
                f.write(f"**Generated**: {results['audit_timestamp']}\n\n")
                
                # Summary statistics
                stats = results["summary_statistics"]
                f.write("## Summary Statistics\n\n")
                f.write(f"- **Files Analyzed**: {stats['total_files_analyzed']}\n")
                f.write(f"- **Sheets Analyzed**: {stats['total_sheets_analyzed']}\n")
                f.write(f"- **Total Data Rows**: {stats['total_data_rows']:,}\n")
                f.write(f"- **Average Quality Score**: {stats['average_quality_score']:.3f}\n")
                f.write(f"- **Quality Range**: {stats['min_quality_score']:.3f} - {stats['max_quality_score']:.3f}\n\n")
                
                # Quality issues
                if results["quality_issues"]:
                    f.write("## Quality Issues\n\n")
                    for issue in results["quality_issues"]:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                
                # Recommendations
                f.write("## Recommendations\n\n")
                for i, rec in enumerate(results["recommendations"], 1):
                    f.write(f"{i}. {rec}\n")
                
                # File-by-file breakdown
                f.write("\n## File Analysis Breakdown\n\n")
                for file in results["files_analyzed"]:
                    if file in results:
                        file_data = results[file]
                        f.write(f"### {file}\n\n")
                        f.write(f"- **Overall Quality Score**: {file_data['overall_quality_score']:.3f}\n")
                        f.write(f"- **File Size**: {file_data['file_size_mb']:.2f} MB\n")
                        f.write(f"- **Sheets Found**: {len(file_data['sheets_found'])}\n")
                        
                        if file_data["sheets_missing"]:
                            f.write(f"- **Missing Sheets**: {', '.join(file_data['sheets_missing'])}\n")
                        
                        f.write("\n")
            
            logger.info(f"Summary report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Error creating summary report: {str(e)}")

def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("Mental Health Data Pipeline - Comprehensive Data Audit")
    print("=" * 60)
    
    auditor = ComprehensiveDataAuditor()
    results = auditor.audit_excel_files()
    
    print("\n" + "=" * 60)
    print("AUDIT COMPLETED")
    print("=" * 60)
    
    # Display key findings
    stats = results["summary_statistics"]
    print(f"\nFiles Analyzed: {stats['total_files_analyzed']}")
    print(f"Total Data Rows: {stats['total_data_rows']:,}")
    print(f"Average Quality Score: {stats['average_quality_score']:.3f}")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(results["recommendations"][:3], 1):
        print(f"{i}. {rec}")
    
    print("\nDetailed results saved to:")
    print("- data_audit_results.json")
    print("- data_audit_summary.md")
    print("- data_audit.log")

if __name__ == "__main__":
    main()