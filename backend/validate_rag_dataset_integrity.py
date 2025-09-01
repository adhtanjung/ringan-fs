#!/usr/bin/env python3
"""
RAG Dataset Integrity Validation Script
Verifies that:
1. Vector database contains complete dataset from Excel files
2. All RAG responses reference actual dataset content
3. Questions and suggestions are properly sourced from Excel data
"""

import asyncio
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
import json

# Import services
from app.services.vector_service import vector_service
from app.services.semantic_search_service import semantic_search_service
from app.services.chat_service import ChatService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGDatasetValidator:
    """Validates RAG system against source Excel datasets"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.datasets = {
            "stress": "stress.xlsx",
            "anxiety": "anxiety.xlsx", 
            "trauma": "trauma.xlsx",
            "general": "mentalhealthdata.xlsx"
        }
        self.chat_service = ChatService()
        
    async def initialize_services(self) -> bool:
        """Initialize all required services"""
        try:
            await vector_service.connect()
            await vector_service.create_collections()
            await semantic_search_service.initialize()
            logger.info("✅ Services initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
            return False
    
    def load_excel_data(self, dataset_name: str) -> Dict[str, pd.DataFrame]:
        """Load all sheets from Excel file"""
        file_path = self.data_dir / self.datasets[dataset_name]
        
        if not file_path.exists():
            logger.error(f"Dataset file not found: {file_path}")
            return {}
            
        try:
            # Load all sheets
            excel_data = pd.read_excel(file_path, sheet_name=None)
            logger.info(f"Loaded {len(excel_data)} sheets from {dataset_name}")
            return excel_data
        except Exception as e:
            logger.error(f"Error loading {dataset_name}: {e}")
            return {}
    
    def extract_dataset_content(self, excel_data: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
        """Extract all text content from Excel sheets"""
        content = {
            "problems": [],
            "assessments": [],
            "suggestions": [],
            "feedback": [],
            "training": []
        }
        
        for sheet_name, df in excel_data.items():
            if "problem" in sheet_name.lower():
                # Extract problem descriptions
                if 'description' in df.columns:
                    content["problems"].extend(df['description'].dropna().astype(str).tolist())
                if 'problem_name' in df.columns:
                    content["problems"].extend(df['problem_name'].dropna().astype(str).tolist())
                    
            elif "assessment" in sheet_name.lower():
                # Extract assessment questions
                if 'question_text' in df.columns:
                    content["assessments"].extend(df['question_text'].dropna().astype(str).tolist())
                    
            elif "suggestion" in sheet_name.lower():
                # Extract suggestions
                if 'suggestion_text' in df.columns:
                    content["suggestions"].extend(df['suggestion_text'].dropna().astype(str).tolist())
                    
            elif "feedback" in sheet_name.lower():
                # Extract feedback prompts
                if 'prompt_text' in df.columns:
                    content["feedback"].extend(df['prompt_text'].dropna().astype(str).tolist())
                    
            elif "tuning" in sheet_name.lower() or "training" in sheet_name.lower():
                # Extract training examples
                if 'completion' in df.columns:
                    content["training"].extend(df['completion'].dropna().astype(str).tolist())
                if 'prompt' in df.columns:
                    content["training"].extend(df['prompt'].dropna().astype(str).tolist())
        
        return content
    
    async def validate_vector_database_coverage(self, dataset_name: str, excel_content: Dict[str, List[str]]) -> Dict[str, Any]:
        """Validate that vector database contains Excel content"""
        validation_result = {
            "dataset": dataset_name,
            "coverage_analysis": {},
            "missing_content": {},
            "vector_db_stats": {}
        }
        
        try:
            # Get vector database statistics
            collections = vector_service.client.get_collections()
            for collection in collections.collections:
                count = vector_service.client.count(collection.name).count
                validation_result["vector_db_stats"][collection.name] = count
            
            # Test search coverage for each content type
            for content_type, texts in excel_content.items():
                if not texts:
                    continue
                    
                found_count = 0
                missing_samples = []
                
                # Sample 10 texts to test coverage
                sample_texts = texts[:10] if len(texts) > 10 else texts
                
                for text in sample_texts:
                    if len(text.strip()) < 10:  # Skip very short texts
                        continue
                        
                    # Search for this text in vector database
                    if content_type == "problems":
                        search_result = await semantic_search_service.search_problems(text, limit=5, score_threshold=0.3)
                    elif content_type == "assessments":
                        search_result = await semantic_search_service.search_assessment_questions(text, limit=5, score_threshold=0.3)
                    elif content_type == "suggestions":
                        search_result = await semantic_search_service.search_therapeutic_suggestions(text, limit=5, score_threshold=0.3)
                    else:
                        continue
                    
                    if search_result.success and search_result.results:
                        # Check if any result contains similar content
                        found = False
                        for result in search_result.results:
                            result_text = result.payload.get('text', '') or result.payload.get('suggestion_text', '') or result.payload.get('question_text', '')
                            if self._text_similarity(text, result_text) > 0.5:
                                found = True
                                break
                        if found:
                            found_count += 1
                        else:
                            missing_samples.append(text[:100] + "..." if len(text) > 100 else text)
                    else:
                        missing_samples.append(text[:100] + "..." if len(text) > 100 else text)
                
                coverage_percentage = (found_count / len(sample_texts)) * 100 if sample_texts else 0
                validation_result["coverage_analysis"][content_type] = {
                    "total_samples_tested": len(sample_texts),
                    "found_in_vector_db": found_count,
                    "coverage_percentage": coverage_percentage
                }
                validation_result["missing_content"][content_type] = missing_samples[:5]  # Show first 5 missing
                
        except Exception as e:
            validation_result["error"] = str(e)
            logger.error(f"Error validating vector database coverage: {e}")
        
        return validation_result
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity check"""
        if not text1 or not text2:
            return 0.0
        
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def validate_rag_responses(self, dataset_name: str, excel_content: Dict[str, List[str]]) -> Dict[str, Any]:
        """Validate that RAG responses reference Excel dataset content"""
        validation_result = {
            "dataset": dataset_name,
            "test_queries": [],
            "rag_source_validation": {},
            "content_traceability": {}
        }
        
        # Generate test queries based on dataset content
        test_queries = [
            f"I'm struggling with {dataset_name} and need help",
            f"What are some {dataset_name} management techniques?",
            f"How do I cope with {dataset_name} symptoms?",
            f"I need assessment questions for {dataset_name}",
            f"Can you suggest interventions for {dataset_name}?"
        ]
        
        for query in test_queries:
            try:
                # Get response from chat service
                client_id = f"validation_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                response = await self.chat_service.process_message(query, client_id)
                
                # Analyze RAG sources
                semantic_context = response.get("semantic_context", [])
                rag_analysis = {
                    "query": query,
                    "sources_found": len(semantic_context),
                    "sources_from_dataset": 0,
                    "content_matches": [],
                    "source_details": []
                }
                
                # Check if sources reference Excel content
                for source in semantic_context:
                    source_text = source.get("payload", {}).get("text", "")
                    source_domain = source.get("payload", {}).get("domain", "")
                    
                    rag_analysis["source_details"].append({
                        "id": source.get("id", ""),
                        "score": source.get("score", 0),
                        "domain": source_domain,
                        "content_preview": source_text[:100] + "..." if len(source_text) > 100 else source_text
                    })
                    
                    # Check if source content matches Excel data
                    for content_type, texts in excel_content.items():
                        for excel_text in texts:
                            if self._text_similarity(source_text, excel_text) > 0.7:
                                rag_analysis["sources_from_dataset"] += 1
                                rag_analysis["content_matches"].append({
                                    "content_type": content_type,
                                    "similarity": self._text_similarity(source_text, excel_text),
                                    "excel_content_preview": excel_text[:100] + "..." if len(excel_text) > 100 else excel_text
                                })
                                break
                
                validation_result["test_queries"].append(rag_analysis)
                
            except Exception as e:
                logger.error(f"Error testing query '{query}': {e}")
                validation_result["test_queries"].append({
                    "query": query,
                    "error": str(e)
                })
        
        # Calculate overall traceability metrics
        total_sources = sum(q.get("sources_found", 0) for q in validation_result["test_queries"] if "error" not in q)
        dataset_sources = sum(q.get("sources_from_dataset", 0) for q in validation_result["test_queries"] if "error" not in q)
        
        validation_result["content_traceability"] = {
            "total_rag_sources": total_sources,
            "sources_from_excel_dataset": dataset_sources,
            "traceability_percentage": (dataset_sources / total_sources * 100) if total_sources > 0 else 0
        }
        
        return validation_result
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete RAG dataset integrity validation"""
        logger.info("🚀 Starting RAG Dataset Integrity Validation")
        
        if not await self.initialize_services():
            return {"error": "Failed to initialize services"}
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "dataset_coverage": {},
            "rag_validation": {},
            "summary": {}
        }
        
        total_coverage = 0
        total_traceability = 0
        datasets_processed = 0
        
        for dataset_name in self.datasets.keys():
            logger.info(f"📊 Validating {dataset_name} dataset...")
            
            # Load Excel data
            excel_data = self.load_excel_data(dataset_name)
            if not excel_data:
                continue
            
            # Extract content
            excel_content = self.extract_dataset_content(excel_data)
            
            # Validate vector database coverage
            coverage_result = await self.validate_vector_database_coverage(dataset_name, excel_content)
            validation_results["dataset_coverage"][dataset_name] = coverage_result
            
            # Validate RAG responses
            rag_result = await self.validate_rag_responses(dataset_name, excel_content)
            validation_results["rag_validation"][dataset_name] = rag_result
            
            # Calculate metrics
            avg_coverage = sum(c.get("coverage_percentage", 0) for c in coverage_result.get("coverage_analysis", {}).values())
            avg_coverage = avg_coverage / len(coverage_result.get("coverage_analysis", {})) if coverage_result.get("coverage_analysis") else 0
            
            traceability = rag_result.get("content_traceability", {}).get("traceability_percentage", 0)
            
            total_coverage += avg_coverage
            total_traceability += traceability
            datasets_processed += 1
            
            logger.info(f"  ✓ {dataset_name}: {avg_coverage:.1f}% coverage, {traceability:.1f}% traceability")
        
        # Generate summary
        validation_results["summary"] = {
            "datasets_processed": datasets_processed,
            "average_vector_db_coverage": total_coverage / datasets_processed if datasets_processed > 0 else 0,
            "average_rag_traceability": total_traceability / datasets_processed if datasets_processed > 0 else 0,
            "validation_passed": (total_coverage / datasets_processed if datasets_processed > 0 else 0) > 70 and (total_traceability / datasets_processed if datasets_processed > 0 else 0) > 70
        }
        
        # Save results
        with open("rag_dataset_validation_results.json", "w") as f:
            json.dump(validation_results, f, indent=2)
        
        logger.info("✅ RAG Dataset Integrity Validation completed")
        return validation_results

async def main():
    """Main validation function"""
    validator = RAGDatasetValidator()
    results = await validator.run_comprehensive_validation()
    
    # Print summary
    summary = results.get("summary", {})
    print("\n" + "="*60)
    print("RAG DATASET INTEGRITY VALIDATION SUMMARY")
    print("="*60)
    print(f"Datasets Processed: {summary.get('datasets_processed', 0)}")
    print(f"Average Vector DB Coverage: {summary.get('average_vector_db_coverage', 0):.1f}%")
    print(f"Average RAG Traceability: {summary.get('average_rag_traceability', 0):.1f}%")
    print(f"Validation Status: {'✅ PASSED' if summary.get('validation_passed', False) else '❌ FAILED'}")
    print("="*60)
    
if __name__ == "__main__":
    asyncio.run(main())