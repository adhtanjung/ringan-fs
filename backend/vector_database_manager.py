#!/usr/bin/env python3
"""
Vector Database Manager for Mental Health Data Pipeline

This module implements a comprehensive vector database management system with:
- MongoDB-Qdrant synchronization
- Embedding generation using SentenceTransformer
- Hybrid storage architecture
- Real-time sync capabilities
- Performance optimization

Author: Mental Health Data Pipeline Team
Date: January 2025
"""

import numpy as np
import pandas as pd
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, 
    FieldCondition, MatchValue, UpdateStatus
)
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import json
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import uuid
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vector_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VectorStats:
    """Statistics for vector operations"""
    total_documents: int = 0
    total_embeddings: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    embedding_time: float = 0.0
    sync_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def total_time(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        total_ops = self.successful_syncs + self.failed_syncs
        if total_ops == 0:
            return 0.0
        return self.successful_syncs / total_ops

class VectorDatabaseError(Exception):
    """Custom exception for vector database operations"""
    pass

class EmbeddingGenerationError(Exception):
    """Custom exception for embedding generation"""
    pass

class VectorDatabaseManager:
    """
    Comprehensive vector database manager for MongoDB-Qdrant synchronization.
    
    Features:
    - Automatic embedding generation using SentenceTransformer
    - Real-time synchronization between MongoDB and Qdrant
    - Hybrid storage architecture
    - Batch processing for performance
    - Error handling and recovery
    - Performance monitoring
    """
    
    def __init__(self,
                 mongo_uri: str = "mongodb://localhost:27017/",
                 mongo_db: str = "mental_health_db",
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 embedding_model: str = "all-MiniLM-L6-v2",
                 vector_size: int = 384,
                 batch_size: int = 100,
                 max_workers: int = 4):
        """
        Initialize the VectorDatabaseManager.
        
        Args:
            mongo_uri: MongoDB connection string
            mongo_db: MongoDB database name
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            embedding_model: SentenceTransformer model name
            vector_size: Dimension of embedding vectors
            batch_size: Batch size for processing
            max_workers: Maximum number of worker threads
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.embedding_model_name = embedding_model
        self.vector_size = vector_size
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Initialize connections
        self.mongo_client = None
        self.mongo_database = None
        self.qdrant_client = None
        self.embedding_model = None
        
        # Statistics
        self.stats = VectorStats()
        
        # Text fields to embed for each collection type
        self.embedding_fields = {
            'anxiety': ['problem_description', 'solution', 'response', 'feedback'],
            'stress': ['problem_description', 'solution', 'response', 'feedback'],
            'trauma': ['problem_description', 'solution', 'response', 'feedback'],
            'general': ['text', 'content', 'description', 'response']
        }
        
        self._initialize_connections()
        logger.info("VectorDatabaseManager initialized successfully")
    
    def _initialize_connections(self) -> None:
        """Initialize all database connections and models."""
        try:
            # Initialize MongoDB
            self.mongo_client = MongoClient(self.mongo_uri)
            self.mongo_database = self.mongo_client[self.mongo_db]
            logger.info("MongoDB connection established")
            
            # Initialize Qdrant
            self.qdrant_client = QdrantClient(
                host=self.qdrant_host,
                port=self.qdrant_port
            )
            logger.info("Qdrant connection established")
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("Embedding model loaded successfully")
            
        except Exception as e:
            raise VectorDatabaseError(f"Failed to initialize connections: {e}")
    
    def create_collection(self, collection_name: str, recreate: bool = False) -> bool:
        """Create a Qdrant collection for storing vectors.
        
        Args:
            collection_name: Name of the collection
            recreate: Whether to recreate if exists
            
        Returns:
            True if successful
        """
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            collection_exists = any(col.name == collection_name for col in collections)
            
            if collection_exists:
                if recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.qdrant_client.delete_collection(collection_name)
                else:
                    logger.info(f"Collection {collection_name} already exists")
                    return True
            
            # Create collection
            logger.info(f"Creating Qdrant collection: {collection_name}")
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Collection {collection_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            raise VectorDatabaseError(f"Collection creation failed: {e}")
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        try:
            if not texts:
                return np.array([])
            
            # Filter out None and empty strings
            valid_texts = [str(text) for text in texts if text is not None and str(text).strip()]
            
            if not valid_texts:
                return np.array([])
            
            start_time = time.time()
            embeddings = self.embedding_model.encode(valid_texts, show_progress_bar=False)
            embedding_time = time.time() - start_time
            
            self.stats.embedding_time += embedding_time
            self.stats.total_embeddings += len(embeddings)
            
            logger.debug(f"Generated {len(embeddings)} embeddings in {embedding_time:.2f}s")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise EmbeddingGenerationError(f"Embedding generation failed: {e}")
    
    def extract_text_content(self, document: Dict[str, Any], collection_type: str) -> str:
        """Extract and combine text content from a document for embedding.
        
        Args:
            document: MongoDB document
            collection_type: Type of collection (anxiety, stress, trauma, etc.)
            
        Returns:
            Combined text content
        """
        # Determine which fields to use for embedding
        if collection_type in self.embedding_fields:
            fields = self.embedding_fields[collection_type]
        else:
            fields = self.embedding_fields['general']
        
        text_parts = []
        
        for field in fields:
            if field in document and document[field] is not None:
                text_value = str(document[field]).strip()
                if text_value:
                    text_parts.append(text_value)
        
        # If no specific fields found, try to extract any text content
        if not text_parts:
            for key, value in document.items():
                if (isinstance(value, str) and 
                    not key.startswith('_') and 
                    len(value.strip()) > 10):  # Minimum length threshold
                    text_parts.append(value.strip())
        
        # Combine all text parts
        combined_text = " ".join(text_parts)
        
        # Ensure minimum content length
        if len(combined_text.strip()) < 10:
            combined_text = f"Document ID: {document.get('id', 'unknown')} - {combined_text}"
        
        return combined_text
    
    def sync_collection(self, mongo_collection_name: str, qdrant_collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Synchronize a MongoDB collection with Qdrant.
        
        Args:
            mongo_collection_name: Name of MongoDB collection
            qdrant_collection_name: Name of Qdrant collection (defaults to mongo name)
            
        Returns:
            Synchronization results
        """
        if qdrant_collection_name is None:
            qdrant_collection_name = mongo_collection_name
        
        logger.info(f"Starting sync: {mongo_collection_name} -> {qdrant_collection_name}")
        
        sync_start = time.time()
        results = {
            'mongo_collection': mongo_collection_name,
            'qdrant_collection': qdrant_collection_name,
            'total_documents': 0,
            'processed_documents': 0,
            'failed_documents': 0,
            'errors': []
        }
        
        try:
            # Get MongoDB collection
            mongo_collection = self.mongo_database[mongo_collection_name]
            
            # Create Qdrant collection if it doesn't exist
            self.create_collection(qdrant_collection_name)
            
            # Get total document count
            total_docs = mongo_collection.count_documents({})
            results['total_documents'] = total_docs
            self.stats.total_documents += total_docs
            
            if total_docs == 0:
                logger.warning(f"No documents found in {mongo_collection_name}")
                return results
            
            logger.info(f"Processing {total_docs} documents from {mongo_collection_name}")
            
            # Determine collection type for text extraction
            collection_type = self._determine_collection_type(mongo_collection_name)
            
            # Process documents in batches
            batch_count = 0
            for batch_docs in self._get_document_batches(mongo_collection):
                try:
                    batch_result = self._process_document_batch(
                        batch_docs, qdrant_collection_name, collection_type
                    )
                    
                    results['processed_documents'] += batch_result['processed']
                    results['failed_documents'] += batch_result['failed']
                    results['errors'].extend(batch_result['errors'])
                    
                    batch_count += 1
                    if batch_count % 10 == 0:
                        logger.info(f"Processed {batch_count} batches ({results['processed_documents']} documents)")
                
                except Exception as e:
                    error_msg = f"Batch processing failed: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
                    results['failed_documents'] += len(batch_docs)
            
            sync_time = time.time() - sync_start
            self.stats.sync_time += sync_time
            
            if results['failed_documents'] == 0:
                self.stats.successful_syncs += 1
            else:
                self.stats.failed_syncs += 1
            
            logger.info(f"Sync completed in {sync_time:.2f}s: {results['processed_documents']} processed, {results['failed_documents']} failed")
            
        except Exception as e:
            error_msg = f"Collection sync failed: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            self.stats.failed_syncs += 1
            raise VectorDatabaseError(error_msg)
        
        return results
    
    def _determine_collection_type(self, collection_name: str) -> str:
        """Determine the type of collection based on its name."""
        name_lower = collection_name.lower()
        if 'anxiety' in name_lower:
            return 'anxiety'
        elif 'stress' in name_lower:
            return 'stress'
        elif 'trauma' in name_lower:
            return 'trauma'
        else:
            return 'general'
    
    def _get_document_batches(self, collection):
        """Generator that yields batches of documents from MongoDB collection."""
        skip = 0
        while True:
            batch = list(collection.find().skip(skip).limit(self.batch_size))
            if not batch:
                break
            yield batch
            skip += self.batch_size
    
    def _process_document_batch(self, documents: List[Dict], qdrant_collection: str, collection_type: str) -> Dict[str, Any]:
        """Process a batch of documents for vector storage.
        
        Args:
            documents: List of MongoDB documents
            qdrant_collection: Target Qdrant collection
            collection_type: Type of collection for text extraction
            
        Returns:
            Batch processing results
        """
        result = {
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Extract text content from all documents
            texts = []
            valid_docs = []
            
            for doc in documents:
                try:
                    text_content = self.extract_text_content(doc, collection_type)
                    if text_content.strip():
                        texts.append(text_content)
                        valid_docs.append(doc)
                    else:
                        logger.warning(f"No text content found for document {doc.get('_id')}")
                        result['failed'] += 1
                except Exception as e:
                    error_msg = f"Text extraction failed for document {doc.get('_id')}: {e}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed'] += 1
            
            if not texts:
                logger.warning("No valid texts found in batch")
                return result
            
            # Generate embeddings for all texts
            embeddings = self.generate_embeddings(texts)
            
            if len(embeddings) == 0:
                logger.warning("No embeddings generated for batch")
                result['failed'] += len(valid_docs)
                return result
            
            # Prepare points for Qdrant
            points = []
            for i, (doc, embedding) in enumerate(zip(valid_docs, embeddings)):
                try:
                    # Generate unique point ID
                    point_id = str(uuid.uuid4())
                    
                    # Prepare payload (metadata)
                    payload = {
                        'mongo_id': str(doc['_id']),
                        'document_id': doc.get('id', ''),
                        'collection_type': collection_type,
                        'text_content': texts[i][:1000],  # Truncate for storage
                        'import_timestamp': doc.get('_import_timestamp', datetime.utcnow()).isoformat()
                    }
                    
                    # Add other relevant fields to payload
                    for key, value in doc.items():
                        if (not key.startswith('_') and 
                            key not in payload and 
                            isinstance(value, (str, int, float, bool)) and
                            len(str(value)) < 500):  # Limit payload size
                            payload[key] = value
                    
                    points.append(PointStruct(
                        id=point_id,
                        vector=embedding.tolist(),
                        payload=payload
                    ))
                    
                except Exception as e:
                    error_msg = f"Point preparation failed for document {doc.get('_id')}: {e}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed'] += 1
            
            # Upload points to Qdrant
            if points:
                try:
                    upload_result = self.qdrant_client.upsert(
                        collection_name=qdrant_collection,
                        points=points
                    )
                    
                    if upload_result.status == UpdateStatus.COMPLETED:
                        result['processed'] += len(points)
                        logger.debug(f"Successfully uploaded {len(points)} points to Qdrant")
                    else:
                        error_msg = f"Qdrant upload failed with status: {upload_result.status}"
                        logger.error(error_msg)
                        result['errors'].append(error_msg)
                        result['failed'] += len(points)
                
                except Exception as e:
                    error_msg = f"Qdrant upload failed: {e}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed'] += len(points)
        
        except Exception as e:
            error_msg = f"Batch processing failed: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['failed'] += len(documents)
        
        return result
    
    def sync_all_collections(self) -> Dict[str, Any]:
        """Synchronize all MongoDB collections with Qdrant.
        
        Returns:
            Overall synchronization results
        """
        self.stats.start_time = datetime.utcnow()
        logger.info("Starting synchronization of all collections")
        
        results = {
            'collections_synced': [],
            'total_collections': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'overall_stats': None
        }
        
        try:
            # Get all collection names
            collection_names = self.mongo_database.list_collection_names()
            
            # Filter out system collections
            data_collections = [name for name in collection_names 
                              if not name.startswith('system.')]
            
            results['total_collections'] = len(data_collections)
            logger.info(f"Found {len(data_collections)} collections to sync")
            
            # Sync each collection
            for collection_name in data_collections:
                try:
                    sync_result = self.sync_collection(collection_name)
                    results['collections_synced'].append(sync_result)
                    
                    if sync_result['failed_documents'] == 0:
                        results['successful_collections'] += 1
                    else:
                        results['failed_collections'] += 1
                    
                    logger.info(f"Completed sync for {collection_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to sync collection {collection_name}: {e}")
                    results['failed_collections'] += 1
                    results['collections_synced'].append({
                        'mongo_collection': collection_name,
                        'error': str(e)
                    })
            
            self.stats.end_time = datetime.utcnow()
            results['overall_stats'] = asdict(self.stats)
            
            logger.info(f"All collections sync completed in {self.stats.total_time:.2f}s")
            logger.info(f"Success rate: {self.stats.success_rate:.2%}")
            
        except Exception as e:
            logger.error(f"Overall sync failed: {e}")
            raise VectorDatabaseError(f"Overall sync failed: {e}")
        
        return results
    
    def search_similar(self, query_text: str, collection_name: str, limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity.
        
        Args:
            query_text: Text to search for
            collection_name: Qdrant collection to search in
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.generate_embeddings([query_text])
            
            if len(query_embedding) == 0:
                return []
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding[0].tolist(),
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise VectorDatabaseError(f"Search failed: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current vector database statistics."""
        return asdict(self.stats)
    
    def close(self) -> None:
        """Close all database connections."""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
        
        if self.qdrant_client:
            # Qdrant client doesn't need explicit closing
            logger.info("Qdrant client closed")

def main():
    """Main function for testing the VectorDatabaseManager."""
    print("=" * 60)
    print("Mental Health Data Pipeline - Vector Database Manager")
    print("=" * 60)
    
    try:
        # Initialize manager
        manager = VectorDatabaseManager(
            mongo_uri="mongodb://localhost:27017/",
            mongo_db="mental_health_db",
            qdrant_host="localhost",
            qdrant_port=6333
        )
        
        # Sync all collections
        results = manager.sync_all_collections()
        
        # Save results
        with open('vector_sync_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nVector sync completed successfully!")
        print(f"Collections synced: {results['successful_collections']}/{results['total_collections']}")
        print(f"Total documents: {results['overall_stats']['total_documents']}")
        print(f"Total embeddings: {results['overall_stats']['total_embeddings']}")
        print(f"Success rate: {results['overall_stats'].success_rate:.2%}")
        print(f"Results saved to vector_sync_results.json")
        
    except Exception as e:
        logger.error(f"Vector sync failed: {e}")
        print(f"Vector sync failed: {e}")
    
    finally:
        if 'manager' in locals():
            manager.close()

if __name__ == "__main__":
    main()