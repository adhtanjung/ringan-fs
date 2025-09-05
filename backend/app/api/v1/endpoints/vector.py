"""
Vector Database API Endpoints
Handles vectorization, search, and collection management
"""

import logging
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from qdrant_client.models import PointStruct

from app.models.vector_models import (
    VectorizationRequest, VectorizationResponse,
    SearchRequest, SearchResponse,
    ProblemCategory, AssessmentQuestion, TherapeuticSuggestion,
    FeedbackPrompt, TrainingExample
)
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service
from app.services.semantic_search_service import semantic_search_service
from app.core.auth import get_current_user_optional, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/vectorize", response_model=VectorizationResponse)
async def vectorize_text(request: VectorizationRequest):
    """Vectorize a single text with metadata"""
    try:
        # Generate embedding
        embedding = await embedding_service.generate_embedding(request.text)

        if not embedding:
            return VectorizationResponse(
                success=False,
                error="Failed to generate embedding"
            )

        return VectorizationResponse(
            success=True,
            vector=embedding,
            metadata={
                "model": embedding_service.model_name,
                "vector_size": embedding_service.vector_size,
                "text": request.text,
                "user_metadata": request.metadata
            }
        )

    except Exception as e:
        logger.error(f"Vectorization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vectorize/batch", response_model=List[VectorizationResponse])
async def vectorize_texts_batch(requests: List[VectorizationRequest]):
    """Vectorize multiple texts with metadata"""
    try:
        # Prepare text-metadata pairs
        text_metadata_pairs = [
            {"text": req.text, "metadata": req.metadata}
            for req in requests
        ]

        # Generate embeddings
        results = await embedding_service.generate_embeddings_with_metadata_batch(
            text_metadata_pairs
        )

        # Convert to response format
        responses = []
        for result in results:
            if result:
                responses.append(VectorizationResponse(
                    success=True,
                    vector=result["embedding"],
                    metadata=result["metadata"]
                ))
            else:
                responses.append(VectorizationResponse(
                    success=False,
                    error="Failed to generate embedding"
                ))

        return responses

    except Exception as e:
        logger.error(f"Batch vectorization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """Perform semantic search in specified collection"""
    try:
        # Initialize services if needed
        await semantic_search_service.initialize()

        # Route to appropriate search method
        if request.collection == "mental-health-problems":
            return await semantic_search_service.search_problems(
                request.query,
                request.limit,
                request.score_threshold,
                request.filters.get("domain") if request.filters else None
            )
        elif request.collection == "mental-health-assessments":
            return await semantic_search_service.search_assessment_questions(
                request.query,
                request.filters.get("sub_category_id") if request.filters else None,
                request.limit,
                request.score_threshold
            )
        elif request.collection == "mental-health-suggestions":
            return await semantic_search_service.search_therapeutic_suggestions(
                request.query,
                request.filters.get("sub_category_id") if request.filters else None,
                request.filters.get("cluster") if request.filters else None,
                request.limit,
                request.score_threshold
            )
        elif request.collection == "mental-health-feedback":
            return await semantic_search_service.search_feedback_prompts(
                request.query,
                request.filters.get("stage") if request.filters else None,
                request.limit,
                request.score_threshold
            )
        elif request.collection == "mental-health-training":
            return await semantic_search_service.search_training_examples(
                request.query,
                request.filters.get("domain") if request.filters else None,
                request.limit,
                request.score_threshold
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown collection: {request.collection}"
            )

    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/problems")
async def search_problems(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Maximum number of results"),
    score_threshold: float = Query(0.7, description="Minimum similarity score"),
    domain: Optional[str] = Query(None, description="Filter by domain")
):
    """Search for mental health problems"""
    try:
        await semantic_search_service.initialize()
        return await semantic_search_service.search_problems(
            query, limit, score_threshold, domain
        )
    except Exception as e:
        logger.error(f"Problem search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/assessments")
async def search_assessments(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    score_threshold: float = Query(0.6, description="Minimum similarity score"),
    sub_category_id: Optional[str] = Query(None, description="Filter by sub-category")
):
    """Search for assessment questions"""
    try:
        await semantic_search_service.initialize()
        return await semantic_search_service.search_assessment_questions(
            query, sub_category_id, limit, score_threshold
        )
    except Exception as e:
        logger.error(f"Assessment search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/suggestions")
async def search_suggestions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Maximum number of results"),
    score_threshold: float = Query(0.7, description="Minimum similarity score"),
    sub_category_id: Optional[str] = Query(None, description="Filter by sub-category"),
    cluster: Optional[str] = Query(None, description="Filter by cluster")
):
    """Search for therapeutic suggestions"""
    try:
        await semantic_search_service.initialize()
        return await semantic_search_service.search_therapeutic_suggestions(
            query, sub_category_id, cluster, limit, score_threshold
        )
    except Exception as e:
        logger.error(f"Suggestion search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/feedback")
async def search_feedback(
    query: str = Query(..., description="Search query"),
    limit: int = Query(3, description="Maximum number of results"),
    score_threshold: float = Query(0.6, description="Minimum similarity score"),
    stage: Optional[str] = Query(None, description="Filter by stage")
):
    """Search for feedback prompts"""
    try:
        await semantic_search_service.initialize()
        return await semantic_search_service.search_feedback_prompts(
            query, stage, limit, score_threshold
        )
    except Exception as e:
        logger.error(f"Feedback search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/multi")
async def multi_collection_search(
    query: str = Query(..., description="Search query"),
    collections: List[str] = Query(..., description="Collections to search in"),
    limit_per_collection: int = Query(3, description="Results per collection"),
    score_threshold: float = Query(0.6, description="Minimum similarity score")
):
    """Search across multiple collections"""
    try:
        await semantic_search_service.initialize()
        return await semantic_search_service.multi_collection_search(
            query, collections, limit_per_collection, score_threshold
        )
    except Exception as e:
        logger.error(f"Multi-collection search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/stats")
async def get_collection_stats(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """Get statistics for all collections"""
    try:
        await vector_service.connect()
        # Use vector_service.get_collection_stats() directly which handles config properly
        stats_data = await vector_service.get_collection_stats()
        
        # Transform the data to match frontend expectations
        collections = []
        for collection_name, stats in stats_data.items():
            if "error" not in stats:
                collection_data = {
                    "name": collection_name,
                    "status": stats.get("status", "unknown"),
                    "points_count": stats.get("points_count", 0),
                    "segments_count": stats.get("segments_count", 0),
                    "vectors_count": stats.get("vectors_count", 0),
                    "vector_size": stats.get("config", {}).get("vector_size", 384),
                    "distance": stats.get("config", {}).get("distance", "cosine")
                }
                
                # Add the full config if available
                if "config" in stats:
                    collection_data["config"] = {
                        "params": {
                            "vectors": {
                                "size": stats["config"]["vector_size"],
                                "distance": stats["config"]["distance"]
                            }
                        }
                    }
                
                collections.append(collection_data)
            else:
                # Include error collections for debugging
                collections.append({
                    "name": collection_name,
                    "status": "error",
                    "error": stats["error"],
                    "points_count": 0,
                    "segments_count": 0,
                    "vector_size": 0,
                    "distance": "unknown"
                })
        
        return {
            "collections": collections,
            "total_collections": len(collections),
            "healthy_collections": len([c for c in collections if c["status"] != "error"])
        }
        
    except Exception as e:
        logger.error(f"Failed to get collection stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def vector_health_check(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """Check vector database and embedding service health"""
    try:
        # Check vector service
        vector_health = await vector_service.health_check()

        # Check embedding service
        embedding_info = embedding_service.get_model_info()

        return {
            "vector_service": vector_health,
            "embedding_service": embedding_info,
            "status": "healthy" if vector_health["status"] == "healthy" else "unhealthy"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/collections/create")
async def create_collections(
    current_user: Dict = Depends(get_current_user)
):
    """Create all required collections"""
    try:
        await vector_service.connect()
        success = await vector_service.create_collections()

        if success:
            return {
                "success": True,
                "message": "Collections created successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to create collections"
            }

    except Exception as e:
        logger.error(f"Failed to create collections: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@router.delete("/collections/{collection_name}")
async def delete_collection(
    collection_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete a specific collection"""
    try:
        await vector_service.connect()
        success = await vector_service.delete_collection(collection_name)

        if success:
            return {
                "success": True,
                "message": f"Collection '{collection_name}' deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to delete collection"
            }

    except Exception as e:
        logger.error(f"Failed to delete collection: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/collections/{collection_name}/info")
async def get_collection_info(
    collection_name: str,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """Get information about a specific collection"""
    try:
        await vector_service.connect()
        info = await vector_service.get_collection_info(collection_name)

        if info:
            return {
                "name": info.name,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status,
                "config": info.config
            }
        else:
            raise HTTPException(status_code=404, detail="Collection not found")

    except Exception as e:
        logger.error(f"Failed to get collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
