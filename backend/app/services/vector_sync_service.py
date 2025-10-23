"""Vector Database Sync Service

This service handles synchronization between MongoDB collections and Qdrant vector database.
It creates embeddings for text content and stores them in appropriate vector collections
for semantic search functionality.
"""

import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.core.database import get_mongodb
from app.services.vector_service import VectorService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class VectorSyncService:
    """Service for syncing MongoDB data to Qdrant vector database"""

    def __init__(self):
        self.vector_service = VectorService()
        self.embedding_service = EmbeddingService()
        self.mongodb = None

        # Collection mapping from MongoDB to Qdrant
        self.collection_mapping = {
            'problems': 'mental-health-problems',
            'assessments': 'mental-health-assessments',
            'suggestions': 'mental-health-suggestions',
            'feedback_prompts': 'mental-health-feedback',
            'training_examples': 'mental-health-training'
        }

    async def initialize(self):
        """Initialize the sync service"""
        try:
            # Initialize MongoDB connection
            mongodb_client = get_mongodb()
            if mongodb_client is None:
                logger.warning("⚠️ MongoDB not available")
                self.mongodb = None
                return

            self.mongodb = mongodb_client.mental_health_db  # Use the correct database

            # Initialize vector service
            await self.vector_service.initialize()

            # Initialize embedding service
            await self.embedding_service.initialize()

            logger.info("VectorSyncService initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize VectorSyncService: {str(e)}")
            raise

    async def sync_all_collections(self) -> Dict[str, Any]:
        """Sync all MongoDB collections to vector database"""
        sync_results = {}
        total_synced = 0

        try:
            logger.info("Starting sync of all collections...")

            for mongo_collection, qdrant_collection in self.collection_mapping.items():
                try:
                    logger.info(f"Syncing {mongo_collection} to {qdrant_collection}...")

                    result = await self.sync_collection(mongo_collection, qdrant_collection)
                    sync_results[mongo_collection] = result
                    total_synced += result.get('synced_count', 0)

                    logger.info(f"Completed sync for {mongo_collection}: {result}")

                except Exception as e:
                    logger.error(f"Failed to sync {mongo_collection}: {str(e)}")
                    sync_results[mongo_collection] = {
                        'success': False,
                        'error': str(e),
                        'synced_count': 0
                    }

            logger.info(f"Sync completed. Total items synced: {total_synced}")

            return {
                'success': True,
                'total_synced': total_synced,
                'collections': sync_results,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to sync all collections: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_synced': total_synced,
                'collections': sync_results,
                'timestamp': datetime.utcnow().isoformat()
            }

    async def sync_collection(self, mongo_collection: str, qdrant_collection: str) -> Dict[str, Any]:
        """Sync a specific MongoDB collection to Qdrant"""
        try:
            # Get data from MongoDB
            collection = self.mongodb[mongo_collection]
            documents = await collection.find({"is_active": True}).to_list(length=None)

            if not documents:
                logger.warning(f"No active documents found in {mongo_collection}")
                return {
                    'success': True,
                    'synced_count': 0,
                    'message': 'No active documents to sync'
                }

            # Prepare vectors for Qdrant
            vectors_data = []

            for doc in documents:
                try:
                    # Extract text content based on collection type
                    text_content = self._extract_text_content(doc, mongo_collection)

                    if not text_content:
                        logger.warning(f"No text content found for document {doc.get('_id')}")
                        continue

                    # Generate embedding
                    embedding = await self.embedding_service.generate_embedding(text_content)

                    # Prepare vector data
                    vector_data = {
                        'id': self._objectid_to_uuid(doc['_id']),
                        'vector': embedding,
                        'payload': {
                            'text': text_content,
                            'collection': mongo_collection,
                            'document_id': str(doc['_id']),
                            'domain': doc.get('domain', 'general'),
                            'created_at': doc.get('created_at', datetime.utcnow().isoformat()),
                            'metadata': self._extract_metadata(doc, mongo_collection)
                        }
                    }

                    vectors_data.append(vector_data)

                except Exception as e:
                    logger.error(f"Failed to process document {doc.get('_id')}: {str(e)}")
                    continue

            if not vectors_data:
                logger.warning(f"No valid vectors generated for {mongo_collection}")
                return {
                    'success': True,
                    'synced_count': 0,
                    'message': 'No valid vectors generated'
                }

            # Upsert vectors to Qdrant
            await self.vector_service.upsert_vectors(qdrant_collection, vectors_data)

            logger.info(f"Successfully synced {len(vectors_data)} vectors to {qdrant_collection}")

            return {
                'success': True,
                'synced_count': len(vectors_data),
                'total_documents': len(documents),
                'collection': qdrant_collection
            }

        except Exception as e:
            logger.error(f"Failed to sync collection {mongo_collection}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'synced_count': 0
            }

    def _extract_text_content(self, doc: Dict[str, Any], collection_name: str) -> Optional[str]:
        """Extract text content from document based on collection type"""
        try:
            if collection_name == 'problems':
                # Combine problem name and description
                name = doc.get('problem_name', '')
                description = doc.get('description', '')
                return f"{name} {description}".strip()

            elif collection_name == 'assessments':
                # Use question text
                return doc.get('question_text', '')

            elif collection_name == 'suggestions':
                # Use suggestion text (handle both old and new formats)
                suggestion_text = doc.get('suggestion_text', '')
                title = doc.get('title', '')
                content = doc.get('content', '')

                if suggestion_text:
                    return suggestion_text
                elif title and content:
                    return f"{title} {content}"
                else:
                    return title or content or ''

            elif collection_name == 'feedback_prompts':
                # Use prompt text
                return doc.get('prompt_text', '')

            elif collection_name == 'training_examples':
                # Combine prompt and completion
                prompt = doc.get('prompt', '')
                completion = doc.get('completion', '')
                return f"{prompt} {completion}".strip()

            else:
                logger.warning(f"Unknown collection type: {collection_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to extract text content: {str(e)}")
            return None

    def _extract_metadata(self, doc: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        """Extract relevant metadata from document"""
        metadata = {
            'collection_type': collection_name,
            'is_active': doc.get('is_active', True)
        }

        # Add collection-specific metadata
        if collection_name == 'problems':
            metadata.update({
                'category': doc.get('category', ''),
                'sub_category_id': doc.get('sub_category_id', ''),
                'severity_level': doc.get('severity_level', '')
            })

        elif collection_name == 'assessments':
            metadata.update({
                'question_id': doc.get('question_id', ''),
                'sub_category_id': doc.get('sub_category_id', ''),
                'response_type': doc.get('response_type', ''),
                'clusters': doc.get('clusters', '')
            })

        elif collection_name == 'suggestions':
            metadata.update({
                'suggestion_id': doc.get('suggestion_id', ''),
                'sub_category_id': doc.get('sub_category_id', ''),
                'cluster': doc.get('cluster', ''),
                'priority': doc.get('priority', ''),
                'effectiveness_rating': doc.get('effectiveness_rating', 0)
            })

        elif collection_name == 'feedback_prompts':
            metadata.update({
                'prompt_id': doc.get('prompt_id', ''),
                'sub_category_id': doc.get('sub_category_id', ''),
                'stage': doc.get('stage', ''),
                'prompt_type': doc.get('prompt_type', '')
            })

        elif collection_name == 'training_examples':
            metadata.update({
                'example_id': doc.get('example_id', ''),
                'user_intent': doc.get('user_intent', ''),
                'quality_score': doc.get('quality_score', 0),
                'conversation_id': doc.get('conversation_id', '')
            })

        return metadata

    def _objectid_to_uuid(self, object_id) -> str:
        """Convert MongoDB ObjectId to UUID string for Qdrant compatibility"""
        # Convert ObjectId to string and create a deterministic UUID
        object_id_str = str(object_id)
        # Use the ObjectId string to generate a deterministic UUID
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, object_id_str))

    async def _get_qdrant_count_simple(self, collection_name: str) -> int:
        """Get Qdrant collection count using a simple approach that avoids Pydantic validation issues"""
        try:
            if not self.vector_service.client:
                await self.vector_service.connect()

            # Use the count API directly
            try:
                result = self.vector_service.client.count(
                    collection_name=collection_name,
                    exact=True
                )
                return result.count
            except Exception as count_error:
                logger.warning(f"Count API failed for {collection_name}: {count_error}")

                # Fallback: try to get collections list and find the specific collection
                try:
                    collections = self.vector_service.client.get_collections()
                    for collection in collections.collections:
                        if collection.name == collection_name:
                            # Try to get basic info without full validation
                            try:
                                # Use the collection info directly from the collections list
                                return getattr(collection, 'vectors_count', 0)
                            except:
                                # If that fails, return 0 but assume sync worked
                                logger.info(f"Collection {collection_name} exists but exact count unavailable")
                                return 0

                    # Collection not found
                    logger.warning(f"Collection {collection_name} not found")
                    return 0
                except Exception as fallback_error:
                    logger.error(f"Fallback method also failed for {collection_name}: {fallback_error}")
                    return 0

        except Exception as e:
            logger.error(f"Failed to get simple count for {collection_name}: {str(e)}")
            return 0

    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status for all collections"""
        try:
            status = {}

            for mongo_collection, qdrant_collection in self.collection_mapping.items():
                try:
                    # Get MongoDB count
                    collection = self.mongodb[mongo_collection]
                    mongo_count = await collection.count_documents({"is_active": True})

                    # Get Qdrant count using simple method
                    qdrant_count = await self._get_qdrant_count_simple(qdrant_collection)

                    status[mongo_collection] = {
                        'mongo_count': mongo_count,
                        'qdrant_count': qdrant_count,
                        'synced': mongo_count == qdrant_count,
                        'collection': qdrant_collection
                    }

                except Exception as e:
                    logger.error(f"Failed to get status for {mongo_collection}: {str(e)}")
                    status[mongo_collection] = {
                        'error': str(e),
                        'synced': False
                    }

            return {
                'success': True,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get sync status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
