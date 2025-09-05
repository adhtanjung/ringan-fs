"""
Data Models for Vector Database Operations
Pydantic schemas for mental health data structures
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ResponseType(str, Enum):
    """Assessment response types"""
    SCALE = "scale"
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"


class FeedbackStage(str, Enum):
    """Feedback prompt stages"""
    POST_SUGGESTION = "post_suggestion"
    ONGOING = "ongoing"


class NextAction(str, Enum):
    """Next action after feedback"""
    CONTINUE_SAME = "continue_same"
    SHOW_PROBLEM_MENU = "show_problem_menu"
    END_SESSION = "end_session"
    ESCALATE = "escalate"
    SCHEDULE_FOLLOWUP = "schedule_followup"


class ProblemCategory(BaseModel):
    """Mental health problem category model"""
    category_id: str = Field(..., description="Unique category identifier")
    sub_category_id: str = Field(..., description="Sub-category identifier")
    category: str = Field(..., description="Main category name")
    problem_name: str = Field(..., description="Problem name")
    description: str = Field(..., description="Problem description")
    domain: str = Field(..., description="Mental health domain (stress, anxiety, trauma, general)")

    class Config:
        schema_extra = {
            "example": {
                "category_id": "s001",
                "sub_category_id": "s001_01",
                "category": "Relationship Stress",
                "problem_name": "Communication Issues",
                "description": "Difficulty in communicating effectively with partner",
                "domain": "stress"
            }
        }


class AssessmentQuestion(BaseModel):
    """Assessment question model"""
    question_id: str = Field(..., description="Unique question identifier")
    sub_category_id: str = Field(..., description="Related sub-category")
    batch_id: str = Field(..., description="Batch identifier for flow control")
    question_text: str = Field(..., description="Question text")
    response_type: ResponseType = Field(..., description="Type of response expected")
    next_step: Optional[str] = Field(None, description="Next question identifier")
    clusters: Optional[List[str]] = Field(None, description="Related clusters")
    domain: str = Field(..., description="Mental health domain")
    scale_min: Optional[int] = Field(None, description="Minimum value for scale questions")
    scale_max: Optional[int] = Field(None, description="Maximum value for scale questions")
    options: Optional[List[str]] = Field(None, description="Options for multiple choice questions")

    class Config:
        schema_extra = {
            "example": {
                "question_id": "q001",
                "sub_category_id": "s001_01",
                "batch_id": "b001",
                "question_text": "Seberapa sering Anda mengalami kesulitan berkomunikasi dengan pasangan?",
                "response_type": "scale",
                "next_step": "q002",
                "clusters": ["communication", "relationship"],
                "domain": "stress"
            }
        }


class TherapeuticSuggestion(BaseModel):
    """Therapeutic suggestion model"""
    suggestion_id: str = Field(..., description="Unique suggestion identifier")
    sub_category_id: str = Field(..., description="Related sub-category")
    cluster: str = Field(..., description="Suggestion cluster")
    suggestion_text: str = Field(..., description="Therapeutic suggestion text")
    resource_link: Optional[str] = Field(None, description="External resource link")
    evidence_based: bool = Field(True, description="Whether suggestion is evidence-based")
    domain: str = Field(..., description="Mental health domain")

    class Config:
        schema_extra = {
            "example": {
                "suggestion_id": "sug001",
                "sub_category_id": "s001_01",
                "cluster": "communication",
                "suggestion_text": "Coba teknik komunikasi aktif dengan mendengarkan tanpa interupsi",
                "resource_link": "https://example.com/active-listening",
                "evidence_based": True,
                "domain": "stress"
            }
        }


class FeedbackPrompt(BaseModel):
    """Feedback prompt model"""
    prompt_id: str = Field(..., description="Unique prompt identifier")
    stage: FeedbackStage = Field(..., description="Feedback stage")
    prompt_text: str = Field(..., description="Feedback prompt text")
    next_action: NextAction = Field(..., description="Next action after feedback")
    domain: str = Field(..., description="Mental health domain")

    class Config:
        schema_extra = {
            "example": {
                "prompt_id": "fp001",
                "stage": "post_suggestion",
                "prompt_text": "Apakah saran ini membantu? Bagaimana perasaan Anda sekarang?",
                "next_action": "continue_same",
                "domain": "stress"
            }
        }


class TrainingExample(BaseModel):
    """Training example for AI model fine-tuning"""
    example_id: str = Field(..., description="Unique example identifier")
    problem: str = Field(..., description="Problem description")
    conversation_id: str = Field(..., description="Conversation identifier")
    prompt: str = Field(..., description="User prompt")
    completion: str = Field(..., description="AI response")
    domain: str = Field(..., description="Mental health domain")
    sub_category_id: Optional[str] = Field(None, description="Related sub-category")

    class Config:
        schema_extra = {
            "example": {
                "example_id": "te001",
                "problem": "Communication issues with partner",
                "conversation_id": "conv001",
                "prompt": "Saya sulit berkomunikasi dengan pasangan saya",
                "completion": "Saya mengerti perasaan Anda. Mari kita bahas lebih lanjut tentang kesulitan komunikasi ini.",
                "domain": "stress",
                "sub_category_id": "s001_01"
            }
        }


class VectorPoint(BaseModel):
    """Vector database point model"""
    id: str = Field(..., description="Unique point identifier")
    vector: List[float] = Field(..., description="Embedding vector")
    payload: Dict[str, Any] = Field(..., description="Point metadata")

    class Config:
        schema_extra = {
            "example": {
                "id": "p001",
                "vector": [0.1, 0.2, 0.3, ...],
                "payload": {
                    "text": "Communication issues with partner",
                    "type": "problem",
                    "domain": "stress"
                }
            }
        }


class SearchResult(BaseModel):
    """Search result model"""
    id: str = Field(..., description="Result identifier")
    score: float = Field(..., description="Similarity score")
    payload: Dict[str, Any] = Field(..., description="Result metadata")

    class Config:
        schema_extra = {
            "example": {
                "id": "p001",
                "score": 0.85,
                "payload": {
                    "text": "Communication issues with partner",
                    "type": "problem",
                    "domain": "stress"
                }
            }
        }


class VectorizationRequest(BaseModel):
    """Request model for vectorization"""
    text: str = Field(..., description="Text to vectorize")
    metadata: Dict[str, Any] = Field(..., description="Text metadata")

    class Config:
        schema_extra = {
            "example": {
                "text": "Communication issues with partner",
                "metadata": {
                    "type": "problem",
                    "domain": "stress",
                    "category_id": "s001"
                }
            }
        }


class VectorizationResponse(BaseModel):
    """Response model for vectorization"""
    success: bool = Field(..., description="Vectorization success status")
    vector: Optional[List[float]] = Field(None, description="Generated embedding")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "vector": [0.1, 0.2, 0.3, ...],
                "metadata": {
                    "model": "all-MiniLM-L6-v2",
                    "vector_size": 384
                }
            }
        }


class SearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., description="Search query")
    collection: str = Field(..., description="Collection to search in")
    limit: int = Field(10, description="Maximum number of results")
    score_threshold: float = Field(0.4, description="Minimum similarity score")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")

    class Config:
        schema_extra = {
            "example": {
                "query": "communication problems",
                "collection": "mental-health-problems",
                "limit": 5,
                "score_threshold": 0.8,
                "filters": {"domain": "stress"}
            }
        }


class SearchResponse(BaseModel):
    """Response model for semantic search"""
    success: bool = Field(..., description="Search success status")
    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total results found")
    query_time: float = Field(..., description="Query execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "results": [
                    {
                        "id": "p001",
                        "score": 0.85,
                        "payload": {"text": "Communication issues", "type": "problem"}
                    }
                ],
                "total_found": 1,
                "query_time": 0.15
            }
        }
