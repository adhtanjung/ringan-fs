#!/usr/bin/env python3
"""
Data Validation Service
Validates data consistency between dataset management service and vector database
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd

from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service
from app.services.data_import_service import data_import_service
from app.services.data_cleaning_service import data_cleaning_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidationService:
    """Service for validating data consistency and integrity"""
    
    def __init__(self):
        self.collections = [
            "mental-health-problems",
            "mental-health-assessments", 
            "mental-health-suggestions",
            "mental-health-feedback",
            "mental-health-training",
            "mental_health_docs"
        ]
        
    async def validate_vector_database(self) -> Dict[str, Any]:
        """Validate vector database collections and data integrity"""
        try:
            logger.info("🔍 Starting vector database validation...")
            
            # Connect to vector service first
            connected = await vector_service.connect()
            if not connected:
                return {
                    "valid": False,
                    "error": "Failed to connect to vector database"
                }
            
            # Check vector service health
            health = await vector_service.health_check()
            logger.info(f"Vector service health check result: {health}")
            if not health.get('status') == 'healthy':
                return {
                    "valid": False,
                    "error": f"Vector database is not healthy. Health status: {health}",
                    "health": health
                }
            
            validation_results = {
                "valid": True,
                "collections": {},
                "total_points": 0,
                "empty_collections": [],
                "errors": []
            }
            
            # Get stats for all collections
            all_stats = await vector_service.get_collection_stats()
            
            # Validate each expected collection
            for collection_name in self.collections:
                try:
                    if collection_name in all_stats:
                        stats = all_stats[collection_name]
                        if "error" in stats:
                            validation_results["errors"].append(f"Error in collection {collection_name}: {stats['error']}")
                            validation_results["collections"][collection_name] = {
                                "points": 0,
                                "status": "error"
                            }
                            validation_results["empty_collections"].append(collection_name)
                        else:
                            point_count = stats.get('points_count', 0)
                            validation_results["collections"][collection_name] = {
                                "points": point_count,
                                "status": "healthy" if point_count > 0 else "empty"
                            }
                            validation_results["total_points"] += point_count
                            
                            if point_count == 0:
                                validation_results["empty_collections"].append(collection_name)
                    else:
                        validation_results["collections"][collection_name] = {
                            "points": 0,
                            "status": "missing"
                        }
                        validation_results["empty_collections"].append(collection_name)
                        validation_results["errors"].append(f"Collection {collection_name} not found")
                        
                except Exception as e:
                    validation_results["errors"].append(f"Error validating {collection_name}: {str(e)}")
                    validation_results["valid"] = False
            
            logger.info(f"✅ Vector database validation completed. Total points: {validation_results['total_points']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Vector database validation failed: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                "valid": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    async def validate_data_files(self) -> Dict[str, Any]:
        """Validate source data files and their structure"""
        try:
            logger.info("📁 Starting data files validation...")
            
            data_dir = Path("data")
            excel_files = {
                "stress": "stress.xlsx",
                "anxiety": "anxiety.xlsx", 
                "trauma": "trauma.xlsx",
                "mental_health": "mentalhealthdata.xlsx"
            }
            
            validation_results = {
                "valid": True,
                "files": {},
                "errors": []
            }
            
            for domain, filename in excel_files.items():
                file_path = data_dir / filename
                
                if not file_path.exists():
                    validation_results["errors"].append(f"File not found: {filename}")
                    validation_results["valid"] = False
                    continue
                
                try:
                    # Read and validate Excel file structure
                    sheets = data_import_service.read_excel_file(file_path)
                    
                    file_stats = {
                        "exists": True,
                        "sheets": {},
                        "total_rows": 0
                    }
                    
                    expected_sheets = [
                        "1.1 Problems",
                        "1.2 Self Assessment", 
                        "1.3 Suggestions",
                        "1.4 Feedback Prompts",
                        "1.6 FineTuning Examples"
                    ]
                    
                    for sheet_name in expected_sheets:
                        if sheet_name in sheets:
                            df = sheets[sheet_name]
                            cleaned_df = data_cleaning_service.clean_dataframe(df, sheet_name)
                            validation_stats = data_cleaning_service.validate_cleaned_data(cleaned_df, sheet_name)
                            
                            file_stats["sheets"][sheet_name] = {
                                "rows": len(cleaned_df),
                                "columns": len(cleaned_df.columns) if not cleaned_df.empty else 0,
                                "valid": validation_stats["valid"],
                                "errors": validation_stats.get("errors", [])
                            }
                            file_stats["total_rows"] += len(cleaned_df)
                        else:
                            file_stats["sheets"][sheet_name] = {
                                "rows": 0,
                                "columns": 0,
                                "valid": False,
                                "errors": ["Sheet not found"]
                            }
                    
                    validation_results["files"][domain] = file_stats
                    
                except Exception as e:
                    validation_results["errors"].append(f"Error reading {filename}: {str(e)}")
                    validation_results["valid"] = False
            
            logger.info("✅ Data files validation completed")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Data files validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def validate_data_consistency(self) -> Dict[str, Any]:
        """Validate consistency between source data and vector database"""
        try:
            logger.info("🔄 Starting data consistency validation...")
            
            # Get validation results for both sources
            vector_validation = await self.validate_vector_database()
            files_validation = await self.validate_data_files()
            
            consistency_results = {
                "valid": True,
                "vector_db": vector_validation,
                "source_files": files_validation,
                "consistency_checks": {},
                "recommendations": []
            }
            
            # Check if vector database has data when source files exist
            if files_validation["valid"] and vector_validation["valid"]:
                total_vector_points = vector_validation["total_points"]
                
                if total_vector_points == 0:
                    consistency_results["recommendations"].append(
                        "Vector database is empty but source files contain data. Run data import."
                    )
                
                # Check for empty collections that should have data
                empty_collections = vector_validation["empty_collections"]
                if empty_collections:
                    consistency_results["recommendations"].append(
                        f"Empty collections detected: {', '.join(empty_collections)}. Consider re-importing data."
                    )
            
            # Check for data quality issues
            if files_validation.get("errors"):
                consistency_results["recommendations"].append(
                    "Data quality issues detected in source files. Review and clean data."
                )
            
            logger.info("✅ Data consistency validation completed")
            return consistency_results
            
        except Exception as e:
            logger.error(f"❌ Data consistency validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def generate_validation_report(self) -> str:
        """Generate a comprehensive validation report"""
        try:
            logger.info("📊 Generating validation report...")
            
            consistency_results = await self.validate_data_consistency()
            
            report = []
            report.append("=" * 60)
            report.append("DATA VALIDATION REPORT")
            report.append("=" * 60)
            
            # Vector Database Status
            report.append("\n📊 VECTOR DATABASE STATUS:")
            vector_db = consistency_results.get("vector_db", {})
            if vector_db.get("valid"):
                report.append(f"✅ Status: Healthy")
                report.append(f"📈 Total Points: {vector_db.get('total_points', 0)}")
                
                collections = vector_db.get("collections", {})
                for name, stats in collections.items():
                    status_icon = "✅" if stats["points"] > 0 else "⚠️"
                    report.append(f"  {status_icon} {name}: {stats['points']} points")
                    
                # Show empty collections warning if any
                empty_collections = vector_db.get("empty_collections", [])
                if empty_collections:
                    report.append(f"  ⚠️ Empty collections: {', '.join(empty_collections)}")
            else:
                report.append(f"❌ Status: Unhealthy - {vector_db.get('error', 'Unknown error')}")
            
            # Source Files Status
            report.append("\n📁 SOURCE FILES STATUS:")
            source_files = consistency_results.get("source_files", {})
            if source_files.get("valid"):
                report.append("✅ Status: Valid")
                files = source_files.get("files", {})
                for domain, file_stats in files.items():
                    report.append(f"  📄 {domain}: {file_stats['total_rows']} total rows")
            else:
                report.append(f"❌ Status: Invalid - {source_files.get('error', 'Unknown error')}")
            
            # Recommendations
            recommendations = consistency_results.get("recommendations", [])
            if recommendations:
                report.append("\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    report.append(f"  {i}. {rec}")
            
            report.append("\n" + "=" * 60)
            
            report_text = "\n".join(report)
            logger.info("✅ Validation report generated")
            return report_text
            
        except Exception as e:
            logger.error(f"❌ Failed to generate validation report: {str(e)}")
            return f"Error generating report: {str(e)}"

# Global instance
data_validation_service = DataValidationService()

async def main():
    """Run validation and generate report"""
    report = await data_validation_service.generate_validation_report()
    print(report)

if __name__ == "__main__":
    asyncio.run(main())