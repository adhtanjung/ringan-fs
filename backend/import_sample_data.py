#!/usr/bin/env python3
"""
Sample Data Import Script
Imports data from Excel files to populate the database for meaningful API responses
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import get_mongodb, init_db
from app.services.dataset_management_service import DatasetManagementService

class SampleDataImporter:
    def __init__(self):
        self.db = None
        self.dataset_service = None
        self.data_files = {
            'stress': 'data/stress.xlsx',
            'anxiety': 'data/anxiety.xlsx',
            'trauma': 'data/trauma.xlsx',
            'mental_health': 'data/mentalhealthdata.xlsx'
        }

    async def initialize(self):
        """Initialize database connection and services"""
        await init_db()
        self.db = get_mongodb()
        self.dataset_service = DatasetManagementService()
        await self.dataset_service.initialize()
        print("✅ Database and services initialized")

    def read_excel_sheet(self, file_path: str, sheet_name: str) -> pd.DataFrame:
        """Read a specific sheet from Excel file"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df.fillna('')  # Replace NaN with empty strings
        except Exception as e:
            print(f"⚠️  Error reading {file_path} sheet {sheet_name}: {e}")
            return pd.DataFrame()

    async def import_problems(self, category: str, file_path: str):
        """Import problem categories from Excel"""
        print(f"📋 Importing problems from {category}...")

        df = self.read_excel_sheet(file_path, '1.1 Problems')
        if df.empty:
            return

        problems = []
        for _, row in df.iterrows():
            problem_data = {
                'category': str(row.get('category', category)).strip(),
                'category_id': str(row.get('category_id', '')).strip(),
                'sub_category_id': str(row.get('sub_category_id', '')).strip(),
                'problem_name': str(row.get('problem_name', '')).strip(),
                'description': str(row.get('description', '')).strip(),
                'severity_level': 'moderate',  # Default value
                'tags': [category, 'imported'],
                'created_at': datetime.utcnow()
            }

            if problem_data['problem_name']:  # Only add if problem_name exists
                problems.append(problem_data)

        if problems:
            result = await self.dataset_service.bulk_create('problems', problems)
            print(f"✅ Imported {len(problems)} problems for {category}")
        else:
            print(f"⚠️  No valid problems found for {category}")

    async def import_assessments(self, category: str, file_path: str):
        """Import assessment questions from Excel"""
        print(f"📝 Importing assessments from {category}...")

        df = self.read_excel_sheet(file_path, '1.2 Self Assessment')
        if df.empty:
            return

        assessments = []
        for _, row in df.iterrows():
            assessment_data = {
                'question_id': str(row.get('question_id', '')).strip(),
                'sub_category_id': str(row.get('sub_category_id', '')).strip(),
                'batch_id': str(row.get('batch_id', '')).strip(),
                'question_text': str(row.get('question_text', '')).strip(),
                'response_type': str(row.get('response_type', 'scale')).strip(),
                'next_step': str(row.get('next_step', '')).strip(),
                'clusters': str(row.get('clusters', '')).strip(),
                'category': category,
                'scale_min': 0,
                'scale_max': 4,
                'tags': [category, 'imported'],
                'created_at': datetime.utcnow()
            }

            if assessment_data['question_text']:  # Only add if question exists
                assessments.append(assessment_data)

        if assessments:
            result = await self.dataset_service.bulk_create('assessments', assessments)
            print(f"✅ Imported {len(assessments)} assessments for {category}")
        else:
            print(f"⚠️  No valid assessments found for {category}")

    async def import_suggestions(self, category: str, file_path: str):
        """Import therapeutic suggestions from Excel"""
        print(f"💡 Importing suggestions from {category}...")

        df = self.read_excel_sheet(file_path, '1.3 Suggestions')
        if df.empty:
            return

        suggestions = []
        for _, row in df.iterrows():
            suggestion_data = {
                'suggestion_id': str(row.get('suggestion_id', '')).strip(),
                'sub_category_id': str(row.get('sub_category_id', '')).strip(),
                'cluster': str(row.get('cluster', '')).strip(),
                'suggestion_text': str(row.get('suggestion_text', '')).strip(),
                'resource_link': str(row.get('resource_link', '')).strip(),
                'category': category,
                'intervention_type': 'therapeutic',
                'evidence_level': 'moderate',
                'tags': [category, 'imported'],
                'created_at': datetime.utcnow()
            }

            if suggestion_data['suggestion_text']:  # Only add if suggestion exists
                suggestions.append(suggestion_data)

        if suggestions:
            result = await self.dataset_service.bulk_create('suggestions', suggestions)
            print(f"✅ Imported {len(suggestions)} suggestions for {category}")
        else:
            print(f"⚠️  No valid suggestions found for {category}")

    async def import_feedback_prompts(self, category: str, file_path: str):
        """Import feedback prompts from Excel"""
        print(f"🔄 Importing feedback prompts from {category}...")

        df = self.read_excel_sheet(file_path, '1.4 Feedback Prompts')
        if df.empty:
            return

        prompts = []
        for _, row in df.iterrows():
            prompt_data = {
                'prompt_id': str(row.get('prompt_id', '')).strip(),
                'stage': str(row.get('stage', 'post_suggestion')).strip(),
                'prompt_text': str(row.get('prompt_text', '')).strip(),
                'next_action': str(row.get('next_action', '')).strip(),
                'category': category,
                'prompt_type': 'feedback',
                'tags': [category, 'imported'],
                'created_at': datetime.utcnow()
            }

            if prompt_data['prompt_text']:  # Only add if prompt exists
                prompts.append(prompt_data)

        if prompts:
            result = await self.dataset_service.bulk_create('feedback', prompts)
            print(f"✅ Imported {len(prompts)} feedback prompts for {category}")
        else:
            print(f"⚠️  No valid feedback prompts found for {category}")

    async def import_next_actions(self, category: str, file_path: str):
        """Import next actions from Excel"""
        print(f"➡️  Importing next actions from {category}...")

        df = self.read_excel_sheet(file_path, '1.5 Next Action After Feedback')
        if df.empty:
            return

        actions = []
        for _, row in df.iterrows():
            action_data = {
                'action_id': str(row.get('action_id', '')).strip(),
                'action_type': str(row.get('action_type', 'continue_same')).strip(),
                'description': str(row.get('description', '')).strip(),
                'condition': str(row.get('condition', '')).strip(),
                'category': category,
                'priority': 'medium',
                'tags': [category, 'imported'],
                'created_at': datetime.utcnow()
            }

            if action_data['action_type']:  # Only add if action_type exists
                actions.append(action_data)

        if actions:
            result = await self.dataset_service.bulk_create('next_actions', actions)
            print(f"✅ Imported {len(actions)} next actions for {category}")
        else:
            print(f"⚠️  No valid next actions found for {category}")

    async def import_training_examples(self, category: str, file_path: str):
        """Import fine-tuning examples from Excel"""
        print(f"🎯 Importing training examples from {category}...")

        df = self.read_excel_sheet(file_path, '1.6 FineTuning Examples')
        if df.empty:
            return

        examples = []
        for _, row in df.iterrows():
            example_data = {
                'example_id': str(row.get('id', '')).strip(),
                'problem': str(row.get('problem', '')).strip(),
                'conversation_id': str(row.get('ConversationID', '')).strip(),
                'prompt': str(row.get('prompt', '')).strip(),
                'completion': str(row.get('completion', '')).strip(),
                'category': category,
                'model_type': 'conversational',
                'quality_score': 0.8,  # Default quality score
                'tags': [category, 'imported'],
                'created_at': datetime.utcnow()
            }

            if example_data['prompt'] and example_data['completion']:  # Only add if both exist
                examples.append(example_data)

        if examples:
            result = await self.dataset_service.bulk_create('training', examples)
            print(f"✅ Imported {len(examples)} training examples for {category}")
        else:
            print(f"⚠️  No valid training examples found for {category}")

    async def import_all_data(self):
        """Import all data from all Excel files"""
        print("🚀 Starting sample data import...")

        for category, file_path in self.data_files.items():
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue

            print(f"\n📁 Processing {category} data from {file_path}")

            try:
                await self.import_problems(category, file_path)
                await self.import_assessments(category, file_path)
                await self.import_suggestions(category, file_path)
                await self.import_feedback_prompts(category, file_path)
                await self.import_next_actions(category, file_path)
                await self.import_training_examples(category, file_path)

            except Exception as e:
                print(f"❌ Error processing {category}: {e}")

        print("\n✅ Sample data import completed!")

    async def get_import_stats(self):
        """Get statistics of imported data"""
        stats = await self.dataset_service.get_dataset_stats()

        print("\n📊 Import Statistics:")
        for stat in stats:
            total_items = (stat.problems_count + stat.assessment_questions_count + 
                          stat.suggestions_count + stat.feedback_prompts_count + 
                          stat.next_actions_count + stat.training_examples_count)
            print(f"  {stat.domain}: {total_items} items (Problems: {stat.problems_count}, Assessments: {stat.assessment_questions_count}, Suggestions: {stat.suggestions_count}, Feedback: {stat.feedback_prompts_count}, Actions: {stat.next_actions_count}, Training: {stat.training_examples_count})")

async def main():
    """Main function to run the import"""
    importer = SampleDataImporter()

    try:
        await importer.initialize()
        await importer.import_all_data()
        await importer.get_import_stats()

    except Exception as e:
        print(f"❌ Import failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())