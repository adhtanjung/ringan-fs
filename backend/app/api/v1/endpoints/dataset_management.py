"""Dataset Management API Endpoints

Provides REST API endpoints for managing mental health datasets
with CRUD operations, validation, and bulk operations.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse

from app.services.dataset_management_service import dataset_management_service
from app.services.problems_data_cleaning_service import ProblemsDataCleaningService
from app.models.dataset_models import (
    ProblemCategoryModel, AssessmentQuestionModel, TherapeuticSuggestionModel,
    FeedbackPromptModel, NextActionModel, FineTuningExampleModel,
    BulkOperationResult, DatasetStatsModel
)
# TEMPORARILY DISABLED: Admin authentication import
# from app.core.auth import get_current_admin_user  # Assuming admin auth exists

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dataset", tags=["Dataset Management"])

# Data type mapping for validation
DATA_TYPES = {
    'problems': ProblemCategoryModel,
    'assessments': AssessmentQuestionModel,
    'suggestions': TherapeuticSuggestionModel,
    'feedback_prompts': FeedbackPromptModel,
    'next_actions': NextActionModel,
    'training_examples': FineTuningExampleModel
}


# Removed duplicate startup event - service is initialized in main.py lifespan
# @router.on_event("startup")
# async def startup_event():
#     """Initialize dataset management service on startup"""
#     await dataset_management_service.initialize()


# CRUD Operations for Problems
@router.post("/problems", response_model=Dict[str, Any])
async def create_problem(
    problem_data: ProblemCategoryModel,
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Create a new problem category with data cleaning and validation"""
    try:
        # Initialize data cleaning service
        cleaning_service = ProblemsDataCleaningService()

        # Validate and clean the problem data
        validation_result = cleaning_service.validate_problem_data(
            problem_data.model_dump(exclude={'id', 'created_at', 'updated_at'})
        )

        if not validation_result['is_valid']:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "errors": validation_result['errors'],
                    "warnings": validation_result['warnings']
                }
            )

        # Use cleaned data for creation
        cleaned_data = validation_result['cleaned_data']

        result = await dataset_management_service.create_item(
            "problems",
            cleaned_data
        )

        # Close cleaning service
        cleaning_service.close()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "data": result,
                "warnings": validation_result['warnings'] if validation_result['warnings'] else None
            }
        )
    except ValueError as e:
        logger.error(f"ValueError in create_problem: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Failed to create problem: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/problems/clean", response_model=Dict[str, Any])
async def clean_problems_data(
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Clean and standardize all problems data in the database"""
    try:
        cleaning_service = ProblemsDataCleaningService()

        # Get data quality report before cleaning
        before_report = cleaning_service.get_data_quality_report()

        # Clean all problems
        cleaning_results = cleaning_service.clean_all_problems()

        # Get data quality report after cleaning
        after_report = cleaning_service.get_data_quality_report()

        # Close cleaning service
        cleaning_service.close()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Problems data cleaning completed",
                "results": cleaning_results,
                "before_report": before_report,
                "after_report": after_report
            }
        )
    except Exception as e:
        import traceback
        logger.error(f"Failed to clean problems data: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/problems/quality-report", response_model=Dict[str, Any])
async def get_problems_quality_report(
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get data quality report for problems collection"""
    try:
        cleaning_service = ProblemsDataCleaningService()
        quality_report = cleaning_service.get_data_quality_report()
        cleaning_service.close()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "quality_report": quality_report
            }
        )
    except Exception as e:
        import traceback
        logger.error(f"Failed to get quality report: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/problems/{problem_id}")
async def get_problem(
    problem_id: str,
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get a specific problem by ID"""
    try:
        result = await dataset_management_service.get_item("problems", problem_id)
        if not result:
            raise HTTPException(status_code=404, detail="Problem not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get problem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/problems")
async def get_problems(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(1000, ge=1, le=10000, description="Number of items to return"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: int = Query(-1, description="Sort order: 1 for ascending, -1 for descending")
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get problems with filtering and pagination"""
    try:
        filters = {}
        if domain:
            filters["domain"] = domain
        if category:
            filters["category"] = category

        result = await dataset_management_service.get_items(
            "problems", filters, skip, limit, sort_by, sort_order
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Failed to get problems: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/problems/{problem_id}")
async def update_problem(
    problem_id: str,
    problem_data: Dict[str, Any]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Update a problem category"""
    try:
        result = await dataset_management_service.update_item(
            "problems", problem_id, problem_data
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update problem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/problems/{problem_id}")
async def delete_problem(
    problem_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Delete a problem category"""
    try:
        success = await dataset_management_service.delete_item("problems", problem_id)
        if not success:
            raise HTTPException(status_code=404, detail="Problem not found")
        return {"success": True, "message": "Problem deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete problem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# CRUD Operations for Assessment Questions
@router.post("/assessments", response_model=Dict[str, Any])
async def create_assessment(
    assessment_data: AssessmentQuestionModel
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Create a new assessment question"""
    try:
        result = await dataset_management_service.create_item(
            "assessments",
            assessment_data.dict(exclude={'id', 'created_at', 'updated_at'})
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "data": result}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/assessments/{assessment_id}")
async def get_assessment(
    assessment_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get a specific assessment question by ID"""
    try:
        result = await dataset_management_service.get_item("assessments", assessment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/assessments")
async def get_assessments(
    sub_category_id: Optional[str] = Query(None, description="Filter by sub-category ID"),
    response_type: Optional[str] = Query(None, description="Filter by response type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    sort_order: int = Query(-1)
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get assessment questions with filtering and pagination"""
    try:
        filters = {}
        if sub_category_id:
            filters["sub_category_id"] = sub_category_id
        if response_type:
            filters["response_type"] = response_type

        result = await dataset_management_service.get_items(
            "assessments", filters, skip, limit, sort_by, sort_order
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Failed to get assessments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/assessments/{assessment_id}")
async def update_assessment(
    assessment_id: str,
    assessment_data: Dict[str, Any]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Update an assessment question"""
    try:
        result = await dataset_management_service.update_item(
            "assessments", assessment_id, assessment_data
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/assessments/{assessment_id}")
async def delete_assessment(
    assessment_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Delete an assessment question"""
    try:
        success = await dataset_management_service.delete_item("assessments", assessment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return {"success": True, "message": "Assessment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# CRUD Operations for Suggestions
@router.post("/suggestions", response_model=Dict[str, Any])
async def create_suggestion(
    suggestion_data: TherapeuticSuggestionModel
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Create a new therapeutic suggestion"""
    try:
        result = await dataset_management_service.create_item(
            "suggestions",
            suggestion_data.dict(exclude={'id', 'created_at', 'updated_at'})
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "data": result}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/suggestions/{suggestion_id}")
async def get_suggestion(
    suggestion_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get a specific suggestion by ID"""
    try:
        result = await dataset_management_service.get_item("suggestions", suggestion_id)
        if not result:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/suggestions")
async def get_suggestions(
    sub_category_id: Optional[str] = Query(None, description="Filter by sub-category ID"),
    cluster: Optional[str] = Query(None, description="Filter by cluster"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    sort_order: int = Query(-1)
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get therapeutic suggestions with filtering and pagination"""
    try:
        filters = {}
        if sub_category_id:
            filters["sub_category_id"] = sub_category_id
        if cluster:
            filters["cluster"] = cluster

        result = await dataset_management_service.get_items(
            "suggestions", filters, skip, limit, sort_by, sort_order
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Failed to get suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/suggestions/{suggestion_id}")
async def update_suggestion(
    suggestion_id: str,
    suggestion_data: Dict[str, Any]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Update a therapeutic suggestion"""
    try:
        result = await dataset_management_service.update_item(
            "suggestions", suggestion_id, suggestion_data
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/suggestions/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Delete a therapeutic suggestion"""
    try:
        success = await dataset_management_service.delete_item("suggestions", suggestion_id)
        if not success:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        return {"success": True, "message": "Suggestion deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# CRUD Operations for Feedback Prompts
@router.post("/feedback_prompts", response_model=Dict[str, Any])
async def create_feedback_prompt(
    prompt_data: FeedbackPromptModel
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Create a new feedback prompt"""
    try:
        result = await dataset_management_service.create_item(
            "feedback_prompts",
            prompt_data.dict(exclude={'id', 'created_at', 'updated_at'})
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "data": result}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create feedback prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/feedback_prompts/{prompt_id}")
async def get_feedback_prompt(
    prompt_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get a specific feedback prompt by ID"""
    try:
        result = await dataset_management_service.get_item("feedback_prompts", prompt_id)
        if not result:
            raise HTTPException(status_code=404, detail="Feedback prompt not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get feedback prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/feedback_prompts")
async def get_feedback_prompts(
    next_action_id: Optional[str] = Query(None, description="Filter by next action ID"),
    stage: Optional[str] = Query(None, description="Filter by stage"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    sort_order: int = Query(-1)
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get feedback prompts with filtering and pagination"""
    try:
        filters = {}
        if next_action_id:
            filters["next_action_id"] = next_action_id
        if stage:
            filters["stage"] = stage

        result = await dataset_management_service.get_items(
            "feedback_prompts", filters, skip, limit, sort_by, sort_order
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Failed to get feedback prompts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/feedback_prompts/{prompt_id}")
async def update_feedback_prompt(
    prompt_id: str,
    prompt_data: Dict[str, Any]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Update a feedback prompt"""
    try:
        result = await dataset_management_service.update_item(
            "feedback_prompts", prompt_id, prompt_data
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update feedback prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/feedback_prompts/{prompt_id}")
async def delete_feedback_prompt(
    prompt_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Delete a feedback prompt"""
    try:
        success = await dataset_management_service.delete_item("feedback_prompts", prompt_id)
        if not success:
            raise HTTPException(status_code=404, detail="Feedback prompt not found")
        return {"success": True, "message": "Feedback prompt deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete feedback prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# CRUD Operations for Next Actions
@router.post("/next_actions", response_model=Dict[str, Any])
async def create_next_action(
    action_data: NextActionModel
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Create a new next action"""
    try:
        result = await dataset_management_service.create_item(
            "next_actions",
            action_data.dict(exclude={'id', 'created_at', 'updated_at'})
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "data": result}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create next action: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/next_actions/{action_id}")
async def get_next_action(
    action_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get a specific next action by ID"""
    try:
        result = await dataset_management_service.get_item("next_actions", action_id)
        if not result:
            raise HTTPException(status_code=404, detail="Next action not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get next action: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/next_actions")
async def get_next_actions(
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    sort_order: int = Query(-1)
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get next actions with filtering and pagination"""
    try:
        filters = {}
        if action_type:
            filters["action_type"] = action_type

        result = await dataset_management_service.get_items(
            "next_actions", filters, skip, limit, sort_by, sort_order
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Failed to get next actions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/next_actions/{action_id}")
async def update_next_action(
    action_id: str,
    action_data: Dict[str, Any]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Update a next action"""
    try:
        result = await dataset_management_service.update_item(
            "next_actions", action_id, action_data
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update next action: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/next_actions/{action_id}")
async def delete_next_action(
    action_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Delete a next action"""
    try:
        success = await dataset_management_service.delete_item("next_actions", action_id)
        if not success:
            raise HTTPException(status_code=404, detail="Next action not found")
        return {"success": True, "message": "Next action deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete next action: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# CRUD Operations for Training Examples
@router.post("/training_examples", response_model=Dict[str, Any])
async def create_training_example(
    example_data: FineTuningExampleModel
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Create a new training example"""
    try:
        result = await dataset_management_service.create_item(
            "training_examples",
            example_data.dict(exclude={'id', 'created_at', 'updated_at'})
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "data": result}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create training example: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/training_examples/{example_id}")
async def get_training_example(
    example_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get a specific training example by ID"""
    try:
        result = await dataset_management_service.get_item("training_examples", example_id)
        if not result:
            raise HTTPException(status_code=404, detail="Training example not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get training example: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/training_examples")
async def get_training_examples(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    user_intent: Optional[str] = Query(None, description="Filter by user intent"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    sort_order: int = Query(-1)
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get training examples with filtering and pagination"""
    try:
        filters = {}
        if domain:
            filters["domain"] = domain
        if user_intent:
            filters["user_intent"] = user_intent

        result = await dataset_management_service.get_items(
            "training_examples", filters, skip, limit, sort_by, sort_order
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Failed to get training examples: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/training_examples/{example_id}")
async def update_training_example(
    example_id: str,
    example_data: Dict[str, Any]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Update a training example"""
    try:
        result = await dataset_management_service.update_item(
            "training_examples", example_id, example_data
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update training example: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/training_examples/{example_id}")
async def delete_training_example(
    example_id: str
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Delete a training example"""
    try:
        success = await dataset_management_service.delete_item("training_examples", example_id)
        if not success:
            raise HTTPException(status_code=404, detail="Training example not found")
        return {"success": True, "message": "Training example deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete training example: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Bulk Operations
@router.post("/bulk/create/{data_type}")
async def bulk_create(
    data_type: str,
    items: List[Dict[str, Any]]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Create multiple items in bulk"""
    if data_type not in DATA_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid data type: {data_type}")

    try:
        result = await dataset_management_service.bulk_create(data_type, items)
        return {"success": result.success, "data": result.dict()}
    except Exception as e:
        logger.error(f"Failed to bulk create {data_type}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/bulk/update/{data_type}")
async def bulk_update(
    data_type: str,
    updates: List[Dict[str, Any]]
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Update multiple items in bulk"""
    if data_type not in DATA_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid data type: {data_type}")

    try:
        result = await dataset_management_service.bulk_update(data_type, updates)
        return {"success": result.success, "data": result.dict()}
    except Exception as e:
        logger.error(f"Failed to bulk update {data_type}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Statistics and Overview
@router.get("/stats", response_model=List[DatasetStatsModel])
async def get_dataset_stats(
    # TEMPORARILY DISABLED: Admin authentication dependency
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get dataset statistics for all domains"""
    try:
        stats = await dataset_management_service.get_dataset_stats()
        return {"success": True, "data": [stat.dict() for stat in stats]}
    except Exception as e:
        logger.error(f"Failed to get dataset stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint for dataset management"""
    try:
        # Basic connectivity check
        stats = await dataset_management_service.get_dataset_stats()
        return {
            "status": "healthy",
            "service": "dataset_management",
            "timestamp": datetime.utcnow().isoformat(),
            "domains_available": len(stats)
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "dataset_management",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }