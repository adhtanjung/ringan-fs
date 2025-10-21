#!/usr/bin/env python3
"""
Training Examples Import Script

This script imports training examples from the JSON file into MongoDB
with proper field mapping and deduplication.
"""

import asyncio
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

# Add the backend directory to Python path
import sys
sys.path.append(str(Path(__file__).parent))

from app.services.dataset_management_service import dataset_management_service
from app.core.database import init_db
from app.models.dataset_models import UserIntent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrainingExamplesImporter:
    """Handles importing training examples with proper field mapping"""

    def __init__(self):
        self.stats = {
            'total_processed': 0,
            'successfully_imported': 0,
            'duplicates_skipped': 0,
            'validation_errors': 0,
            'import_errors': 0
        }
        self.existing_hashes = set()
        self.generated_ids = set()  # Track IDs generated in this session

    async def initialize(self):
        """Initialize the importer"""
        await init_db()

        # Initialize the dataset management service
        await dataset_management_service.initialize()

        await self.load_existing_hashes()

    async def load_existing_hashes(self):
        """Load existing training example hashes to prevent duplicates"""
        try:
            from app.core.database import get_mongodb
            db = get_mongodb()

            if db is None:
                logger.warning("MongoDB not available, skipping existing hash loading")
                self.existing_hashes = set()
                return

            # Get existing training examples and their hashes
            existing_examples = await db.mental_health_chat.training_examples.find({}, {"_record_hash": 1}).to_list(None)
            self.existing_hashes = {example.get("_record_hash") for example in existing_examples if example.get("_record_hash")}

            logger.info(f"Loaded {len(self.existing_hashes)} existing training example hashes")

        except Exception as e:
            logger.error(f"Failed to load existing hashes: {str(e)}")
            self.existing_hashes = set()

    def generate_content_hash(self, prompt: str, completion: str) -> str:
        """Generate hash for content deduplication"""
        prompt = prompt or ''
        completion = completion or ''
        content = f"{prompt.strip()}|{completion.strip()}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def clean_training_example(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and map training example data"""
        # Remove MongoDB-specific fields
        cleaned_item = {}
        for key, value in item.items():
            if key not in ['_id', '_record_hash', '_import_timestamp']:
                cleaned_item[key] = value

        # Map fields to the expected model structure
        prompt = item.get('prompt') or ''
        completion = item.get('completion') or ''

        mapped_item = {
            'example_id': self._generate_example_id(item),
            'domain': self._determine_domain(item),
            'problem': item.get('problem') or 'General mental health support',
            'conversation_id': str(item.get('ConversationID') or f"conv_{item.get('id', 'unknown')}"),
            'user_intent': self._determine_user_intent(item),
            'prompt': prompt.strip() if prompt else '',
            'completion': completion.strip() if completion else '',
            'context': None,
            'quality_score': 0.8,  # Default quality score
            'tags': self._generate_tags(item),
            '_record_hash': self.generate_content_hash(prompt, completion),
            '_import_timestamp': datetime.utcnow()
        }

        return mapped_item

    def _generate_example_id(self, item: Dict[str, Any]) -> str:
        """Generate a unique example ID in the format E_DOMAIN_###"""
        # Get domain prefix
        domain = self._determine_domain(item)
        domain_prefixes = {
            'anxiety': 'ANX',
            'stress': 'STR',
            'trauma': 'TRA',
            'depression': 'DEP',
            'general': 'GEN'
        }
        domain_prefix = domain_prefixes.get(domain, 'GEN')

        # Generate unique ID using content hash and timestamp
        content_hash = self.generate_content_hash(
            item.get('prompt', ''),
            item.get('completion', '')
        )

        # Use hash + current timestamp to ensure uniqueness
        import time
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
        hash_num = int(content_hash[:2], 16) % 100   # First 2 chars of hash

        # Combine to create a unique 3-4 digit number
        unique_num = (hash_num * 100 + timestamp % 100) % 1000

        # Ensure it's at least 3 digits
        if unique_num < 100:
            unique_num += 100

        # Generate the ID
        generated_id = f"E_{domain_prefix}_{unique_num:03d}"

        # If this ID was already generated in this session, add a suffix
        counter = 1
        original_id = generated_id
        while generated_id in self.generated_ids:
            generated_id = f"{original_id}_{counter:02d}"
            counter += 1

        # Track this ID
        self.generated_ids.add(generated_id)

        return generated_id

    def _determine_domain(self, item: Dict[str, Any]) -> str:
        """Determine the domain from the content"""
        prompt = (item.get('prompt') or '').lower()
        completion = (item.get('completion') or '').lower()
        content = f"{prompt} {completion}"

        # Simple keyword-based domain detection
        if any(word in content for word in ['anxiety', 'panic', 'worry', 'nervous']):
            return 'anxiety'
        elif any(word in content for word in ['stress', 'pressure', 'overwhelmed', 'burnout']):
            return 'stress'
        elif any(word in content for word in ['trauma', 'ptsd', 'flashback', 'trigger']):
            return 'trauma'
        elif any(word in content for word in ['depression', 'sad', 'hopeless', 'suicidal']):
            return 'depression'
        else:
            return 'general'

    def _determine_user_intent(self, item: Dict[str, Any]) -> str:
        """Determine user intent from the prompt"""
        prompt = (item.get('prompt') or '').lower()

        # Simple intent detection based on keywords - using valid enum values
        if any(word in prompt for word in ['help', 'what can i do', 'how to', 'advice']):
            return 'seeking_help'
        elif any(word in prompt for word in ['feel', 'feeling', 'emotion', 'mood']):
            return 'emotional_expression'
        elif any(word in prompt for word in ['problem', 'issue', 'difficulty', 'struggle']):
            return 'problem_identification'
        elif any(word in prompt for word in ['question', 'why', 'what is', 'explain']):
            return 'clarification'
        else:
            return 'problem_identification'  # Default to a valid enum value

    def _generate_tags(self, item: Dict[str, Any]) -> List[str]:
        """Generate tags based on content"""
        tags = []
        prompt = (item.get('prompt') or '').lower()
        completion = (item.get('completion') or '').lower()
        content = f"{prompt} {completion}"

        # Add domain-based tags
        domain = self._determine_domain(item)
        tags.append(domain)

        # Add content-based tags
        if 'breathing' in content:
            tags.append('breathing_exercise')
        if 'meditation' in content or 'mindfulness' in content:
            tags.append('meditation')
        if 'therapy' in content or 'counseling' in content:
            tags.append('therapy')
        if 'emergency' in content or 'crisis' in content:
            tags.append('crisis_support')

        return tags

    async def import_training_examples(self, json_file_path: str) -> Dict[str, Any]:
        """Import training examples from JSON file"""
        try:
            logger.info(f"Starting import of training examples from {json_file_path}")

            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            logger.info(f"Loaded {len(raw_data)} training examples from JSON file")

            # Process each training example
            for item in raw_data:
                self.stats['total_processed'] += 1

                # Clean and map the item
                cleaned_item = self.clean_training_example(item)

                # Check for duplicates
                content_hash = cleaned_item['_record_hash']
                if content_hash in self.existing_hashes:
                    self.stats['duplicates_skipped'] += 1
                    continue

                # Validate required fields
                if not cleaned_item['prompt'] or not cleaned_item['completion']:
                    self.stats['validation_errors'] += 1
                    logger.warning(f"Skipping item with missing prompt/completion: {cleaned_item.get('example_id')}")
                    continue

                try:
                    # Import the training example using the correct method
                    result = await dataset_management_service.create_item("training_examples", cleaned_item)

                    if result:
                        self.stats['successfully_imported'] += 1
                        self.existing_hashes.add(content_hash)

                        if self.stats['successfully_imported'] % 50 == 0:
                            logger.info(f"Imported {self.stats['successfully_imported']} training examples...")
                    else:
                        self.stats['validation_errors'] += 1
                        logger.warning(f"Import failed for {cleaned_item.get('example_id')}")

                except Exception as e:
                    self.stats['import_errors'] += 1
                    logger.error(f"Failed to import {cleaned_item.get('example_id')}: {str(e)}")

            logger.info("Training examples import completed")
            return self.stats

        except Exception as e:
            logger.error(f"Failed to import training examples: {str(e)}")
            return {"error": str(e)}

async def main():
    """Main function to run the import"""
    importer = TrainingExamplesImporter()
    await importer.initialize()

    # Import training examples
    json_file_path = "data/mental_health_db.training_examples.json"
    results = await importer.import_training_examples(json_file_path)

    # Print results
    print("\n" + "="*50)
    print("TRAINING EXAMPLES IMPORT RESULTS")
    print("="*50)
    print(f"Total processed: {results.get('total_processed', 0)}")
    print(f"Successfully imported: {results.get('successfully_imported', 0)}")
    print(f"Duplicates skipped: {results.get('duplicates_skipped', 0)}")
    print(f"Validation errors: {results.get('validation_errors', 0)}")
    print(f"Import errors: {results.get('import_errors', 0)}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
