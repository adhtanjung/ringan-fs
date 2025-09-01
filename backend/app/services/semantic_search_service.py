"""
Semantic Search Service for Mental Health Data
Integrates vector database and embedding services for intelligent search
"""

import logging
import time
from typing import List, Dict, Optional, Any
from qdrant_client.models import PointStruct

from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service
from app.models.vector_models import SearchRequest, SearchResponse, SearchResult

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Service for semantic search operations on mental health data"""

    def __init__(self):
        self.collections = {
            "problems": "mental-health-problems",
            "assessments": "mental-health-assessments",
            "suggestions": "mental-health-suggestions",
            "feedback": "mental-health-feedback",
            "training": "mental-health-training"
        }

    async def initialize(self) -> bool:
        """Initialize the semantic search service"""
        try:
            # Initialize vector service
            await vector_service.connect()
            await vector_service.create_collections()

            # Initialize embedding service
            await embedding_service.initialize()

            logger.info("✅ Semantic search service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize semantic search service: {str(e)}")
            return False

    async def search_problems(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.4,
        domain_filter: Optional[str] = None
    ) -> SearchResponse:
        """Search for mental health problems"""
        try:
            start_time = time.time()

            # Generate query embedding
            query_embedding = await embedding_service.generate_embedding(query)
            if not query_embedding:
                return SearchResponse(
                    success=False,
                    results=[],
                    total_found=0,
                    query_time=time.time() - start_time,
                    error="Failed to generate query embedding"
                )

            # Prepare filters
            filters = None
            if domain_filter:
                filters = {"must": [{"key": "domain", "match": {"value": domain_filter}}]}

            # Search in problems collection
            search_results = await vector_service.search_similar(
                collection_name=self.collections["problems"],
                vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filters
            )

            # Convert to SearchResult objects
            results = []
            for result in search_results:
                results.append(SearchResult(
                    id=str(result["id"]),  # Convert integer ID to string
                    score=result["score"],
                    payload=result["payload"]
                ))

            query_time = time.time() - start_time

            return SearchResponse(
                success=True,
                results=results,
                total_found=len(results),
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"❌ Problem search failed: {str(e)}")
            return SearchResponse(
                success=False,
                results=[],
                total_found=0,
                query_time=0.0,
                error=str(e)
            )

    async def search_assessment_questions(
        self,
        problem_description: str,
        sub_category_id: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.6
    ) -> SearchResponse:
        """Search for relevant assessment questions"""
        try:
            start_time = time.time()

            # Generate embedding for problem description
            query_embedding = await embedding_service.generate_embedding(problem_description)
            if not query_embedding:
                return SearchResponse(
                    success=False,
                    results=[],
                    total_found=0,
                    query_time=time.time() - start_time,
                    error="Failed to generate query embedding"
                )

            # Prepare filters
            filters = None
            if sub_category_id:
                filters = {"must": [{"key": "sub_category_id", "match": {"value": sub_category_id}}]}

            # Search in assessments collection
            search_results = await vector_service.search_similar(
                collection_name=self.collections["assessments"],
                vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filters
            )

            # Convert to SearchResult objects
            results = []
            for result in search_results:
                results.append(SearchResult(
                    id=str(result["id"]),  # Convert integer ID to string
                    score=result["score"],
                    payload=result["payload"]
                ))

            query_time = time.time() - start_time

            return SearchResponse(
                success=True,
                results=results,
                total_found=len(results),
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"❌ Assessment search failed: {str(e)}")
            return SearchResponse(
                success=False,
                results=[],
                total_found=0,
                query_time=0.0,
                error=str(e)
            )

    async def search_therapeutic_suggestions(
        self,
        problem_description: str,
        sub_category_id: Optional[str] = None,
        cluster: Optional[str] = None,
        limit: int = 5,
        score_threshold: float = 0.4
    ) -> SearchResponse:
        """Search for therapeutic suggestions"""
        try:
            start_time = time.time()

            # Generate embedding for problem description
            query_embedding = await embedding_service.generate_embedding(problem_description)
            if not query_embedding:
                return SearchResponse(
                    success=False,
                    results=[],
                    total_found=0,
                    query_time=time.time() - start_time,
                    error="Failed to generate query embedding"
                )

            # Prepare filters
            filters = {"must": []}
            if sub_category_id:
                filters["must"].append({"key": "sub_category_id", "match": {"value": sub_category_id}})
            if cluster:
                filters["must"].append({"key": "cluster", "match": {"value": cluster}})

            if not filters["must"]:
                filters = None

            # Search in suggestions collection
            search_results = await vector_service.search_similar(
                collection_name=self.collections["suggestions"],
                vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filters
            )

            # Convert to SearchResult objects
            results = []
            for result in search_results:
                results.append(SearchResult(
                    id=str(result["id"]),  # Convert integer ID to string
                    score=result["score"],
                    payload=result["payload"]
                ))

            query_time = time.time() - start_time

            return SearchResponse(
                success=True,
                results=results,
                total_found=len(results),
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"❌ Suggestion search failed: {str(e)}")
            return SearchResponse(
                success=False,
                results=[],
                total_found=0,
                query_time=0.0,
                error=str(e)
            )

    async def search_feedback_prompts(
        self,
        user_response: Optional[str] = None,
        context: Optional[str] = None,
        stage: Optional[str] = None,
        limit: int = 3,
        score_threshold: float = 0.6
    ) -> SearchResponse:
        """Search for appropriate feedback prompts"""
        try:
            start_time = time.time()

            # Generate embedding for user response or context
            query_text = user_response or context or "feedback prompt"
            query_embedding = await embedding_service.generate_embedding(query_text)
            if not query_embedding:
                return SearchResponse(
                    success=False,
                    results=[],
                    total_found=0,
                    query_time=time.time() - start_time,
                    error="Failed to generate query embedding"
                )

            # Prepare filters
            filters = None
            if stage:
                filters = {"must": [{"key": "stage", "match": {"value": stage}}]}

            # Search in feedback collection
            search_results = await vector_service.search_similar(
                collection_name=self.collections["feedback"],
                vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filters
            )

            # Convert to SearchResult objects
            results = []
            for result in search_results:
                results.append(SearchResult(
                    id=str(result["id"]),  # Convert integer ID to string
                    score=result["score"],
                    payload=result["payload"]
                ))

            query_time = time.time() - start_time

            return SearchResponse(
                success=True,
                results=results,
                total_found=len(results),
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"❌ Feedback search failed: {str(e)}")
            return SearchResponse(
                success=False,
                results=[],
                total_found=0,
                query_time=0.0,
                error=str(e)
            )

    async def search_next_actions(
        self,
        feedback_context: str,
        limit: int = 3,
        score_threshold: float = 0.6
    ) -> SearchResponse:
        """Search for appropriate next actions based on feedback context"""
        try:
            start_time = time.time()

            # Generate embedding for feedback context
            query_embedding = await embedding_service.generate_embedding(feedback_context)
            if not query_embedding:
                return SearchResponse(
                    success=False,
                    results=[],
                    total_found=0,
                    query_time=time.time() - start_time,
                    error="Failed to generate query embedding"
                )

            # Search in next_actions collection (fallback to suggestions if not available)
            collection_name = self.collections.get("next_actions", self.collections["suggestions"])
            search_results = await vector_service.search_similar(
                collection_name=collection_name,
                vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )

            # Convert to SearchResult objects
            results = []
            for result in search_results:
                results.append(SearchResult(
                    id=str(result["id"]),
                    score=result["score"],
                    payload=result["payload"]
                ))

            query_time = time.time() - start_time

            return SearchResponse(
                success=True,
                results=results,
                total_found=len(results),
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"❌ Next actions search failed: {str(e)}")
            return SearchResponse(
                success=False,
                results=[],
                total_found=0,
                query_time=0.0,
                error=str(e)
            )

    async def search_training_examples(
        self,
        user_input: str,
        domain: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.4
    ) -> SearchResponse:
        """Search for relevant training examples"""
        try:
            start_time = time.time()

            # Generate embedding for user input
            query_embedding = await embedding_service.generate_embedding(user_input)
            if not query_embedding:
                return SearchResponse(
                    success=False,
                    results=[],
                    total_found=0,
                    query_time=time.time() - start_time,
                    error="Failed to generate query embedding"
                )

            # Prepare filters
            filters = None
            if domain:
                filters = {"must": [{"key": "domain", "match": {"value": domain}}]}

            # Search in training collection
            search_results = await vector_service.search_similar(
                collection_name=self.collections["training"],
                vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filters
            )

            # Convert to SearchResult objects
            results = []
            for result in search_results:
                results.append(SearchResult(
                    id=str(result["id"]),  # Convert integer ID to string
                    score=result["score"],
                    payload=result["payload"]
                ))

            query_time = time.time() - start_time

            return SearchResponse(
                success=True,
                results=results,
                total_found=len(results),
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"❌ Training example search failed: {str(e)}")
            return SearchResponse(
                success=False,
                results=[],
                total_found=0,
                query_time=0.0,
                error=str(e)
            )

    async def multi_collection_search(
        self,
        query: str,
        collections: List[str],
        limit_per_collection: int = 3,
        score_threshold: float = 0.6
    ) -> Dict[str, SearchResponse]:
        """Search across multiple collections"""
        try:
            results = {}

            for collection in collections:
                if collection == "problems":
                    results[collection] = await self.search_problems(
                        query, limit_per_collection, score_threshold
                    )
                elif collection == "assessments":
                    results[collection] = await self.search_assessment_questions(
                        query, limit=limit_per_collection, score_threshold=score_threshold
                    )
                elif collection == "suggestions":
                    results[collection] = await self.search_therapeutic_suggestions(
                        query, limit=limit_per_collection, score_threshold=score_threshold
                    )
                elif collection == "feedback":
                    results[collection] = await self.search_feedback_prompts(
                        query, limit=limit_per_collection, score_threshold=score_threshold
                    )
                elif collection == "training":
                    results[collection] = await self.search_training_examples(
                        query, limit=limit_per_collection, score_threshold=score_threshold
                    )

            return results

        except Exception as e:
            logger.error(f"❌ Multi-collection search failed: {str(e)}")
            return {}

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        try:
            stats = {}

            for collection_name in self.collections.values():
                info = await vector_service.get_collection_info(collection_name)
                if info:
                    stats[collection_name] = {
                        "points_count": info.points_count,
                        "segments_count": info.segments_count,
                        "status": info.status
                    }
                else:
                    stats[collection_name] = {"error": "Failed to get collection info"}

            return stats

        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {str(e)}")
            return {"error": str(e)}


# Global semantic search service instance
semantic_search_service = SemanticSearchService()
