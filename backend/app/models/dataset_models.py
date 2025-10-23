"""Enhanced Data Models for Dataset Management System

Implements the unified data structure outlined in PRD with proper relationships
and validation for the mental health dataset management system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator, field_validator
from enum import Enum


class ResponseType(str, Enum):
    """Valid response types for assessment questions"""
    SCALE = "scale"
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    BOOLEAN = "boolean"


class Stage(str, Enum):
    """Valid stages for feedback prompts"""
    POST_SUGGESTION = "post_suggestion"
    ONGOING = "ongoing"
    FOLLOWUP = "followup"


class NextActionType(str, Enum):
    """Valid next action types"""
    CONTINUE_SAME = "continue_same"
    SHOW_PROBLEM_MENU = "show_problem_menu"
    END_SESSION = "end_session"
    ESCALATE = "escalate"
    SCHEDULE_FOLLOWUP = "schedule_followup"


class UserIntent(str, Enum):
    """User intent categories for fine-tuning examples"""
    PROBLEM_IDENTIFICATION = "problem_identification"
    ASSESSMENT_RESPONSE = "assessment_response"
    SEEKING_HELP = "seeking_help"
    EMOTIONAL_EXPRESSION = "emotional_expression"
    PROGRESS_UPDATE = "progress_update"
    CLARIFICATION = "clarification"
    RESISTANCE = "resistance"
    GRATITUDE = "gratitude"


class BaseDataModel(BaseModel):
    """Base model with common fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    class Config:
        use_enum_values = True
        validate_assignment = True


class ProblemCategoryModel(BaseDataModel):
    """Unified Problems model combining all domains"""
    id: Optional[str] = Field(None, description="Auto-generated ID")
    category: str = Field(..., description="References problem_types.type_name")
    sub_category_id: str = Field(..., description="Unique subcategory identifier")
    problem_name: str = Field(..., description="Specific problem name")
    description: str = Field(..., description="Detailed problem description")
    severity_level: Optional[int] = Field(None, ge=1, le=5, description="Severity level 1-5")

    @field_validator('sub_category_id')
    @classmethod
    def validate_sub_category_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("sub_category_id cannot be empty")
        return v.strip()


class AssessmentQuestionModel(BaseDataModel):
    """Enhanced Self Assessment model with proper relationships"""
    id: Optional[str] = Field(None, description="Auto-generated ID")
    question_id: str = Field(..., description="Unique question identifier")
    sub_category_id: str = Field(..., description="Links to ProblemCategory.sub_category_id")
    batch_id: Optional[str] = Field(None, description="Question batch identifier")
    question_text: str = Field(..., description="The assessment question")
    response_type: ResponseType = Field(..., description="Type of expected response")
    scale_min: Optional[int] = Field(None, description="Minimum scale value")
    scale_max: Optional[int] = Field(None, description="Maximum scale value")
    scale_labels: Optional[Dict[str, str]] = Field(
        default={"1": "Not at all", "2": "A little", "3": "Quite a bit", "4": "Very much"},
        description="Labels for scale values"
    )
    options: Optional[List[str]] = Field(None, description="Multiple choice options")
    next_step: Optional[str] = Field(None, description="Next step logic")
    clusters: Optional[str] = Field(None, description="Associated clusters")

    @model_validator(mode='after')
    def validate_response_type_fields(self):
        if self.response_type == ResponseType.SCALE:
            if self.scale_min is None or self.scale_max is None:
                raise ValueError("Scale questions must have min and max values")
            if self.scale_min != 1 or self.scale_max != 4:
                raise ValueError("Scale questions must use 1-4 range")
            if self.scale_labels is None:
                raise ValueError("Scale questions must have scale_labels")
            # Validate scale_labels has required keys
            required_keys = {"1", "2", "3", "4"}
            if not all(key in self.scale_labels for key in required_keys):
                raise ValueError("scale_labels must contain keys '1', '2', '3', '4'")
        elif self.response_type == ResponseType.MULTIPLE_CHOICE:
            if not self.options:
                raise ValueError("Multiple choice questions must have options")
        return self


class TherapeuticSuggestionModel(BaseDataModel):
    """Enhanced Suggestions model with better categorization"""
    id: Optional[str] = Field(None, description="Auto-generated ID")
    suggestion_id: str = Field(..., description="Unique suggestion identifier")
    sub_category_id: str = Field(..., description="Links to ProblemCategory.sub_category_id")
    cluster: Optional[str] = Field(None, description="Problem cluster")
    suggestion_text: str = Field(..., description="Therapeutic suggestion content")
    resource_link: Optional[str] = Field(None, description="Additional resource URL")
    evidence_base: Optional[str] = Field(None, description="Evidence-based approach (CBT, ACT, etc.)")
    difficulty_level: Optional[int] = Field(None, ge=1, le=3, description="Implementation difficulty 1-3")
    estimated_duration: Optional[str] = Field(None, description="Estimated time to complete")
    tags: Optional[List[str]] = Field(None, description="Categorization tags")


class FeedbackPromptModel(BaseDataModel):
    """Enhanced Feedback Prompts with standardized next_action"""
    id: Optional[str] = Field(None, description="Auto-generated ID")
    prompt_id: str = Field(..., description="Unique prompt identifier")
    stage: Stage = Field(..., description="Feedback stage")
    prompt_text: str = Field(..., description="Feedback prompt content")
    next_action_id: str = Field(..., description="Links to NextActionModel.action_id")
    context: Optional[str] = Field(None, description="Additional context for prompt")

    # Deprecated field for backward compatibility
    next_action: Optional[str] = Field(None, description="Deprecated: use next_action_id")


class NextActionModel(BaseDataModel):
    """Standardized Next Actions with clear machine-readable logic"""
    id: Optional[str] = Field(None, description="Auto-generated ID")
    action_id: str = Field(..., description="Unique action identifier")
    action_type: NextActionType = Field(..., description="Type of next action")
    action_name: str = Field(..., description="Human-readable action name")
    description: str = Field(..., description="Detailed action description")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions for triggering")


class FineTuningExampleModel(BaseDataModel):
    """Enhanced Fine-tuning Examples with user_intent categorization"""
    id: Optional[str] = Field(None, description="Auto-generated ID")
    example_id: str = Field(..., description="Unique example identifier")
    problem: Optional[str] = Field(None, description="Associated problem")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    user_intent: UserIntent = Field(..., description="Categorized user intent")
    prompt: str = Field(..., description="User input/prompt")
    completion: str = Field(..., description="Expected AI response")
    context: Optional[str] = Field(None, description="Conversation context")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality rating 0-1")
    tags: Optional[List[str]] = Field(None, description="Additional categorization tags")


class DatasetStatsModel(BaseModel):
    """Statistics for dataset overview"""
    problems_count: int
    assessment_questions_count: int
    suggestions_count: int
    feedback_prompts_count: int
    next_actions_count: int
    training_examples_count: int
    last_updated: datetime


class BulkOperationResult(BaseModel):
    """Result of bulk operations"""
    success: bool
    total_processed: int
    successful: int
    failed: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_ids: List[str] = Field(default_factory=list)
    updated_ids: List[str] = Field(default_factory=list)


class ProblemTypeModel(BaseDataModel):
    """Master table for problem type categories"""
    id: Optional[str] = Field(None, description="Auto-generated ID")
    type_name: str = Field(..., description="Problem type name (e.g., Anxiety, Depression, Stress)")
    category_id: str = Field(..., description="Unique category identifier")
    description: Optional[str] = Field(None, description="Description of this problem type")


class ValidationResult(BaseModel):
    """Data validation result"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    field_errors: Dict[str, List[str]] = Field(default_factory=dict)
    foreign_key_errors: List[str] = Field(default_factory=list)