"""
Vector Database Service for Qdrant Integration
Handles connection management, health checks, and collection operations
"""

import logging
from typing import Dict, List, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    CreateCollection, CollectionInfo, CollectionStatus
)
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing Qdrant vector database operations"""

    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.collections = {
            "problems": "mental-health-problems",
            "assessments": "mental-health-assessments",
            "suggestions": "mental-health-suggestions",
            "feedback": "mental-health-feedback",
            "training": "mental-health-training"
        }
        self.vector_size = 384  # all-MiniLM-L6-v2 embedding size

    async def connect(self) -> bool:
        """Establish connection to Qdrant"""
        try:
            if settings.QDRANT_API_KEY:
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY
                )
            else:
                self.client = QdrantClient(url=settings.QDRANT_URL)

            # Test connection
            await self.health_check()
            logger.info("✅ Successfully connected to Qdrant")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {str(e)}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check Qdrant service health"""
        try:
            if not self.client:
                return {"status": "disconnected", "error": "No client connection"}

            # Get collections info
            collections = self.client.get_collections()

            return {
                "status": "healthy",
                "collections": len(collections.collections),
                "url": settings.QDRANT_URL
            }

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    async def create_collections(self) -> bool:
        """Create all required collections if they don't exist"""
        try:
            if not self.client:
                await self.connect()

            for collection_name in self.collections.values():
                await self._create_collection_if_not_exists(collection_name)

            logger.info("✅ All collections created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create collections: {str(e)}")
            return False

    async def _create_collection_if_not_exists(self, collection_name: str) -> bool:
        """Create a single collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            existing_collections = [c.name for c in collections.collections]

            if collection_name in existing_collections:
                logger.info(f"Collection '{collection_name}' already exists")
                return True

            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

            logger.info(f"✅ Created collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create collection '{collection_name}': {str(e)}")
            return False

    async def upsert_points(self, collection_name: str, points: List[PointStruct]) -> bool:
        """Insert or update points in a collection"""
        try:
            if not self.client:
                await self.connect()

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )

            logger.info(f"✅ Upserted {len(points)} points to {collection_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upsert points to {collection_name}: {str(e)}")
            return False

    async def search_similar(
        self,
        collection_name: str,
        vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar vectors in a collection"""
        try:
            if not self.client:
                await self.connect()

            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_conditions
            )

            # Convert to list of dicts
            results = []
            for point in search_result:
                results.append({
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload
                })

            return results

        except Exception as e:
            logger.error(f"❌ Search failed in {collection_name}: {str(e)}")
            return []

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            if not self.client:
                await self.connect()

            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"✅ Deleted collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete collection '{collection_name}': {str(e)}")
            return False

    async def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """Get information about a collection"""
        try:
            if not self.client:
                await self.connect()

            return self.client.get_collection(collection_name=collection_name)

        except Exception as e:
            logger.error(f"❌ Failed to get collection info for '{collection_name}': {str(e)}")
            return None

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        try:
            if not self.client:
                await self.connect()

            stats = {}
            collections = self.client.get_collections()

            for collection in collections.collections:
                try:
                    info = self.client.get_collection(collection_name=collection.name)
                    stats[collection.name] = {
                        "name": collection.name,
                        "status": info.status,
                        "vectors_count": info.vectors_count,
                        "points_count": info.points_count,
                        "segments_count": info.segments_count,
                        "config": {
                            "vector_size": info.config.params.vectors.size,
                            "distance": info.config.params.vectors.distance
                        }
                    }
                except Exception as e:
                    logger.warning(f"Failed to get stats for collection {collection.name}: {e}")
                    stats[collection.name] = {"error": str(e)}

            return stats

        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {str(e)}")
            return {"error": str(e)}

    async def close(self):
        """Close the Qdrant client connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Closed Qdrant connection")


# Global vector service instance
vector_service = VectorService()
