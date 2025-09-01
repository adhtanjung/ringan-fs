#!/usr/bin/env python3
"""
Quick Vector Database Content Check
Verifies that Excel data has been properly imported into vector database
"""

import asyncio
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any
import json

# Import services
from app.services.vector_service import vector_service
from app.services.semantic_search_service import semantic_search_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuickVectorChecker:
    """Quick checker for vector database content"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.datasets = {
            "stress": "stress.xlsx",
            "anxiety": "anxiety.xlsx", 
            "trauma": "trauma.xlsx",
            "general": "mentalhealthdata.xlsx"
        }
        
    async def initialize_services(self) -> bool:
        """Initialize services"""
        try:
            await vector_service.connect()
            await semantic_search_service.initialize()
            logger.info("✅ Services initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize: {e}")
            return False
    
    def count_excel_records(self, dataset_name: str) -> Dict[str, int]:
        """Count records in Excel file"""
        file_path = self.data_dir / self.datasets[dataset_name]
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
            
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None)
            counts = {}
            
            for sheet_name, df in excel_data.items():
                # Count non-empty rows
                non_empty_rows = len(df.dropna(how='all'))
                counts[sheet_name] = non_empty_rows
                
            return counts
        except Exception as e:
            return {"error": str(e)}
    
    async def get_vector_db_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        try:
            collections = vector_service.client.get_collections()
            stats = {}
            
            for collection in collections.collections:
                count = vector_service.client.count(collection.name).count
                stats[collection.name] = count
                
            return stats
        except Exception as e:
            return {"error": str(e)}
    
    async def test_search_functionality(self) -> Dict[str, Any]:
        """Test basic search functionality"""
        test_results = {}
        
        # Test queries for each domain
        test_queries = {
            "stress": "work stress and pressure",
            "anxiety": "social anxiety and fear", 
            "trauma": "traumatic experience and recovery",
            "general": "mental health support"
        }
        
        for domain, query in test_queries.items():
            try:
                # Test problem search
                problem_result = await semantic_search_service.search_problems(query, limit=3)
                
                # Test assessment search
                assessment_result = await semantic_search_service.search_assessment_questions(query, limit=3)
                
                # Test suggestion search
                suggestion_result = await semantic_search_service.search_therapeutic_suggestions(query, limit=3)
                
                test_results[domain] = {
                    "problems_found": len(problem_result.results) if problem_result.success else 0,
                    "assessments_found": len(assessment_result.results) if assessment_result.success else 0,
                    "suggestions_found": len(suggestion_result.results) if suggestion_result.success else 0,
                    "total_results": (
                        len(problem_result.results) if problem_result.success else 0
                    ) + (
                        len(assessment_result.results) if assessment_result.success else 0
                    ) + (
                        len(suggestion_result.results) if suggestion_result.success else 0
                    )
                }
                
            except Exception as e:
                test_results[domain] = {"error": str(e)}
                
        return test_results
    
    async def run_quick_check(self) -> Dict[str, Any]:
        """Run quick vector database check"""
        logger.info("🚀 Starting Quick Vector Database Check")
        
        if not await self.initialize_services():
            return {"error": "Failed to initialize services"}
        
        results = {
            "excel_data_counts": {},
            "vector_db_stats": {},
            "search_functionality": {},
            "summary": {}
        }
        
        # Count Excel records
        logger.info("📊 Counting Excel records...")
        for dataset_name in self.datasets.keys():
            counts = self.count_excel_records(dataset_name)
            results["excel_data_counts"][dataset_name] = counts
            
        # Get vector database stats
        logger.info("🔍 Checking vector database...")
        results["vector_db_stats"] = await self.get_vector_db_stats()
        
        # Test search functionality
        logger.info("🔎 Testing search functionality...")
        results["search_functionality"] = await self.test_search_functionality()
        
        # Generate summary
        total_excel_records = 0
        total_vector_records = 0
        
        for dataset_counts in results["excel_data_counts"].values():
            if "error" not in dataset_counts:
                total_excel_records += sum(dataset_counts.values())
        
        if "error" not in results["vector_db_stats"]:
            total_vector_records = sum(results["vector_db_stats"].values())
        
        total_search_results = 0
        for domain_results in results["search_functionality"].values():
            if "error" not in domain_results:
                total_search_results += domain_results.get("total_results", 0)
        
        results["summary"] = {
            "total_excel_records": total_excel_records,
            "total_vector_records": total_vector_records,
            "total_search_results": total_search_results,
            "data_import_success": total_vector_records > 0,
            "search_functionality_working": total_search_results > 0
        }
        
        # Save results
        with open("quick_vector_check_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info("✅ Quick check completed")
        return results

async def main():
    """Main function"""
    checker = QuickVectorChecker()
    results = await checker.run_quick_check()
    
    # Print summary
    summary = results.get("summary", {})
    print("\n" + "="*50)
    print("QUICK VECTOR DATABASE CHECK SUMMARY")
    print("="*50)
    print(f"Excel Records: {summary.get('total_excel_records', 0)}")
    print(f"Vector Records: {summary.get('total_vector_records', 0)}")
    print(f"Search Results: {summary.get('total_search_results', 0)}")
    print(f"Data Import: {'✅ SUCCESS' if summary.get('data_import_success', False) else '❌ FAILED'}")
    print(f"Search Working: {'✅ SUCCESS' if summary.get('search_functionality_working', False) else '❌ FAILED'}")
    print("="*50)
    
    # Print detailed stats
    print("\nVector Database Collections:")
    vector_stats = results.get("vector_db_stats", {})
    if "error" not in vector_stats:
        for collection, count in vector_stats.items():
            print(f"  {collection}: {count} records")
    else:
        print(f"  Error: {vector_stats['error']}")
    
    print("\nSearch Functionality Test:")
    search_results = results.get("search_functionality", {})
    for domain, domain_results in search_results.items():
        if "error" not in domain_results:
            print(f"  {domain}: {domain_results['total_results']} total results")
        else:
            print(f"  {domain}: Error - {domain_results['error']}")
    
if __name__ == "__main__":
    asyncio.run(main())