#!/usr/bin/env python3
"""
Dataset Import Verification Script

This script verifies that all specified datasets have been successfully imported
into both MongoDB and the vector database (Qdrant). It checks for:
- Data completeness and integrity
- Proper collection structure
- Vector database synchronization
- Missing or corrupted data
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from app.core.database import init_db, get_mongodb
from app.services.vector_service import vector_service
from app.services.dataset_management_service import dataset_management_service
from app.services.embedding_service import embedding_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatasetImportVerifier:
    """Comprehensive dataset import verification"""
    
    def __init__(self):
        self.mongodb_client = None
        self.db = None
        self.verification_results = {
            'mongodb': {},
            'vector_db': {},
            'data_integrity': {},
            'summary': {}
        }
        
        # Expected dataset types and their MongoDB collections
        self.dataset_types = {
            'problems': 'problems',
            'assessments': 'assessments', 
            'suggestions': 'suggestions',
            'feedback_prompts': 'feedback_prompts',
            'next_actions': 'next_actions',
            'training_examples': 'training_examples'
        }
        
        # Expected vector database collections
        self.vector_collections = {
            'mental-health-problems': 'problems',
            'mental-health-assessments': 'assessments',
            'mental-health-suggestions': 'suggestions'
        }
    
    async def initialize(self) -> bool:
        """Initialize database connections and services"""
        try:
            print("🔄 Initializing database connections...")
            
            # Initialize MongoDB
            await init_db()
            self.mongodb_client = get_mongodb()
            
            if self.mongodb_client is None:
                print("❌ MongoDB connection failed")
                return False
                
            self.db = self.mongodb_client.mental_health_db
            print("✅ MongoDB connected successfully")
            
            # Initialize vector database
            await vector_service.connect()
            health = await vector_service.health_check()
            if not health:
                print("❌ Vector database connection failed")
                return False
                
            print("✅ Vector database connected successfully")
            
            # Initialize dataset management service
            await dataset_management_service.initialize()
            print("✅ Dataset management service initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {str(e)}")
            return False
    
    async def verify_mongodb_collections(self) -> Dict[str, Any]:
        """Verify MongoDB collections and their data"""
        print("\n📊 Verifying MongoDB collections...")
        
        mongodb_results = {}
        
        try:
            # Get all collection names
            collection_names = await self.db.list_collection_names()
            print(f"Found collections: {collection_names}")
            
            for dataset_type, collection_name in self.dataset_types.items():
                collection_info = {
                    'exists': collection_name in collection_names,
                    'count': 0,
                    'sample_data': None,
                    'schema_validation': 'pending'
                }
                
                if collection_info['exists']:
                    collection = getattr(self.db, collection_name)
                    
                    # Get document count
                    collection_info['count'] = await collection.count_documents({})
                    
                    # Get sample document for schema validation
                    if collection_info['count'] > 0:
                        sample_doc = await collection.find_one()
                        if sample_doc:
                            # Remove MongoDB ObjectId for display
                            sample_doc.pop('_id', None)
                            collection_info['sample_data'] = sample_doc
                            collection_info['schema_validation'] = 'valid'
                    
                    print(f"  ✅ {dataset_type}: {collection_info['count']} documents")
                else:
                    print(f"  ❌ {dataset_type}: Collection missing")
                
                mongodb_results[dataset_type] = collection_info
                
        except Exception as e:
            logger.error(f"❌ MongoDB verification failed: {str(e)}")
            mongodb_results['error'] = str(e)
        
        self.verification_results['mongodb'] = mongodb_results
        return mongodb_results
    
    async def verify_vector_database(self) -> Dict[str, Any]:
        """Verify vector database collections and embeddings"""
        print("\n🔍 Verifying vector database collections...")
        
        vector_results = {}
        
        try:
            # Get all collections
            collections = vector_service.client.get_collections()
            existing_collections = [c.name for c in collections.collections]
            print(f"Found vector collections: {existing_collections}")
            
            for collection_name, dataset_type in self.vector_collections.items():
                collection_info = {
                    'exists': collection_name in existing_collections,
                    'count': 0,
                    'sample_point': None,
                    'embedding_dimension': None
                }
                
                if collection_info['exists']:
                    # Get point count
                    count_result = vector_service.client.count(collection_name)
                    collection_info['count'] = count_result.count
                    
                    # Get sample point for validation
                    if collection_info['count'] > 0:
                        scroll_result = vector_service.client.scroll(
                            collection_name=collection_name,
                            limit=1,
                            with_payload=True,
                            with_vectors=True
                        )
                        
                        if scroll_result[0]:  # points
                            sample_point = scroll_result[0][0]
                            collection_info['sample_point'] = {
                                'id': sample_point.id,
                                'payload': sample_point.payload,
                                'vector_length': len(sample_point.vector) if sample_point.vector else 0
                            }
                            collection_info['embedding_dimension'] = len(sample_point.vector) if sample_point.vector else 0
                    
                    print(f"  ✅ {collection_name}: {collection_info['count']} points")
                else:
                    print(f"  ❌ {collection_name}: Collection missing")
                
                vector_results[collection_name] = collection_info
                
        except Exception as e:
            logger.error(f"❌ Vector database verification failed: {str(e)}")
            vector_results['error'] = str(e)
        
        self.verification_results['vector_db'] = vector_results
        return vector_results
    
    async def verify_data_integrity(self) -> Dict[str, Any]:
        """Verify data integrity and relationships between datasets"""
        print("\n🔗 Verifying data integrity and relationships...")
        
        integrity_results = {
            'foreign_key_validation': {},
            'data_consistency': {},
            'missing_relationships': []
        }
        
        try:
            # Check foreign key relationships
            if 'problems' in self.verification_results['mongodb'] and \
               'assessments' in self.verification_results['mongodb']:
                
                # Get all problem sub_category_ids
                problems_collection = getattr(self.db, 'problems')
                problem_sub_categories = set()
                async for doc in problems_collection.find({}, {'sub_category_id': 1}):
                    problem_sub_categories.add(doc.get('sub_category_id'))
                
                # Check assessment sub_category_ids
                assessments_collection = getattr(self.db, 'assessments')
                assessment_sub_categories = set()
                orphaned_assessments = []
                
                async for doc in assessments_collection.find({}, {'sub_category_id': 1, 'question_id': 1}):
                    sub_cat_id = doc.get('sub_category_id')
                    assessment_sub_categories.add(sub_cat_id)
                    
                    if sub_cat_id not in problem_sub_categories:
                        orphaned_assessments.append({
                            'question_id': doc.get('question_id'),
                            'sub_category_id': sub_cat_id
                        })
                
                integrity_results['foreign_key_validation'] = {
                    'problems_sub_categories': len(problem_sub_categories),
                    'assessments_sub_categories': len(assessment_sub_categories),
                    'orphaned_assessments': len(orphaned_assessments),
                    'orphaned_assessment_details': orphaned_assessments[:10]  # Show first 10
                }
                
                print(f"  📊 Problems have {len(problem_sub_categories)} unique sub-categories")
                print(f"  📊 Assessments reference {len(assessment_sub_categories)} sub-categories")
                if orphaned_assessments:
                    print(f"  ⚠️  Found {len(orphaned_assessments)} orphaned assessments")
                else:
                    print(f"  ✅ All assessments have valid sub-category references")
            
            # Check MongoDB vs Vector DB consistency
            mongodb_counts = {}
            vector_counts = {}
            
            for dataset_type in ['problems', 'assessments', 'suggestions']:
                if dataset_type in self.verification_results['mongodb']:
                    mongodb_counts[dataset_type] = self.verification_results['mongodb'][dataset_type].get('count', 0)
                
                vector_collection_name = f"mental-health-{dataset_type}"
                if vector_collection_name in self.verification_results['vector_db']:
                    vector_counts[dataset_type] = self.verification_results['vector_db'][vector_collection_name].get('count', 0)
            
            integrity_results['data_consistency'] = {
                'mongodb_counts': mongodb_counts,
                'vector_counts': vector_counts,
                'sync_status': {}
            }
            
            for dataset_type in mongodb_counts:
                mongo_count = mongodb_counts.get(dataset_type, 0)
                vector_count = vector_counts.get(dataset_type, 0)
                is_synced = mongo_count == vector_count
                
                integrity_results['data_consistency']['sync_status'][dataset_type] = {
                    'mongodb': mongo_count,
                    'vector_db': vector_count,
                    'synced': is_synced,
                    'difference': abs(mongo_count - vector_count)
                }
                
                if is_synced:
                    print(f"  ✅ {dataset_type}: MongoDB and Vector DB in sync ({mongo_count} items)")
                else:
                    print(f"  ⚠️  {dataset_type}: Sync mismatch - MongoDB: {mongo_count}, Vector DB: {vector_count}")
                    
        except Exception as e:
            logger.error(f"❌ Data integrity verification failed: {str(e)}")
            integrity_results['error'] = str(e)
        
        self.verification_results['data_integrity'] = integrity_results
        return integrity_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report"""
        print("\n📋 Generating summary report...")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'total_datasets': len(self.dataset_types),
            'imported_datasets': 0,
            'missing_datasets': [],
            'data_issues': [],
            'recommendations': []
        }
        
        # Count successfully imported datasets
        mongodb_results = self.verification_results.get('mongodb', {})
        for dataset_type, info in mongodb_results.items():
            if isinstance(info, dict) and info.get('exists') and info.get('count', 0) > 0:
                summary['imported_datasets'] += 1
            elif isinstance(info, dict):
                summary['missing_datasets'].append(dataset_type)
        
        # Check for data issues
        integrity_results = self.verification_results.get('data_integrity', {})
        if 'foreign_key_validation' in integrity_results:
            fk_validation = integrity_results['foreign_key_validation']
            if fk_validation.get('orphaned_assessments', 0) > 0:
                summary['data_issues'].append(
                    f"Found {fk_validation['orphaned_assessments']} orphaned assessments"
                )
        
        if 'data_consistency' in integrity_results:
            sync_status = integrity_results['data_consistency'].get('sync_status', {})
            for dataset_type, status in sync_status.items():
                if not status.get('synced', False):
                    summary['data_issues'].append(
                        f"{dataset_type}: MongoDB/Vector DB sync mismatch"
                    )
        
        # Generate recommendations
        if summary['missing_datasets']:
            summary['recommendations'].append(
                f"Import missing datasets: {', '.join(summary['missing_datasets'])}"
            )
        
        if summary['data_issues']:
            summary['recommendations'].append(
                "Fix data integrity issues before proceeding with production"
            )
        
        # Determine overall status
        if summary['imported_datasets'] == summary['total_datasets'] and not summary['data_issues']:
            summary['overall_status'] = 'success'
        elif summary['imported_datasets'] > 0:
            summary['overall_status'] = 'partial'
        else:
            summary['overall_status'] = 'failed'
        
        self.verification_results['summary'] = summary
        return summary
    
    def print_detailed_report(self):
        """Print a detailed verification report"""
        print("\n" + "="*80)
        print("📊 DATASET IMPORT VERIFICATION REPORT")
        print("="*80)
        
        summary = self.verification_results.get('summary', {})
        
        # Overall status
        status_emoji = {
            'success': '✅',
            'partial': '⚠️',
            'failed': '❌',
            'unknown': '❓'
        }
        
        overall_status = summary.get('overall_status', 'unknown')
        print(f"\n{status_emoji.get(overall_status, '❓')} Overall Status: {overall_status.upper()}")
        print(f"📅 Verification Time: {summary.get('timestamp', 'Unknown')}")
        
        # Dataset summary
        print(f"\n📈 Dataset Summary:")
        print(f"  Total Datasets: {summary.get('total_datasets', 0)}")
        print(f"  Successfully Imported: {summary.get('imported_datasets', 0)}")
        print(f"  Missing: {len(summary.get('missing_datasets', []))}")
        
        if summary.get('missing_datasets'):
            print(f"  Missing Datasets: {', '.join(summary['missing_datasets'])}")
        
        # MongoDB details
        print(f"\n🗄️  MongoDB Collections:")
        mongodb_results = self.verification_results.get('mongodb', {})
        for dataset_type, info in mongodb_results.items():
            if isinstance(info, dict):
                status = "✅" if info.get('exists') and info.get('count', 0) > 0 else "❌"
                count = info.get('count', 0)
                print(f"  {status} {dataset_type}: {count} documents")
        
        # Vector database details
        print(f"\n🔍 Vector Database Collections:")
        vector_results = self.verification_results.get('vector_db', {})
        for collection_name, info in vector_results.items():
            if isinstance(info, dict):
                status = "✅" if info.get('exists') and info.get('count', 0) > 0 else "❌"
                count = info.get('count', 0)
                print(f"  {status} {collection_name}: {count} points")
        
        # Data issues
        if summary.get('data_issues'):
            print(f"\n⚠️  Data Issues Found:")
            for issue in summary['data_issues']:
                print(f"  • {issue}")
        
        # Recommendations
        if summary.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"  • {rec}")
        
        print("\n" + "="*80)
    
    async def run_verification(self) -> bool:
        """Run complete dataset import verification"""
        print("🚀 Starting dataset import verification...")
        
        # Initialize connections
        if not await self.initialize():
            print("❌ Failed to initialize connections")
            return False
        
        # Run verification steps
        await self.verify_mongodb_collections()
        await self.verify_vector_database()
        await self.verify_data_integrity()
        
        # Generate summary
        self.generate_summary_report()
        
        # Print detailed report
        self.print_detailed_report()
        
        # Return success status
        summary = self.verification_results.get('summary', {})
        return summary.get('overall_status') == 'success'

async def main():
    """Main verification function"""
    verifier = DatasetImportVerifier()
    success = await verifier.run_verification()
    
    if success:
        print("\n🎉 All datasets have been successfully imported and verified!")
        return 0
    else:
        print("\n⚠️  Dataset import verification completed with issues. Please review the report above.")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)