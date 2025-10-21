#!/usr/bin/env python3
"""
Assessment Data Cleaning Script

This script cleans and fixes the assessment data to ensure proper workflow:
- Fixes null values and incorrect data
- Implements proper assessment flow logic with next_step sequencing
- Fixes cluster groupings and batch_id assignments
- Adds proper order_index for question sequencing
- Ensures assessment workflow runs correctly
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# Add the backend directory to Python path
import sys
sys.path.append(str(Path(__file__).parent))

from app.core.database import init_db, get_mongodb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AssessmentDataCleaner:
    """Handles cleaning and fixing assessment data for proper workflow"""

    def __init__(self):
        self.stats = {
            'total_processed': 0,
            'successfully_updated': 0,
            'validation_errors': 0,
            'update_errors': 0
        }
        self.assessment_flow_map = {}  # Maps question_id to next_step
        self.cluster_questions = {}  # Groups questions by cluster
        self.batch_groups = {}  # Groups questions by batch

    async def initialize(self):
        """Initialize the cleaner"""
        await init_db()

    def analyze_assessment_data(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze assessment data to understand current structure and issues"""
        analysis = {
            'total_questions': len(assessments),
            'null_next_step': 0,
            'null_order_index': 0,
            'empty_batch_id': 0,
            'inconsistent_clusters': 0,
            'missing_scale_values': 0,
            'cluster_distribution': {},
            'response_type_distribution': {},
            'sub_category_distribution': {}
        }

        for assessment in assessments:
            # Count null/empty values
            if not assessment.get('next_step'):
                analysis['null_next_step'] += 1
            if assessment.get('order_index') is None:
                analysis['null_order_index'] += 1
            if not assessment.get('batch_id'):
                analysis['empty_batch_id'] += 1

            # Check for missing scale values for scale questions
            if assessment.get('response_type') == 'scale':
                if assessment.get('scale_min') is None or assessment.get('scale_max') is None:
                    analysis['missing_scale_values'] += 1

            # Count distributions
            cluster = assessment.get('clusters', 'unknown')
            analysis['cluster_distribution'][cluster] = analysis['cluster_distribution'].get(cluster, 0) + 1

            response_type = assessment.get('response_type', 'unknown')
            analysis['response_type_distribution'][response_type] = analysis['response_type_distribution'].get(response_type, 0) + 1

            sub_category = assessment.get('sub_category_id', 'unknown')
            analysis['sub_category_distribution'][sub_category] = analysis['sub_category_distribution'].get(sub_category, 0) + 1

        return analysis

    def create_assessment_flow_logic(self, assessments: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create proper assessment flow logic based on clusters and question patterns"""
        flow_map = {}

        # Group questions by cluster
        cluster_groups = {}
        for assessment in assessments:
            cluster = assessment.get('clusters', 'general')
            if cluster not in cluster_groups:
                cluster_groups[cluster] = []
            cluster_groups[cluster].append(assessment)

        # Create flow for each cluster
        for cluster, questions in cluster_groups.items():
            # Sort questions by question_id to create logical flow
            sorted_questions = sorted(questions, key=lambda x: x.get('question_id', ''))

            # Create sequential flow within cluster
            for i, question in enumerate(sorted_questions):
                question_id = question.get('question_id')
                if not question_id:
                    continue

                # Determine next step
                if i < len(sorted_questions) - 1:
                    # Not the last question in cluster
                    next_question = sorted_questions[i + 1]
                    next_step = next_question.get('question_id')
                else:
                    # Last question in cluster
                    if cluster == 'general':
                        next_step = 'end_assess'
                    else:
                        # For specific clusters, continue to next cluster or end
                        next_step = 'end_assess'

                flow_map[question_id] = next_step

        return flow_map

    def assign_batch_ids(self, assessments: List[Dict[str, Any]]) -> Dict[str, str]:
        """Assign meaningful batch IDs based on clusters and subcategories"""
        batch_map = {}

        for assessment in assessments:
            question_id = assessment.get('question_id')
            cluster = assessment.get('clusters', 'general')
            sub_category = assessment.get('sub_category_id', 'GEN_01_01')

            # Create batch ID based on cluster and subcategory
            if cluster == 'general':
                batch_id = f"BATCH_GEN_{sub_category}"
            elif cluster.startswith('c'):
                cluster_num = cluster[1:] if cluster[1:].isdigit() else '1'
                batch_id = f"BATCH_C{cluster_num}_{sub_category}"
            else:
                batch_id = f"BATCH_{cluster.upper()}_{sub_category}"

            batch_map[question_id] = batch_id

        return batch_map

    # Removed order index assignment; sequencing is derived from next_step and batch/cluster.
    def assign_order_indices(self, assessments: List[Dict[str, Any]]) -> Dict[str, int]:
        return {}

    def fix_scale_values(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Fix scale values for scale-type questions"""
        if assessment.get('response_type') == 'scale':
            # Set default scale values if missing
            if assessment.get('scale_min') is None:
                assessment['scale_min'] = 1
            if assessment.get('scale_max') is None:
                assessment['scale_max'] = 5

            # Ensure scale_min < scale_max
            if assessment['scale_min'] >= assessment['scale_max']:
                assessment['scale_max'] = assessment['scale_min'] + 4
        else:
            # Clear scale values for non-scale questions
            assessment['scale_min'] = None
            assessment['scale_max'] = None

        return assessment

    def standardize_clusters(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize cluster values"""
        cluster = assessment.get('clusters', 'general')

        # Standardize cluster names
        if cluster in ['general', 'General', 'GENERAL']:
            assessment['clusters'] = 'general'
        elif cluster.startswith('c') and cluster[1:].isdigit():
            assessment['clusters'] = f"c{cluster[1:]}"
        elif cluster.startswith('C') and cluster[1:].isdigit():
            assessment['clusters'] = f"c{cluster[1:]}"
        else:
            # Default to general for unknown clusters
            assessment['clusters'] = 'general'

        return assessment

    def clean_assessment_item(self, assessment: Dict[str, Any], flow_map: Dict[str, str],
                            batch_map: Dict[str, str], order_map: Dict[str, int]) -> Dict[str, Any]:
        """Clean and fix a single assessment item"""
        question_id = assessment.get('question_id')
        if not question_id:
            return assessment

        # Fix null/empty values
        assessment['next_step'] = flow_map.get(question_id, 'end_assess')
        assessment['batch_id'] = batch_map.get(question_id, f"BATCH_GEN_{assessment.get('sub_category_id', 'GEN_01_01')}")
        # order_index removed from schema; sequencing is implicit

        # Ensure is_active is boolean
        if assessment.get('is_active') is None:
            assessment['is_active'] = True

        # Fix scale values
        assessment = self.fix_scale_values(assessment)

        # Standardize clusters
        assessment = self.standardize_clusters(assessment)

        # Ensure required fields have default values
        if not assessment.get('sub_category_id'):
            assessment['sub_category_id'] = 'GEN_01_01'

        if not assessment.get('response_type'):
            assessment['response_type'] = 'text'

        # Clean question text
        if assessment.get('question_text'):
            assessment['question_text'] = assessment['question_text'].strip()

        # Set timestamps if missing
        now = datetime.utcnow()
        if not assessment.get('created_at'):
            assessment['created_at'] = now.isoformat()
        if not assessment.get('updated_at'):
            assessment['updated_at'] = now.isoformat()

        return assessment

    async def clean_assessment_data(self) -> Dict[str, Any]:
        """Main function to clean assessment data"""
        try:
            logger.info("Starting assessment data cleaning...")

            # Get all assessment data directly from database
            client = get_mongodb()
            if client is None:
                logger.error("MongoDB not available")
                return {"error": "MongoDB not available"}

            db = client.mental_health_chat
            assessments_cursor = db.assessments.find({})
            assessments = await assessments_cursor.to_list(length=1000)
            logger.info(f"Found {len(assessments)} assessment questions to clean")

            # Analyze current data
            analysis = self.analyze_assessment_data(assessments)
            logger.info(f"Data analysis: {analysis}")

            # Create flow logic
            flow_map = self.create_assessment_flow_logic(assessments)
            logger.info(f"Created flow map for {len(flow_map)} questions")

            # Assign batch IDs
            batch_map = self.assign_batch_ids(assessments)
            logger.info(f"Assigned batch IDs for {len(batch_map)} questions")

            # Order indices removed; keep placeholder map empty for compatibility
            order_map = self.assign_order_indices(assessments)

            # Clean each assessment
            for assessment in assessments:
                self.stats['total_processed'] += 1

                try:
                    # Clean the assessment item
                    cleaned_assessment = self.clean_assessment_item(
                        assessment, flow_map, batch_map, order_map
                    )

                    # Update in database
                    question_id = cleaned_assessment.get('question_id')
                    if question_id:
                        # Update the document directly
                        result = await db.assessments.update_one(
                            {"question_id": question_id},
                            {"$set": cleaned_assessment}
                        )

                        if result.modified_count > 0:
                            self.stats['successfully_updated'] += 1
                        else:
                            self.stats['validation_errors'] += 1
                            logger.warning(f"Failed to update assessment {question_id}")
                    else:
                        self.stats['validation_errors'] += 1
                        logger.warning("Assessment missing question_id")

                    if self.stats['total_processed'] % 50 == 0:
                        logger.info(f"Processed {self.stats['total_processed']} assessments...")

                except Exception as e:
                    self.stats['update_errors'] += 1
                    logger.error(f"Failed to clean assessment {assessment.get('question_id', 'unknown')}: {str(e)}")

            logger.info("Assessment data cleaning completed")
            return self.stats

        except Exception as e:
            logger.error(f"Failed to clean assessment data: {str(e)}")
            return {"error": str(e)}

    async def validate_assessment_workflow(self) -> Dict[str, Any]:
        """Validate that the assessment workflow is properly configured"""
        try:
            logger.info("Validating assessment workflow...")

            # Get cleaned assessment data directly from database
            client = get_mongodb()
            if client is None:
                return {"error": "MongoDB not available"}

            db = client.mental_health_chat
            assessments_cursor = db.assessments.find({})
            assessments = await assessments_cursor.to_list(length=1000)

            validation_results = {
                'total_questions': len(assessments),
                'valid_flows': 0,
                'invalid_flows': 0,
                'missing_next_steps': 0,
                'circular_references': 0,
                'orphaned_questions': 0,
                'cluster_coverage': {},
                'flow_issues': []
            }

            # Check for valid flows
            question_ids = {a.get('question_id') for a in assessments if a.get('question_id')}

            for assessment in assessments:
                question_id = assessment.get('question_id')
                next_step = assessment.get('next_step')

                if not question_id:
                    continue

                if not next_step:
                    validation_results['missing_next_steps'] += 1
                    validation_results['flow_issues'].append(f"Question {question_id} has no next_step")
                    continue

                if next_step == 'end_assess':
                    validation_results['valid_flows'] += 1
                    continue

                if next_step in question_ids:
                    validation_results['valid_flows'] += 1
                else:
                    validation_results['orphaned_questions'] += 1
                    validation_results['flow_issues'].append(f"Question {question_id} points to non-existent question {next_step}")

            # Check cluster coverage
            for assessment in assessments:
                cluster = assessment.get('clusters', 'general')
                validation_results['cluster_coverage'][cluster] = validation_results['cluster_coverage'].get(cluster, 0) + 1

            logger.info(f"Validation results: {validation_results}")
            return validation_results

        except Exception as e:
            logger.error(f"Failed to validate assessment workflow: {str(e)}")
            return {"error": str(e)}

async def main():
    """Main function to run the assessment data cleaning"""
    cleaner = AssessmentDataCleaner()
    await cleaner.initialize()

    # Clean assessment data
    print("\n" + "="*60)
    print("ASSESSMENT DATA CLEANING")
    print("="*60)

    results = await cleaner.clean_assessment_data()

    print(f"Total processed: {results.get('total_processed', 0)}")
    print(f"Successfully updated: {results.get('successfully_updated', 0)}")
    print(f"Validation errors: {results.get('validation_errors', 0)}")
    print(f"Update errors: {results.get('update_errors', 0)}")

    # Validate workflow
    print("\n" + "="*60)
    print("ASSESSMENT WORKFLOW VALIDATION")
    print("="*60)

    validation = await cleaner.validate_assessment_workflow()

    if 'error' not in validation:
        print(f"Total questions: {validation.get('total_questions', 0)}")
        print(f"Valid flows: {validation.get('valid_flows', 0)}")
        print(f"Invalid flows: {validation.get('invalid_flows', 0)}")
        print(f"Missing next steps: {validation.get('missing_next_steps', 0)}")
        print(f"Orphaned questions: {validation.get('orphaned_questions', 0)}")
        print(f"Cluster coverage: {validation.get('cluster_coverage', {})}")

        if validation.get('flow_issues'):
            print("\nFlow issues found:")
            for issue in validation['flow_issues'][:10]:  # Show first 10 issues
                print(f"  - {issue}")
            if len(validation['flow_issues']) > 10:
                print(f"  ... and {len(validation['flow_issues']) - 10} more issues")
    else:
        print(f"Validation error: {validation['error']}")

    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
