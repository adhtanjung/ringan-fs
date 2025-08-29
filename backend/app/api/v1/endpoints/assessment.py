from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.assessment_service import assessment_service
from app.core.auth import get_current_user

router = APIRouter()

class StartAssessmentRequest(BaseModel):
    user_id: str
    problem_category: Optional[str] = "general"

class SubmitAnswerRequest(BaseModel):
    user_id: str
    answer: str
    question_id: Optional[str] = None

class AssessmentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/start", response_model=AssessmentResponse)
async def start_assessment(request: StartAssessmentRequest):
    """
    Start a new assessment session for a user
    """
    try:
        result = await assessment_service.start_assessment(request.user_id, request.problem_category)
        return AssessmentResponse(
            success=True,
            message="Assessment started successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit", response_model=AssessmentResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """
    Submit an answer for the current assessment question
    """
    try:
        result = await assessment_service.process_assessment_response(
            request.user_id, 
            request.answer,
            request.question_id or ""
        )
        return AssessmentResponse(
            success=True,
            message="Answer submitted successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{user_id}", response_model=AssessmentResponse)
def get_assessment_status(user_id: str):
    """
    Get the current status of an assessment session
    """
    try:
        result = assessment_service.get_session_status(user_id)
        return AssessmentResponse(
            success=True,
            message="Status retrieved successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel", response_model=AssessmentResponse)
def cancel_assessment(request: StartAssessmentRequest):
    """
    Cancel the current assessment session
    """
    try:
        result = assessment_service.cancel_assessment(request.user_id)
        return AssessmentResponse(
            success=True,
            message="Assessment cancelled successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))