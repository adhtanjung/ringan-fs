#!/usr/bin/env python3
"""
Data Synchronization Service for Mental Health Data Pipeline

This module implements a real-time synchronization service between MongoDB and Qdrant:
- Change stream monitoring for MongoDB
- Automatic vector updates on data changes
- Conflict resolution strategies
- Performance optimization
- Error handling and recovery

Author: Mental Health Data Pipeline Team
Date: January 2025
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from vector_database_manager import VectorDatabaseManager, VectorDatabaseError
from contextlib import contextmanager
import queue
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Types of database changes"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    REPLACE = "replace"

@dataclass
class SyncEvent:
    """Represents a synchronization event"""
    change_type: ChangeType
    collection_name: str
    document_id: str
    document_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class SyncStats:
    """Statistics for synchronization operations"""
    total_events: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    insert_events: int = 0
    update_events: int = 0
    delete_events: int = 0
    average_sync_time: float = 0.0
    start_time: Optional[datetime] = None
    last_sync_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_events == 0:
            return 0.0
        return self.successful_syncs / self.total_events
    
    @property
    def uptime(self) -> Optional[float]:
        if self.start_time:
            return (datetime.utcnow() - self.start_time).total_seconds()
        return None

class DataSynchronizationService:
    """
    Real-time data synchronization service between MongoDB and Qdrant.
    
    Features:
    - MongoDB change stream monitoring
    - Automatic vector database updates
    - Batch processing for performance
    - Error handling and retry logic
    - Conflict resolution
    - Performance monitoring
    """
    
    def __init__(self,
                 mongo_uri: str = "mongodb://localhost:27017/",
                 mongo_db: str = "mental_health_db",
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 batch_size: int = 50,
                 batch_timeout: float = 5.0,
                 max_retries: int = 3,
                 retry_delay: float = 2.0,
                 enable_change_streams: bool = True):
        """
        Initialize the DataSynchronizationService.
        
        Args:
            mongo_uri: MongoDB connection string
            mongo_db: MongoDB database name
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            batch_size: Number of events to batch together
            batch_timeout: Maximum time to wait for batch completion
            max_retries: Maximum retry attempts for failed operations
            retry_delay: Delay between retry attempts
            enable_change_streams: Whether to enable MongoDB change streams
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_change_streams = enable_change_streams
        
        # Initialize connections
        self.mongo_client = None
        self.mongo_database = None
        self.vector_manager = None
        
        # Synchronization state
        self.is_running = False
        self.sync_thread = None
        self.event_queue = queue.Queue()
        self.stats = SyncStats()
        
        # Event handlers
        self.event_handlers: Dict[ChangeType, List[Callable]] = {
            ChangeType.INSERT: [],
            ChangeType.UPDATE: [],
            ChangeType.DELETE: [],
            ChangeType.REPLACE: []
        }
        
        # Collections to monitor (empty means all collections)
        self.monitored_collections: List[str] = []
        
        self._initialize_connections()
        self._setup_signal_handlers()
        
        logger.info("DataSynchronizationService initialized")
    
    def _initialize_connections(self) -> None:
        """Initialize database connections."""
        try:
            # Initialize MongoDB
            self.mongo_client = MongoClient(self.mongo_uri)
            self.mongo_database = self.mongo_client[self.mongo_db]
            logger.info("MongoDB connection established for sync service")
            
            # Initialize Vector Database Manager
            self.vector_manager = VectorDatabaseManager(
                mongo_uri=self.mongo_uri,
                mongo_db=self.mongo_db,
                qdrant_host="localhost",
                qdrant_port=6333
            )
            logger.info("Vector database manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            raise
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def add_event_handler(self, change_type: ChangeType, handler: Callable[[SyncEvent], None]) -> None:
        """Add a custom event handler for specific change types.
        
        Args:
            change_type: Type of change to handle
            handler: Function to call when change occurs
        """
        self.event_handlers[change_type].append(handler)
        logger.info(f"Added event handler for {change_type.value} events")
    
    def set_monitored_collections(self, collections: List[str]) -> None:
        """Set which collections to monitor for changes.
        
        Args:
            collections: List of collection names to monitor
        """
        self.monitored_collections = collections
        logger.info(f"Monitoring collections: {collections}")
    
    def start(self) -> None:
        """Start the synchronization service."""
        if self.is_running:
            logger.warning("Synchronization service is already running")
            return
        
        self.is_running = True
        self.stats.start_time = datetime.utcnow()
        
        logger.info("Starting data synchronization service")
        
        # Start the synchronization thread
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        
        # Start change stream monitoring if enabled
        if self.enable_change_streams:
            self._start_change_stream_monitoring()
        
        logger.info("Data synchronization service started successfully")
    
    def stop(self) -> None:
        """Stop the synchronization service."""
        if not self.is_running:
            logger.warning("Synchronization service is not running")
            return
        
        logger.info("Stopping data synchronization service")
        self.is_running = False
        
        # Wait for sync thread to finish
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=10)
        
        # Close connections
        if self.vector_manager:
            self.vector_manager.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        logger.info("Data synchronization service stopped")
    
    def _start_change_stream_monitoring(self) -> None:
        """Start monitoring MongoDB change streams."""
        def monitor_changes():
            try:
                logger.info("Starting MongoDB change stream monitoring")
                
                # Create change stream pipeline
                pipeline = []
                if self.monitored_collections:
                    pipeline.append({
                        '$match': {
                            'ns.coll': {'$in': self.monitored_collections}
                        }
                    })
                
                # Watch for changes
                with self.mongo_database.watch(pipeline, full_document='updateLookup') as stream:
                    for change in stream:
                        if not self.is_running:
                            break
                        
                        try:
                            self._process_change_event(change)
                        except Exception as e:
                            logger.error(f"Error processing change event: {e}")
                
            except PyMongoError as e:
                logger.error(f"MongoDB change stream error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in change stream monitoring: {e}")
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitor_changes, daemon=True)
        monitor_thread.start()
    
    def _process_change_event(self, change: Dict[str, Any]) -> None:
        """Process a MongoDB change stream event.
        
        Args:
            change: Change stream event from MongoDB
        """
        try:
            operation_type = change['operationType']
            collection_name = change['ns']['coll']
            
            # Map MongoDB operation types to our ChangeType enum
            change_type_mapping = {
                'insert': ChangeType.INSERT,
                'update': ChangeType.UPDATE,
                'delete': ChangeType.DELETE,
                'replace': ChangeType.REPLACE
            }
            
            if operation_type not in change_type_mapping:
                logger.debug(f"Ignoring operation type: {operation_type}")
                return
            
            change_type = change_type_mapping[operation_type]
            
            # Extract document information
            document_id = str(change['documentKey']['_id'])
            document_data = change.get('fullDocument')
            
            # Create sync event
            sync_event = SyncEvent(
                change_type=change_type,
                collection_name=collection_name,
                document_id=document_id,
                document_data=document_data
            )
            
            # Add to processing queue
            self.event_queue.put(sync_event)
            self.stats.total_events += 1
            
            # Update operation-specific stats
            if change_type == ChangeType.INSERT:
                self.stats.insert_events += 1
            elif change_type == ChangeType.UPDATE:
                self.stats.update_events += 1
            elif change_type == ChangeType.DELETE:
                self.stats.delete_events += 1
            
            logger.debug(f"Queued {change_type.value} event for {collection_name}:{document_id}")
            
        except Exception as e:
            logger.error(f"Failed to process change event: {e}")
    
    def _sync_worker(self) -> None:
        """Worker thread that processes synchronization events."""
        logger.info("Sync worker thread started")
        
        batch_events = []
        last_batch_time = time.time()
        
        while self.is_running:
            try:
                # Try to get an event from the queue
                try:
                    event = self.event_queue.get(timeout=1.0)
                    batch_events.append(event)
                except queue.Empty:
                    # No events available, check if we should process current batch
                    pass
                
                current_time = time.time()
                batch_ready = (
                    len(batch_events) >= self.batch_size or
                    (batch_events and (current_time - last_batch_time) >= self.batch_timeout)
                )
                
                if batch_ready and batch_events:
                    self._process_event_batch(batch_events)
                    batch_events = []
                    last_batch_time = current_time
                
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                time.sleep(1)
        
        # Process remaining events before shutdown
        if batch_events:
            self._process_event_batch(batch_events)
        
        logger.info("Sync worker thread stopped")
    
    def _process_event_batch(self, events: List[SyncEvent]) -> None:
        """Process a batch of synchronization events.
        
        Args:
            events: List of sync events to process
        """
        if not events:
            return
        
        start_time = time.time()
        logger.info(f"Processing batch of {len(events)} sync events")
        
        # Group events by collection and operation type
        grouped_events = self._group_events(events)
        
        for (collection_name, change_type), event_group in grouped_events.items():
            try:
                self._process_event_group(collection_name, change_type, event_group)
                
                # Mark events as successful
                for event in event_group:
                    self.stats.successful_syncs += 1
                    
                    # Call custom event handlers
                    for handler in self.event_handlers[change_type]:
                        try:
                            handler(event)
                        except Exception as e:
                            logger.error(f"Event handler failed: {e}")
                
            except Exception as e:
                logger.error(f"Failed to process event group {collection_name}:{change_type.value}: {e}")
                
                # Handle failed events
                for event in event_group:
                    self._handle_failed_event(event, str(e))
        
        # Update timing statistics
        batch_time = time.time() - start_time
        self.stats.average_sync_time = (
            (self.stats.average_sync_time * (self.stats.successful_syncs - len(events)) + batch_time) /
            self.stats.successful_syncs if self.stats.successful_syncs > 0 else batch_time
        )
        self.stats.last_sync_time = datetime.utcnow()
        
        logger.debug(f"Batch processed in {batch_time:.2f}s")
    
    def _group_events(self, events: List[SyncEvent]) -> Dict[tuple, List[SyncEvent]]:
        """Group events by collection and change type for efficient processing."""
        grouped = {}
        
        for event in events:
            key = (event.collection_name, event.change_type)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(event)
        
        return grouped
    
    def _process_event_group(self, collection_name: str, change_type: ChangeType, events: List[SyncEvent]) -> None:
        """Process a group of events of the same type for the same collection.
        
        Args:
            collection_name: Name of the MongoDB collection
            change_type: Type of change operation
            events: List of events to process
        """
        logger.debug(f"Processing {len(events)} {change_type.value} events for {collection_name}")
        
        if change_type in [ChangeType.INSERT, ChangeType.UPDATE, ChangeType.REPLACE]:
            # For insert/update operations, re-sync the documents
            self._sync_documents_to_vector_db(collection_name, events)
            
        elif change_type == ChangeType.DELETE:
            # For delete operations, remove from vector database
            self._delete_from_vector_db(collection_name, events)
    
    def _sync_documents_to_vector_db(self, collection_name: str, events: List[SyncEvent]) -> None:
        """Sync documents to vector database.
        
        Args:
            collection_name: MongoDB collection name
            events: List of sync events
        """
        try:
            # Extract document IDs that need to be synced
            document_ids = [event.document_id for event in events if event.document_data]
            
            if not document_ids:
                logger.warning(f"No valid documents to sync for {collection_name}")
                return
            
            # Get the latest document data from MongoDB
            mongo_collection = self.mongo_database[collection_name]
            documents = list(mongo_collection.find({
                '_id': {'$in': [event.document_id for event in events]}
            }))
            
            if not documents:
                logger.warning(f"No documents found in MongoDB for {collection_name}")
                return
            
            # Use vector manager to process these specific documents
            collection_type = self.vector_manager._determine_collection_type(collection_name)
            qdrant_collection = collection_name
            
            # Ensure Qdrant collection exists
            self.vector_manager.create_collection(qdrant_collection)
            
            # Process documents
            batch_result = self.vector_manager._process_document_batch(
                documents, qdrant_collection, collection_type
            )
            
            logger.info(f"Synced {batch_result['processed']} documents to vector DB for {collection_name}")
            
            if batch_result['failed'] > 0:
                logger.warning(f"Failed to sync {batch_result['failed']} documents for {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to sync documents to vector DB: {e}")
            raise
    
    def _delete_from_vector_db(self, collection_name: str, events: List[SyncEvent]) -> None:
        """Delete documents from vector database.
        
        Args:
            collection_name: MongoDB collection name
            events: List of delete events
        """
        try:
            # For delete operations, we need to find and remove the corresponding vectors
            # This is more complex as we need to search by MongoDB document ID
            
            qdrant_collection = collection_name
            
            for event in events:
                try:
                    # Search for points with matching mongo_id in payload
                    search_result = self.vector_manager.qdrant_client.scroll(
                        collection_name=qdrant_collection,
                        scroll_filter={
                            "must": [
                                {
                                    "key": "mongo_id",
                                    "match": {
                                        "value": event.document_id
                                    }
                                }
                            ]
                        },
                        limit=100
                    )
                    
                    # Delete found points
                    point_ids = [point.id for point in search_result[0]]
                    
                    if point_ids:
                        self.vector_manager.qdrant_client.delete(
                            collection_name=qdrant_collection,
                            points_selector=point_ids
                        )
                        logger.debug(f"Deleted {len(point_ids)} vectors for document {event.document_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to delete vectors for document {event.document_id}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to delete from vector DB: {e}")
            raise
    
    def _handle_failed_event(self, event: SyncEvent, error_message: str) -> None:
        """Handle a failed synchronization event.
        
        Args:
            event: The failed sync event
            error_message: Error description
        """
        event.retry_count += 1
        self.stats.failed_syncs += 1
        
        logger.error(f"Sync failed for {event.collection_name}:{event.document_id} (attempt {event.retry_count}): {error_message}")
        
        # Retry logic
        if event.retry_count < self.max_retries:
            # Add back to queue for retry after delay
            def retry_event():
                time.sleep(self.retry_delay * event.retry_count)
                if self.is_running:
                    self.event_queue.put(event)
            
            retry_thread = threading.Thread(target=retry_event, daemon=True)
            retry_thread.start()
            
            logger.info(f"Scheduled retry {event.retry_count}/{self.max_retries} for {event.collection_name}:{event.document_id}")
        else:
            logger.error(f"Max retries exceeded for {event.collection_name}:{event.document_id}, giving up")
    
    def trigger_full_sync(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Trigger a full synchronization for one or all collections.
        
        Args:
            collection_name: Specific collection to sync, or None for all
            
        Returns:
            Synchronization results
        """
        logger.info(f"Triggering full sync for {collection_name or 'all collections'}")
        
        try:
            if collection_name:
                return self.vector_manager.sync_collection(collection_name)
            else:
                return self.vector_manager.sync_all_collections()
        except Exception as e:
            logger.error(f"Full sync failed: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current synchronization statistics."""
        stats_dict = asdict(self.stats)
        stats_dict['is_running'] = self.is_running
        stats_dict['queue_size'] = self.event_queue.qsize()
        return stats_dict
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the synchronization service."""
        return {
            'is_running': self.is_running,
            'uptime_seconds': self.stats.uptime,
            'queue_size': self.event_queue.qsize(),
            'success_rate': self.stats.success_rate,
            'last_sync': self.stats.last_sync_time.isoformat() if self.stats.last_sync_time else None,
            'total_events_processed': self.stats.total_events,
            'average_sync_time': self.stats.average_sync_time
        }

def main():
    """Main function for testing the DataSynchronizationService."""
    print("=" * 60)
    print("Mental Health Data Pipeline - Data Synchronization Service")
    print("=" * 60)
    
    try:
        # Initialize service
        sync_service = DataSynchronizationService(
            mongo_uri="mongodb://localhost:27017/",
            mongo_db="mental_health_db",
            enable_change_streams=True
        )
        
        # Add custom event handlers
        def log_insert_event(event: SyncEvent):
            logger.info(f"Custom handler: Document inserted in {event.collection_name}")
        
        sync_service.add_event_handler(ChangeType.INSERT, log_insert_event)
        
        # Start the service
        sync_service.start()
        
        print("Synchronization service started. Press Ctrl+C to stop.")
        print("Service will monitor for changes and sync automatically.")
        
        # Keep the service running
        try:
            while True:
                time.sleep(10)
                stats = sync_service.get_statistics()
                 success_rate = stats['successful_syncs'] / stats['total_events'] if stats['total_events'] > 0 else 0.0
                 print(f"Stats: {stats['total_events']} events, {success_rate:.2%} success rate")
        except KeyboardInterrupt:
            print("\nShutting down...")
        
    except Exception as e:
        logger.error(f"Service failed: {e}")
        print(f"Service failed: {e}")
    
    finally:
        if 'sync_service' in locals():
            sync_service.stop()

if __name__ == "__main__":
    main()