"""Dataset Management Service

Provides CRUD operations for all dataset types with validation,
vector database synchronization, and bulk operations.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from bson import ObjectId
import asyncio

from app.core.database import get_mongodb
from app.services.dataset_validation_service import dataset_validation_service
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service
from app.models.dataset_models import (
    ProblemCategoryModel, AssessmentQuestionModel, TherapeuticSuggestionModel,
    FeedbackPromptModel, NextActionModel, FineTuningExampleModel,
    BulkOperationResult, ValidationResult, DatasetStatsModel
)

logger = logging.getLogger(__name__)


class DatasetManagementService:
    """Service for managing mental health datasets with CRUD operations"""

    def __init__(self):
        self.db = None
        self.collections = {
            'problems': 'problems',
            'assessments': 'assessments',
            'suggestions': 'suggestions',
            'feedback_prompts': 'feedback_prompts',
            'next_actions': 'next_actions',
            'training_examples': 'training_examples'
        }
        self.model_classes = {
            'problems': ProblemCategoryModel,
            'assessments': AssessmentQuestionModel,
            'suggestions': TherapeuticSuggestionModel,
            'feedback_prompts': FeedbackPromptModel,
            'next_actions': NextActionModel,
            'training_examples': FineTuningExampleModel
        }

    def _get_mock_data(self, data_type: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Return mock data when database is not available"""
        mock_data = {
            'problems': [
                {
                    'id': '1',
                    'category_id': 'STRESS_001',
                    'sub_category_id': 'WORK_STRESS_001',
                    'domain': 'stress',
                    'category': 'Work Stress',
                    'sub_category': 'Deadline Pressure',
                    'problem_statement': 'Feeling overwhelmed by tight deadlines at work',
                    'severity_level': 'moderate',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                },
                {
                    'id': '2',
                    'category_id': 'ANXIETY_001',
                    'sub_category_id': 'SOCIAL_ANXIETY_001',
                    'domain': 'anxiety',
                    'category': 'Social Anxiety',
                    'sub_category': 'Public Speaking',
                    'problem_statement': 'Fear of speaking in public or group settings',
                    'severity_level': 'high',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            ],
            'assessments': [
                {
                    'id': '1',
                    'question_id': 'STRESS_Q001',
                    'sub_category_id': 'WORK_STRESS_001',
                    'question_text': 'How often do you feel overwhelmed by your workload?',
                    'question_type': 'scale',
                    'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always'],
                    'scoring_weights': [0, 1, 2, 3, 4],
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            ],
            'suggestions': [
                {
                    'id': '1',
                    'suggestion_id': 'STRESS_SUG001',
                    'sub_category_id': 'WORK_STRESS_001',
                    'suggestion_text': 'Try breaking large tasks into smaller, manageable chunks',
                    'suggestion_type': 'coping_strategy',
                    'effectiveness_rating': 4.2,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            ],
            'feedback_prompts': [
                {
                    'id': '1',
                    'prompt_id': 'FEEDBACK_001',
                    'sub_category_id': 'WORK_STRESS_001',
                    'prompt_text': 'How did this suggestion work for you?',
                    'prompt_type': 'effectiveness',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            ],
            'next_actions': [
                {
                    'id': '1',
                    'action_id': 'ACTION_001',
                    'sub_category_id': 'WORK_STRESS_001',
                    'action_text': 'Schedule a meeting with your supervisor to discuss workload',
                    'action_type': 'immediate',
                    'priority_level': 'high',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            ],
            'training_examples': [
                {
                    'id': '1',
                    'example_id': 'TRAIN_001',
                    'sub_category_id': 'WORK_STRESS_001',
                    'user_input': 'I am feeling very stressed about my work deadlines',
                    'ai_response': 'I understand that work deadlines can be very stressful. Let me help you explore some strategies to manage this stress.',
                    'context': 'work_stress_conversation',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            ]
        }

        items = mock_data.get(data_type, [])
        total = len(items)

        # Apply pagination
        paginated_items = items[skip:skip + limit]

        return {
            'items': paginated_items,
            'total': total,
            'skip': skip,
            'limit': limit,
            'has_more': skip + len(paginated_items) < total
        }

    async def initialize(self):
        """Initialize the dataset management service"""
        try:
            mongodb_client = get_mongodb()
            logger.info(f"🔍 MongoDB client status: {mongodb_client is not None}")

            if mongodb_client is None:
                logger.warning("⚠️ MongoDB not available, using mock data for development")
                self.db = None
                return

            self.db = mongodb_client.mental_health_db
            logger.info(f"🔍 Database object set: {self.db is not None}")

            # Initialize validation service
            await dataset_validation_service.initialize()

            # Ensure indexes for better performance
            await self._create_indexes()

            logger.info("✅ Dataset management service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize dataset management service: {str(e)}")
            # Don't raise - allow service to work with mock data
            self.db = None

    async def _create_indexes(self):
        """Create database indexes for better performance"""
        if self.db is None:
            return

        try:
            # Problems collection indexes
            await self.db.problems.create_index("category_id", unique=True)
            await self.db.problems.create_index("sub_category_id", unique=True)
            await self.db.problems.create_index("domain")

            # Assessments collection indexes
            await self.db.assessments.create_index("question_id", unique=True)
            await self.db.assessments.create_index("sub_category_id")

            # Suggestions collection indexes
            await self.db.suggestions.create_index("suggestion_id", unique=True)
            await self.db.suggestions.create_index("sub_category_id")

            # Feedback prompts collection indexes
            await self.db.feedback_prompts.create_index("prompt_id", unique=True)
            await self.db.feedback_prompts.create_index("next_action_id")

            # Next actions collection indexes
            await self.db.next_actions.create_index("action_id", unique=True)

            # Training examples collection indexes
            await self.db.training_examples.create_index("example_id", unique=True)
            await self.db.training_examples.create_index("domain")
            await self.db.training_examples.create_index("user_intent")

            logger.info("✅ Database indexes created successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create some indexes: {str(e)}")

    async def create_item(self, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item with validation and vector synchronization"""
        logger.info(f"🔍 create_item called for {data_type}, db status: {self.db is not None}")

        if data_type not in self.collections:
            raise ValueError(f"Unknown data type: {data_type}")

        if self.db is None:
            raise ValueError("Database not initialized. Cannot create items.")

        # Validate data
        validation_methods = {
            'problems': dataset_validation_service.validate_problem_category,
            'assessments': dataset_validation_service.validate_assessment_question,
            'suggestions': dataset_validation_service.validate_therapeutic_suggestion,
            'feedback_prompts': dataset_validation_service.validate_feedback_prompt,
            'next_actions': dataset_validation_service.validate_next_action,
            'training_examples': dataset_validation_service.validate_training_example
        }

        validation_result = await validation_methods[data_type](data)
        if not validation_result.is_valid:
            all_errors = []
            all_errors.extend(validation_result.errors)

            # Add field errors
            for field, field_errors in validation_result.field_errors.items():
                for error in field_errors:
                    all_errors.append(f"{field}: {error}")

            # Add foreign key errors if they exist
            if hasattr(validation_result, 'foreign_key_errors'):
                all_errors.extend(validation_result.foreign_key_errors)

            raise ValueError(f"Validation failed: {all_errors}")

        # Create model instance
        model_class = self.model_classes[data_type]
        model = model_class(**data)

        # Add timestamps
        model.created_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()

        # Insert into database with comprehensive error handling
        collection = getattr(self.db, self.collections[data_type])

        try:
            # Prepare document for insertion
            document = model.model_dump(exclude={'id'}, mode='json')
            logger.info(f"📝 Attempting to insert {data_type} document: {document}")

            # Use mode='json' to properly serialize datetime objects
            result = await collection.insert_one(document)

            # Verify insertion was successful
            if not result.inserted_id:
                raise Exception("MongoDB insert_one returned no inserted_id")

            logger.info(f"✅ MongoDB insert successful for {data_type}, inserted_id: {result.inserted_id}")

        except Exception as e:
            logger.error(f"❌ MongoDB insert failed for {data_type}: {str(e)}")
            logger.error(f"❌ Document that failed: {document}")
            raise Exception(f"Failed to insert {data_type} into MongoDB: {str(e)}")

        # Get the created item
        try:
            created_item = await collection.find_one({"_id": result.inserted_id})
            if not created_item:
                raise Exception(f"Could not retrieve created {data_type} item with id: {result.inserted_id}")

            created_item['id'] = str(created_item['_id'])
            del created_item['_id']

        except Exception as e:
            logger.error(f"❌ Failed to retrieve created {data_type} item: {str(e)}")
            raise Exception(f"Failed to retrieve created {data_type} item: {str(e)}")

        # Sync with vector database for relevant types
        try:
            if data_type in ['problems', 'assessments', 'suggestions']:
                await self._sync_to_vector_db(data_type, created_item, 'create')
        except Exception as e:
            logger.warning(f"⚠️ Vector database sync failed for {data_type} {created_item.get('id')}: {str(e)}")
            # Don't fail the entire operation if vector sync fails

        logger.info(f"✅ Created {data_type} item: {created_item.get('id')}")
        return created_item

    async def get_item(self, data_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single item by ID"""
        if data_type not in self.collections:
            raise ValueError(f"Unknown data type: {data_type}")

        collection = getattr(self.db, self.collections[data_type])
        item = await collection.find_one({"_id": ObjectId(item_id)})

        if item:
            item['id'] = str(item['_id'])
            del item['_id']

        return item

    async def get_items(self, data_type: str, filters: Optional[Dict[str, Any]] = None,
                       skip: int = 0, limit: int = 100, sort_by: str = "created_at",
                       sort_order: int = -1) -> Dict[str, Any]:
        """Get multiple items with filtering, pagination, and sorting"""
        if data_type not in self.collections:
            raise ValueError(f"Unknown data type: {data_type}")

        # Return mock data if database is not available
        if self.db is None:
            return self._get_mock_data(data_type, skip, limit)

        collection = getattr(self.db, self.collections[data_type])

        # Build query
        query = filters or {}

        # Get total count
        total = await collection.count_documents(query)

        # Get items with pagination and sorting
        cursor = collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)

        # Convert ObjectId to string
        for item in items:
            item['id'] = str(item['_id'])
            del item['_id']

        return {
            'items': items,
            'total': total,
            'skip': skip,
            'limit': limit,
            'has_more': skip + len(items) < total
        }

    async def update_item(self, data_type: str, item_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing item with validation and vector synchronization"""
        if data_type not in self.collections:
            raise ValueError(f"Unknown data type: {data_type}")

        # Get existing item
        existing_item = await self.get_item(data_type, item_id)
        if not existing_item:
            raise ValueError(f"Item not found: {item_id}")

        # Merge with existing data
        updated_data = {**existing_item, **data}
        updated_data['id'] = item_id  # Ensure ID is preserved for validation

        # Validate updated data
        validation_methods = {
            'problems': dataset_validation_service.validate_problem_category,
            'assessments': dataset_validation_service.validate_assessment_question,
            'suggestions': dataset_validation_service.validate_therapeutic_suggestion,
            'feedback_prompts': dataset_validation_service.validate_feedback_prompt,
            'next_actions': dataset_validation_service.validate_next_action,
            'training_examples': dataset_validation_service.validate_training_example
        }

        validation_result = await validation_methods[data_type](updated_data)
        if not validation_result.is_valid:
            raise ValueError(f"Validation failed: {validation_result.errors}")

        # Update timestamps
        data['updated_at'] = datetime.utcnow()

        # Update in database
        collection = getattr(self.db, self.collections[data_type])
        await collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": data}
        )

        # Get updated item
        updated_item = await self.get_item(data_type, item_id)

        # Sync with vector database for relevant types
        if data_type in ['problems', 'assessments', 'suggestions']:
            await self._sync_to_vector_db(data_type, updated_item, 'update')

        logger.info(f"✅ Updated {data_type} item: {item_id}")
        return updated_item

    async def delete_item(self, data_type: str, item_id: str) -> bool:
        """Delete an item and sync with vector database"""
        if data_type not in self.collections:
            raise ValueError(f"Unknown data type: {data_type}")

        # Get item before deletion for vector sync
        item = await self.get_item(data_type, item_id)
        if not item:
            raise ValueError(f"Item not found: {item_id}")

        # Delete from database
        collection = getattr(self.db, self.collections[data_type])
        result = await collection.delete_one({"_id": ObjectId(item_id)})

        if result.deleted_count == 0:
            return False

        # Sync with vector database for relevant types
        if data_type in ['problems', 'assessments', 'suggestions']:
            await self._sync_to_vector_db(data_type, item, 'delete')

        logger.info(f"✅ Deleted {data_type} item: {item_id}")
        return True

    async def bulk_create(self, data_type: str, items: List[Dict[str, Any]]) -> BulkOperationResult:
        """Create multiple items in bulk with validation"""
        result = BulkOperationResult(
            success=True,
            total_processed=len(items),
            successful=0,
            failed=0
        )

        for item_data in items:
            try:
                created_item = await self.create_item(data_type, item_data)
                result.successful += 1
                result.created_ids.append(created_item['id'])
            except Exception as e:
                result.failed += 1
                result.errors.append(f"Failed to create item: {str(e)}")

        result.success = result.failed == 0
        return result

    async def bulk_update(self, data_type: str, updates: List[Dict[str, Any]]) -> BulkOperationResult:
        """Update multiple items in bulk"""
        result = BulkOperationResult(
            success=True,
            total_processed=len(updates),
            successful=0,
            failed=0
        )

        for update_data in updates:
            try:
                item_id = update_data.pop('id')
                updated_item = await self.update_item(data_type, item_id, update_data)
                result.successful += 1
                result.updated_ids.append(updated_item['id'])
            except Exception as e:
                result.failed += 1
                result.errors.append(f"Failed to update item: {str(e)}")

        result.success = result.failed == 0
        return result

    async def get_dataset_stats(self) -> List[DatasetStatsModel]:
        """Get statistics for all datasets"""
        stats = []

        for domain in ['stress', 'anxiety', 'trauma', 'general']:
            try:
                problems_count = await self.db.problems.count_documents({"domain": domain})
                assessments_count = await self.db.assessments.count_documents({
                    "sub_category_id": {"$regex": f"^{domain.upper()[:3]}"}
                })
                suggestions_count = await self.db.suggestions.count_documents({
                    "sub_category_id": {"$regex": f"^{domain.upper()[:3]}"}
                })
                feedback_prompts_count = await self.db.feedback_prompts.count_documents({})
                next_actions_count = await self.db.next_actions.count_documents({})
                training_examples_count = await self.db.training_examples.count_documents({"domain": domain})

                # Get last updated timestamp
                last_updated_doc = await self.db.problems.find_one(
                    {"domain": domain},
                    sort=[("updated_at", -1)]
                )
                last_updated = last_updated_doc.get('updated_at', datetime.utcnow()) if last_updated_doc else datetime.utcnow()

                stats.append(DatasetStatsModel(
                    domain=domain,
                    problems_count=problems_count,
                    assessment_questions_count=assessments_count,
                    suggestions_count=suggestions_count,
                    feedback_prompts_count=feedback_prompts_count,
                    next_actions_count=next_actions_count,
                    training_examples_count=training_examples_count,
                    last_updated=last_updated
                ))
            except Exception as e:
                logger.error(f"Failed to get stats for domain {domain}: {str(e)}")

        return stats

    async def _sync_to_vector_db(self, data_type: str, item: Dict[str, Any], operation: str):
        """Sync changes to vector database"""
        try:
            if operation == 'delete':
                # Remove from vector database
                if data_type == 'problems':
                    collection_name = vector_service.collections.get('problems', 'mental-health-problems')
                    await vector_service.delete_points(collection_name, [item['id']])
                elif data_type == 'assessments':
                    collection_name = vector_service.collections.get('assessments', 'mental-health-assessments')
                    await vector_service.delete_points(collection_name, [item['id']])
                elif data_type == 'suggestions':
                    collection_name = vector_service.collections.get('suggestions', 'mental-health-suggestions')
                    await vector_service.delete_points(collection_name, [item['id']])

            elif operation in ['create', 'update']:
                # Ensure collections exist first
                await vector_service.create_collections()

                # Add or update in vector database
                if data_type == 'problems':
                    # Create embedding for problem
                    text_to_embed = f"{item['problem_name']} {item['description']}"
                    embedding = await embedding_service.generate_embedding(text_to_embed)

                    # Convert MongoDB ObjectId to UUID format for Qdrant
                    import uuid
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, item['id']))

                    point = {
                        'id': point_id,
                        'vector': embedding,
                        'payload': {
                            'domain': item['domain'],
                            'category': item['category'],
                            'category_id': item['category_id'],
                            'sub_category_id': item['sub_category_id'],
                            'problem_name': item['problem_name'],
                            'description': item['description'],
                            'type': 'problem'
                        }
                    }

                    if operation == 'create':
                        collection_name = vector_service.collections.get('problems', 'mental-health-problems')
                        await vector_service.upsert_points(collection_name, [point])
                    else:
                        collection_name = vector_service.collections.get('problems', 'mental-health-problems')
                        await vector_service.upsert_points(collection_name, [point])

                elif data_type == 'assessments':
                    # Create embedding for assessment question
                    embedding = await embedding_service.generate_embedding(item['question_text'])

                    # Convert MongoDB ObjectId to UUID format for Qdrant
                    import uuid
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, item['id']))

                    point = {
                        'id': point_id,
                        'vector': embedding,
                        'payload': {
                            'question_id': item['question_id'],
                            'sub_category_id': item['sub_category_id'],
                            'question_text': item['question_text'],
                            'response_type': item['response_type'],
                            'type': 'assessment'
                        }
                    }

                    collection_name = vector_service.collections.get('assessments', 'mental-health-assessments')
                    await vector_service.upsert_points(collection_name, [point])

                elif data_type == 'suggestions':
                    # Create embedding for suggestion
                    embedding = await embedding_service.generate_embedding(item['suggestion_text'])

                    # Convert MongoDB ObjectId to UUID format for Qdrant
                    import uuid
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, item['id']))

                    point = {
                        'id': point_id,
                        'vector': embedding,
                        'payload': {
                            'suggestion_id': item['suggestion_id'],
                            'sub_category_id': item['sub_category_id'],
                            'suggestion_text': item['suggestion_text'],
                            'cluster': item.get('cluster'),
                            'type': 'suggestion'
                        }
                    }

                    collection_name = vector_service.collections.get('suggestions', 'mental-health-suggestions')
                    await vector_service.upsert_points(collection_name, [point])

            logger.info(f"✅ Vector DB sync completed for {data_type} {operation}")

        except Exception as e:
            logger.error(f"❌ Vector DB sync failed for {data_type} {operation}: {str(e)}")
            # Don't raise - vector sync failure shouldn't break the main operation


# Global instance
dataset_management_service = DatasetManagementService()