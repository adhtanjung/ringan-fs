"""Dataset Validation Service

Implements comprehensive data validation including schema validation,
foreign key relationships, and data integrity checks for the mental health
dataset management system.
"""

import logging
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
import re

from app.models.dataset_models import (
    ProblemCategoryModel, AssessmentQuestionModel, TherapeuticSuggestionModel,
    FeedbackPromptModel, NextActionModel, FineTuningExampleModel,
    ProblemTypeModel, DomainTypeModel,
    ValidationResult, ResponseType, Stage, NextActionType, UserIntent
)
from app.core.database import get_mongodb

logger = logging.getLogger(__name__)


class DatasetValidationService:
    """Service for validating dataset integrity and relationships"""

    def __init__(self):
        self.db = None
        self._validation_rules = self._initialize_validation_rules()

    async def initialize(self):
        """Initialize the validation service"""
        try:
            self.db = get_mongodb()
            if self.db is not None:
                self.db = self.db.mental_health_db
            logger.info("✅ Dataset validation service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize validation service: {str(e)}")
            raise

    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for different data types"""
        return {
            'id_patterns': {
                'category_id': r'^[A-Z]{2,4}_\d{2,3}$',  # e.g., STR_01, ANX_001
                'sub_category_id': r'^[A-Z]{2,4}_\d{2,3}_\d{2}$',  # e.g., STR_01_01
                'question_id': r'^Q\d{3,4}$',  # e.g., Q001, Q0001
                'suggestion_id': r'^S_[A-Z]{2,4}_\d{3,4}$',  # e.g., S_STR_001
                'prompt_id': r'^P_[A-Z]{2,4}_\d{3,4}$',  # e.g., P_STR_001
                'action_id': r'^A_\d{3,4}$',  # e.g., A_001
                'example_id': r'^E_[A-Z]{2,4}_\d{3,4}$'  # e.g., E_STR_001
            },
            'required_fields': {
                'problems': ['domain', 'category', 'category_id', 'sub_category_id', 'problem_name', 'description'],
                'assessments': ['question_id', 'sub_category_id', 'question_text', 'response_type'],
                'suggestions': ['suggestion_id', 'sub_category_id', 'suggestion_text'],
                'feedback_prompts': ['prompt_id', 'stage', 'prompt_text', 'next_action_id'],
                'next_actions': ['action_id', 'action_type', 'action_name', 'description'],
                'training_examples': ['example_id', 'domain', 'user_intent', 'prompt', 'completion']
            },
            'valid_domains': ['stress', 'anxiety', 'trauma', 'general'],
            'text_length_limits': {
                'problem_name': 200,
                'description': 2000,
                'question_text': 500,
                'suggestion_text': 2000,
                'prompt_text': 500,
                'prompt': 1000,
                'completion': 2000
            }
        }

    async def validate_problem_category(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a problem category entry"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)

        try:
            # Basic model validation
            model = ProblemCategoryModel(**data)

            # ID pattern validation disabled for Problem Categories
            # Users can use any format for category_id and sub_category_id

            # Domain validation
            if model.domain not in self._validation_rules['valid_domains']:
                field_errors['domain'].append(f"Invalid domain: {model.domain}")

            # Text length validation
            if len(model.problem_name) > self._validation_rules['text_length_limits']['problem_name']:
                field_errors['problem_name'].append("Problem name too long")

            if len(model.description) > self._validation_rules['text_length_limits']['description']:
                field_errors['description'].append("Description too long")

            # Check for duplicate IDs if database is available
            if self.db is not None:
                existing = await self.db.problems.find_one({
                    "$or": [
                        {"category_id": model.category_id},
                        {"sub_category_id": model.sub_category_id}
                    ]
                })
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate category or sub-category ID found")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors)
        )

    async def validate_assessment_question(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate an assessment question entry"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)
        foreign_key_errors = []

        try:
            # Basic model validation
            model = AssessmentQuestionModel(**data)

            # ID pattern validation
            if not re.match(self._validation_rules['id_patterns']['question_id'], model.question_id):
                field_errors['question_id'].append(f"Invalid question_id format: {model.question_id}")

            # Text length validation
            if len(model.question_text) > self._validation_rules['text_length_limits']['question_text']:
                field_errors['question_text'].append("Question text too long")

            # Response type specific validation
            if model.response_type == ResponseType.SCALE:
                if model.scale_min is None or model.scale_max is None:
                    field_errors['response_type'].append("Scale questions must have min and max values")
                elif model.scale_min >= model.scale_max:
                    field_errors['scale_min'].append("Scale min must be less than max")

            elif model.response_type == ResponseType.MULTIPLE_CHOICE:
                if not model.options or len(model.options) < 2:
                    field_errors['options'].append("Multiple choice questions must have at least 2 options")

            # Foreign key validation
            if self.db is not None:
                # Check if sub_category_id exists in problems collection
                problem_exists = await self.db.problems.find_one({"sub_category_id": model.sub_category_id})
                if not problem_exists:
                    foreign_key_errors.append(f"sub_category_id '{model.sub_category_id}' not found in problems")

                # Check for duplicate question_id
                existing = await self.db.assessments.find_one({"question_id": model.question_id})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate question_id: {model.question_id}")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0 and len(foreign_key_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors),
            foreign_key_errors=foreign_key_errors
        )

    async def validate_therapeutic_suggestion(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a therapeutic suggestion entry"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)
        foreign_key_errors = []

        try:
            # Basic model validation
            model = TherapeuticSuggestionModel(**data)

            # ID pattern validation
            if not re.match(self._validation_rules['id_patterns']['suggestion_id'], model.suggestion_id):
                field_errors['suggestion_id'].append(f"Invalid suggestion_id format: {model.suggestion_id}")

            # Text length validation
            if len(model.suggestion_text) > self._validation_rules['text_length_limits']['suggestion_text']:
                field_errors['suggestion_text'].append("Suggestion text too long")

            # URL validation for resource_link
            if model.resource_link:
                url_pattern = r'^https?://[\w\.-]+\.[a-zA-Z]{2,}'
                if not re.match(url_pattern, model.resource_link):
                    field_errors['resource_link'].append("Invalid URL format")

            # Foreign key validation
            if self.db is not None:
                # Check if sub_category_id exists in problems collection
                problem_exists = await self.db.problems.find_one({"sub_category_id": model.sub_category_id})
                if not problem_exists:
                    foreign_key_errors.append(f"sub_category_id '{model.sub_category_id}' not found in problems")

                # Check for duplicate suggestion_id
                existing = await self.db.suggestions.find_one({"suggestion_id": model.suggestion_id})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate suggestion_id: {model.suggestion_id}")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0 and len(foreign_key_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors),
            foreign_key_errors=foreign_key_errors
        )

    async def validate_feedback_prompt(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a feedback prompt entry"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)
        foreign_key_errors = []

        try:
            # Basic model validation
            model = FeedbackPromptModel(**data)

            # ID pattern validation
            if not re.match(self._validation_rules['id_patterns']['prompt_id'], model.prompt_id):
                field_errors['prompt_id'].append(f"Invalid prompt_id format: {model.prompt_id}")

            # Text length validation
            if len(model.prompt_text) > self._validation_rules['text_length_limits']['prompt_text']:
                field_errors['prompt_text'].append("Prompt text too long")

            # Foreign key validation
            if self.db is not None:
                # Check if next_action_id exists in next_actions collection
                action_exists = await self.db.next_actions.find_one({"action_id": model.next_action_id})
                if not action_exists:
                    foreign_key_errors.append(f"next_action_id '{model.next_action_id}' not found in next_actions")

                # Check for duplicate prompt_id
                existing = await self.db.feedback_prompts.find_one({"prompt_id": model.prompt_id})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate prompt_id: {model.prompt_id}")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0 and len(foreign_key_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors),
            foreign_key_errors=foreign_key_errors
        )

    async def validate_next_action(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a next action entry"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)

        try:
            # Basic model validation
            model = NextActionModel(**data)

            # ID pattern validation
            if not re.match(self._validation_rules['id_patterns']['action_id'], model.action_id):
                field_errors['action_id'].append(f"Invalid action_id format: {model.action_id}")

            # Check for duplicate action_id
            if self.db is not None:
                existing = await self.db.next_actions.find_one({"action_id": model.action_id})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate action_id: {model.action_id}")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors)
        )

    async def validate_training_example(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a fine-tuning training example"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)

        try:
            # Basic model validation
            model = FineTuningExampleModel(**data)

            # ID pattern validation
            if not re.match(self._validation_rules['id_patterns']['example_id'], model.example_id):
                field_errors['example_id'].append(f"Invalid example_id format: {model.example_id}")

            # Domain validation
            if model.domain not in self._validation_rules['valid_domains']:
                field_errors['domain'].append(f"Invalid domain: {model.domain}")

            # Text length validation
            if len(model.prompt) > self._validation_rules['text_length_limits']['prompt']:
                field_errors['prompt'].append("Prompt too long")

            if len(model.completion) > self._validation_rules['text_length_limits']['completion']:
                field_errors['completion'].append("Completion too long")

            # Quality score validation
            if model.quality_score is not None and (model.quality_score < 0 or model.quality_score > 1):
                field_errors['quality_score'].append("Quality score must be between 0 and 1")

            # Check for duplicate example_id
            if self.db is not None:
                existing = await self.db.training_examples.find_one({"example_id": model.example_id})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate example_id: {model.example_id}")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors)
        )

    async def validate_problem_type(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a problem type master table entry"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)

        try:
            # Basic model validation
            model = ProblemTypeModel(**data)

            # Type name validation
            if not model.type_name or len(model.type_name.strip()) == 0:
                field_errors['type_name'].append("Type name is required")
            elif len(model.type_name) > 100:
                field_errors['type_name'].append("Type name too long (max 100 characters)")

            # Description validation
            if model.description and len(model.description) > 500:
                field_errors['description'].append("Description too long (max 500 characters)")

            # Check for duplicate type_name
            if self.db is not None:
                existing = await self.db.problem_types.find_one({"type_name": model.type_name})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate type_name: {model.type_name}")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors)
        )

    async def validate_domain_type(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a domain type master table entry"""
        errors = []
        warnings = []
        field_errors = defaultdict(list)

        try:
            # Basic model validation
            model = DomainTypeModel(**data)

            # Domain name validation
            if not model.domain_name or len(model.domain_name.strip()) == 0:
                field_errors['domain_name'].append("Domain name is required")
            elif len(model.domain_name) > 100:
                field_errors['domain_name'].append("Domain name too long (max 100 characters)")

            # Domain code validation
            if not model.domain_code or len(model.domain_code.strip()) == 0:
                field_errors['domain_code'].append("Domain code is required")
            elif len(model.domain_code) > 10:
                field_errors['domain_code'].append("Domain code too long (max 10 characters)")
            elif not re.match(r'^[A-Z0-9_]+$', model.domain_code):
                field_errors['domain_code'].append("Domain code must contain only uppercase letters, numbers, and underscores")

            # Description validation
            if model.description and len(model.description) > 500:
                field_errors['description'].append("Description too long (max 500 characters)")

            # Check for duplicate domain_name
            if self.db is not None:
                existing = await self.db.domain_types.find_one({"domain_name": model.domain_name})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate domain_name: {model.domain_name}")

            # Check for duplicate domain_code
            if self.db is not None:
                existing = await self.db.domain_types.find_one({"domain_code": model.domain_code})
                if existing and existing.get('id') != data.get('id'):
                    errors.append(f"Duplicate domain_code: {model.domain_code}")

        except Exception as e:
            errors.append(f"Model validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0 and len(field_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=dict(field_errors)
        )

    async def validate_bulk_data(self, data_type: str, data_list: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate a list of data entries"""
        validation_methods = {
            'problems': self.validate_problem_category,
            'assessments': self.validate_assessment_question,
            'suggestions': self.validate_therapeutic_suggestion,
            'feedback_prompts': self.validate_feedback_prompt,
            'next_actions': self.validate_next_action,
            'training_examples': self.validate_training_example
        }

        if data_type not in validation_methods:
            raise ValueError(f"Unknown data type: {data_type}")

        validation_method = validation_methods[data_type]
        results = []

        for item in data_list:
            try:
                result = await validation_method(item)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    is_valid=False,
                    errors=[f"Validation error: {str(e)}"]
                ))

        return results

    async def check_referential_integrity(self) -> ValidationResult:
        """Check referential integrity across all collections"""
        if self.db is None:
            return ValidationResult(
                is_valid=False,
                errors=["Database not available for integrity check"]
            )

        errors = []
        warnings = []

        try:
            # Check assessment questions reference valid sub_category_ids
            assessments = await self.db.assessments.find({}).to_list(None)
            problem_sub_categories = set()
            async for problem in self.db.problems.find({}, {"sub_category_id": 1}):
                problem_sub_categories.add(problem["sub_category_id"])

            for assessment in assessments:
                if assessment.get("sub_category_id") not in problem_sub_categories:
                    errors.append(f"Assessment {assessment.get('question_id')} references invalid sub_category_id: {assessment.get('sub_category_id')}")

            # Check suggestions reference valid sub_category_ids
            suggestions = await self.db.suggestions.find({}).to_list(None)
            for suggestion in suggestions:
                if suggestion.get("sub_category_id") not in problem_sub_categories:
                    errors.append(f"Suggestion {suggestion.get('suggestion_id')} references invalid sub_category_id: {suggestion.get('sub_category_id')}")

            # Check feedback prompts reference valid action_ids
            feedback_prompts = await self.db.feedback_prompts.find({}).to_list(None)
            action_ids = set()
            async for action in self.db.next_actions.find({}, {"action_id": 1}):
                action_ids.add(action["action_id"])

            for prompt in feedback_prompts:
                if prompt.get("next_action_id") not in action_ids:
                    errors.append(f"Feedback prompt {prompt.get('prompt_id')} references invalid next_action_id: {prompt.get('next_action_id')}")

        except Exception as e:
            errors.append(f"Integrity check failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    async def validate_bulk_data(self, data_type: str, items: List[Dict[str, Any]]) -> ValidationResult:
        """Validate multiple items in bulk"""
        all_errors = []
        field_errors = defaultdict(list)

        for i, item in enumerate(items):
            try:
                if data_type == 'problems':
                    result = await self.validate_problem_category(item)
                elif data_type == 'assessments':
                    result = await self.validate_assessment_question(item)
                elif data_type == 'suggestions':
                    result = await self.validate_therapeutic_suggestion(item)
                elif data_type == 'feedback_prompts':
                    result = await self.validate_feedback_prompt(item)
                elif data_type == 'next_actions':
                    result = await self.validate_next_action(item)
                elif data_type == 'training_examples':
                    result = await self.validate_fine_tuning_example(item)
                else:
                    result = ValidationResult(
                        is_valid=False,
                        errors=[f"Unknown data type: {data_type}"]
                    )

                if not result.is_valid:
                    for error in result.errors:
                        all_errors.append(f"Item {i}: {error}")
                    for field, errors in result.field_errors.items():
                        field_errors[field].extend([f"Item {i}: {error}" for error in errors])
            except Exception as e:
                all_errors.append(f"Item {i}: {str(e)}")

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            field_errors=dict(field_errors)
        )


# Global instance
dataset_validation_service = DatasetValidationService()