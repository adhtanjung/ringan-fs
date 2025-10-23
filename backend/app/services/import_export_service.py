"""
Import/Export Service for Dataset Management
Handles file import/export operations with template generation
"""

import logging
import pandas as pd
import io
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import asyncio

from app.models.dataset_models import (
    ProblemCategoryModel, AssessmentQuestionModel, TherapeuticSuggestionModel,
    FeedbackPromptModel, NextActionModel, FineTuningExampleModel,
    ProblemTypeModel,
    ResponseType, Stage, NextActionType, UserIntent
)
from app.services.dataset_management_service import dataset_management_service
from app.services.dataset_validation_service import dataset_validation_service

logger = logging.getLogger(__name__)


class ImportExportService:
    """Service for importing/exporting datasets with template generation"""

    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'json']
        self.data_types = {
            'problems': ProblemCategoryModel,
            'assessments': AssessmentQuestionModel,
            'suggestions': TherapeuticSuggestionModel,
            'feedback_prompts': FeedbackPromptModel,
            'next_actions': NextActionModel,
            'training_examples': FineTuningExampleModel,
            'problem_types': ProblemTypeModel,
        }

    async def initialize(self):
        """Initialize the service"""
        try:
            await dataset_management_service.initialize()
            await dataset_validation_service.initialize()
            logger.info("✅ Import/Export service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize import/export service: {str(e)}")
            raise

    def generate_template(self, data_type: str, format: str = 'csv') -> bytes:
        """Generate import template for a specific data type"""
        if data_type not in self.data_types:
            raise ValueError(f"Unsupported data type: {data_type}")

        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}")

        # Get model fields and create template data
        model_class = self.data_types[data_type]
        template_data = self._create_template_data(data_type)

        if format == 'csv':
            return self._generate_csv_template(template_data, data_type)
        elif format == 'xlsx':
            return self._generate_excel_template(template_data, data_type)
        elif format == 'json':
            return self._generate_json_template(template_data, data_type)

    def _create_template_data(self, data_type: str) -> List[Dict[str, Any]]:
        """Create sample data for templates"""
        templates = {
            'problems': [
                {
                    'category': 'Social Anxiety',
                    'sub_category_id': 'SOC_ANX_001_001',
                    'problem_name': 'Fear of Public Speaking',
                    'description': 'Intense fear and anxiety when speaking in front of groups or audiences',
                    'severity_level': 3,
                    'is_active': True
                },
                {
                    'category': 'Work Stress',
                    'sub_category_id': 'WORK_STR_001_001',
                    'problem_name': 'Deadline Pressure',
                    'description': 'Overwhelming stress from tight deadlines and high workload expectations',
                    'severity_level': 4,
                    'is_active': True
                }
            ],
            'assessments': [
                {
                    'question_id': 'Q001',
                    'sub_category_id': 'SOC_ANX_001_001',
                    'batch_id': 'BATCH_001',
                    'question_text': 'How often do you avoid social situations due to anxiety?',
                    'response_type': 'scale',
                    'scale_min': 1,
                    'scale_max': 4,
                    'scale_labels': '{"1": "Not at all", "2": "A little", "3": "Quite a bit", "4": "Very much"}',
                    'options': None,
                    'next_step': 'end_assess',
                    'clusters': 'c1',
                    'is_active': True
                },
                {
                    'question_id': 'Q002',
                    'sub_category_id': 'SOC_ANX_001_001',
                    'batch_id': 'BATCH_001',
                    'question_text': 'Which situations make you most anxious?',
                    'response_type': 'multiple_choice',
                    'scale_min': None,
                    'scale_max': None,
                    'options': '["Public speaking", "Meeting new people", "Group conversations", "Being the center of attention"]',
                    'next_step': 'end_assess',
                    'clusters': 'c1',
                    'is_active': True
                }
            ],
            'suggestions': [
                {
                    'suggestion_id': 'SUGG_001',
                    'sub_category_id': 'SOC_ANX_001_001',
                    'cluster': 'breathing_techniques',
                    'suggestion_text': 'Practice deep breathing exercises before social situations. Inhale for 4 counts, hold for 4, exhale for 6.',
                    'resource_link': 'https://example.com/breathing-exercises',
                    'evidence_base': 'CBT, Mindfulness-based interventions',
                    'difficulty_level': 1,
                    'estimated_duration': '5-10 minutes',
                    'tags': '["breathing", "anxiety", "immediate_relief"]',
                    'is_active': True
                }
            ],
            'feedback_prompts': [
                {
                    'prompt_id': 'PROMPT_001',
                    'stage': 'post_suggestion',
                    'prompt_text': 'How did the breathing exercise make you feel? Rate your anxiety level before and after.',
                    'next_action_id': 'ACTION_001',
                    'context': 'Follow-up after breathing exercise suggestion',
                    'is_active': True
                }
            ],
            'next_actions': [
                {
                    'action_id': 'ACTION_001',
                    'action_type': 'continue_same',
                    'action_name': 'Continue with current approach',
                    'description': 'Continue with the current therapeutic approach and monitor progress',
                    'parameters': '{"duration": "1 week", "check_interval": "daily"}',
                    'conditions': '{"anxiety_level": "< 3", "engagement": "high"}',
                    'is_active': True
                }
            ],
            'training_examples': [
                {
                    'example_id': 'TRAIN_001',
                    'problem': 'Social anxiety in group settings',
                    'conversation_id': 'CONV_001',
                    'user_intent': 'seeking_help',
                    'prompt': 'I get really nervous when I have to speak in meetings at work. My heart races and I can\'t think clearly.',
                    'completion': 'I understand that speaking in meetings can feel overwhelming. Let\'s work on some strategies to help you feel more comfortable. Would you like to try some breathing exercises that can help calm your nervous system?',
                    'context': 'User expressing social anxiety in workplace setting',
                    'quality_score': 0.9,
                    'tags': '["social_anxiety", "workplace", "breathing_techniques"]',
                    'is_active': True
                }
            ],
            'problem_types': [
                {
                    'type_name': 'Social Anxiety',
                    'category_id': 'SOC_ANX_001',
                    'description': 'Anxiety related to social situations',
                    'is_active': True
                },
                {
                    'type_name': 'Work Stress',
                    'category_id': 'WORK_STR_001',
                    'description': 'Stress-related conditions and work-life balance issues',
                    'is_active': True
                }
            ],
        }

        return templates.get(data_type, [])

    def _generate_csv_template(self, template_data: List[Dict], data_type: str) -> bytes:
        """Generate CSV template"""
        if not template_data:
            return b""

        df = pd.DataFrame(template_data)

        # Add instructions as comments
        instructions = self._get_field_instructions(data_type)

        output = io.StringIO()

        # Write instructions as comments
        for instruction in instructions:
            output.write(f"# {instruction}\n")
        output.write("\n")

        # Write the data
        df.to_csv(output, index=False)

        return output.getvalue().encode('utf-8')

    def _generate_excel_template(self, template_data: List[Dict], data_type: str) -> bytes:
        """Generate Excel template with instructions sheet"""
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Create instructions sheet
            instructions = self._get_field_instructions(data_type)
            instructions_df = pd.DataFrame({
                'Field': [inst.split(':')[0] if ':' in inst else inst for inst in instructions],
                'Description': [inst.split(':', 1)[1].strip() if ':' in inst else '' for inst in instructions]
            })
            instructions_df.to_excel(writer, sheet_name='Instructions', index=False)

            # Create data sheet
            if template_data:
                df = pd.DataFrame(template_data)
                df.to_excel(writer, sheet_name='Data', index=False)
            else:
                # Create empty sheet with headers
                model_class = self.data_types[data_type]
                headers = list(model_class.model_fields.keys())
                empty_df = pd.DataFrame(columns=headers)
                empty_df.to_excel(writer, sheet_name='Data', index=False)

        return output.getvalue()

    def _generate_json_template(self, template_data: List[Dict], data_type: str) -> bytes:
        """Generate JSON template"""
        template = {
            "instructions": self._get_field_instructions(data_type),
            "sample_data": template_data,
            "schema": self._get_json_schema(data_type)
        }

        return json.dumps(template, indent=2).encode('utf-8')

    def _get_field_instructions(self, data_type: str) -> List[str]:
        """Get field instructions for templates"""
        instructions = {
            'problems': [
                'category: Main problem category name (must exist in problem_types)',
                'sub_category_id: Unique subcategory identifier (e.g., SOC_ANX_001_001)',
                'problem_name: Specific problem name',
                'description: Detailed description of the problem',
                'severity_level: Numeric severity level (1-5)',
                'is_active: Whether this problem is active (true/false)'
            ],
            'assessments': [
                'question_id: Unique question identifier (e.g., ASSESS_001)',
                'sub_category_id: Links to problem subcategory',
                'batch_id: Question batch identifier',
                'question_text: The assessment question text',
                'response_type: Type of response (scale, multiple_choice, text, boolean)',
                'scale_min: Minimum value for scale questions (must be 1)',
                'scale_max: Maximum value for scale questions (must be 4)',
                'scale_label_1: Label for scale value 1 (default: "Not at all")',
                'scale_label_2: Label for scale value 2 (default: "A little")',
                'scale_label_3: Label for scale value 3 (default: "Quite a bit")',
                'scale_label_4: Label for scale value 4 (default: "Very much")',
                'options: JSON array of options for multiple choice questions',
                'next_step: Logic for next question based on response',
                'clusters: Comma-separated cluster names',
                'is_active: Whether this question is active (true/false)'
            ],
            'suggestions': [
                'suggestion_id: Unique suggestion identifier (e.g., SUGG_001)',
                'sub_category_id: Links to problem subcategory',
                'cluster: Problem cluster name',
                'suggestion_text: The therapeutic suggestion content',
                'resource_link: URL to additional resources',
                'evidence_base: Evidence-based approach (CBT, ACT, etc.)',
                'difficulty_level: Implementation difficulty (1-3)',
                'estimated_duration: Estimated time to complete',
                'tags: JSON array of categorization tags',
                'is_active: Whether this suggestion is active (true/false)'
            ],
            'feedback_prompts': [
                'prompt_id: Unique prompt identifier (e.g., PROMPT_001)',
                'stage: Feedback stage (post_suggestion, ongoing, followup)',
                'prompt_text: The feedback prompt content',
                'next_action_id: Links to next action',
                'context: Additional context for the prompt',
                'is_active: Whether this prompt is active (true/false)'
            ],
            'next_actions': [
                'action_id: Unique action identifier (e.g., ACTION_001)',
                'action_type: Type of action (continue_same, show_problem_menu, end_session, escalate, schedule_followup)',
                'action_name: Human-readable action name',
                'description: Detailed action description',
                'parameters: JSON object with action parameters',
                'conditions: JSON object with trigger conditions',
                'is_active: Whether this action is active (true/false)'
            ],
            'training_examples': [
                'example_id: Unique example identifier (e.g., TRAIN_001)',
                'problem: Associated problem description',
                'conversation_id: Conversation identifier',
                'user_intent: User intent category (seeking_help, emotional_expression, etc.)',
                'prompt: User input/prompt',
                'completion: Expected AI response',
                'context: Conversation context',
                'quality_score: Quality rating (0.0-1.0)',
                'tags: JSON array of categorization tags',
                'is_active: Whether this example is active (true/false)'
            ],
            'problem_types': [
                'type_name: Problem type name (must be unique)',
                'category_id: Unique category identifier (e.g., SOC_ANX_001)',
                'description: Description of this problem type',
                'is_active: Whether this type is active (true/false)'
            ],
        }

        return instructions.get(data_type, [])

    def _get_json_schema(self, data_type: str) -> Dict[str, Any]:
        """Get JSON schema for data type"""
        model_class = self.data_types[data_type]
        return model_class.model_json_schema()

    def _clean_import_data(self, records: List[Dict[str, Any]], data_type: str) -> List[Dict[str, Any]]:
        """Clean imported data to handle NaN values and type conversions"""
        import pandas as pd
        import json

        cleaned_records = []

        for record in records:
            cleaned_record = {}

            for key, value in record.items():
                # Handle NaN values
                if pd.isna(value) or value is None:
                    cleaned_record[key] = None
                # Handle string representations of lists (only for options field)
                elif key == 'options' and isinstance(value, str):
                    try:
                        # Try to parse as JSON list
                        if value.startswith('[') and value.endswith(']'):
                            cleaned_record[key] = json.loads(value)
                        else:
                            # Split by comma if it's a simple comma-separated string
                            cleaned_record[key] = [item.strip() for item in value.split(',') if item.strip()]
                    except (json.JSONDecodeError, ValueError):
                        cleaned_record[key] = None
                # Handle clusters as string field (not list)
                elif key == 'clusters' and isinstance(value, str):
                    # Keep clusters as string, don't convert to list
                    cleaned_record[key] = value.strip() if value.strip() else None
                # Handle numeric fields that might be NaN
                elif key in ['scale_min', 'scale_max'] and pd.isna(value):
                    cleaned_record[key] = None
                # Handle scale_labels field
                elif key == 'scale_labels' and isinstance(value, str):
                    try:
                        # Try to parse as JSON
                        cleaned_record[key] = json.loads(value)
                    except (json.JSONDecodeError, ValueError):
                        # If not valid JSON, use default
                        cleaned_record[key] = {"1": "Not at all", "2": "A little", "3": "Quite a bit", "4": "Very much"}
                elif key == 'scale_labels' and pd.isna(value):
                    cleaned_record[key] = {"1": "Not at all", "2": "A little", "3": "Quite a bit", "4": "Very much"}
                # Handle boolean fields
                elif key == 'is_active':
                    if pd.isna(value):
                        cleaned_record[key] = True  # Default to active
                    else:
                        cleaned_record[key] = bool(value)
                else:
                    cleaned_record[key] = value

            cleaned_records.append(cleaned_record)

        return cleaned_records

    async def import_data(self, file_content: bytes, filename: str, data_type: str,
                         overwrite: bool = False, validate: bool = True) -> Dict[str, Any]:
        """Import data from file"""
        try:
            # Determine file format
            file_ext = Path(filename).suffix.lower()

            if file_ext == '.csv':
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(io.BytesIO(file_content))
            elif file_ext == '.json':
                data = json.loads(file_content.decode('utf-8'))
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif 'sample_data' in data:
                    df = pd.DataFrame(data['sample_data'])
                else:
                    raise ValueError("Invalid JSON format")
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')

            # Clean the data to handle NaN values and type conversions
            records = self._clean_import_data(records, data_type)

            # Clean and validate data (validation disabled by default)
            if validate:
                validation_result = await dataset_validation_service.validate_bulk_data(
                    data_type, records
                )
                if not validation_result.is_valid:
                    return {
                        'success': False,
                        'message': 'Validation failed',
                        'errors': validation_result.errors,
                        'field_errors': validation_result.field_errors
                    }

            # Import data
            result = await dataset_management_service.bulk_create(data_type, records, overwrite)

            # Format errors for better frontend display
            formatted_errors = []
            for error in result.errors:
                if "Model validation failed" in error:
                    # Extract the specific validation error details
                    import re
                    # Look for field-specific errors
                    field_errors = re.findall(r'(\w+)\n\s+Input should be a valid (\w+)', error)
                    for field, expected_type in field_errors:
                        formatted_errors.append(f"Field '{field}' should be {expected_type}")
                else:
                    formatted_errors.append(error)

            return {
                'success': result.success,
                'imported_count': result.successful,
                'failed_count': result.failed,
                'errors': formatted_errors,
                'warnings': result.warnings,
                'raw_errors': result.errors  # Keep original errors for debugging
            }

        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'imported_count': 0,
                'failed_count': 0,
                'errors': [str(e)]
            }

    async def export_data(self, data_type: str, format: str = 'csv',
                         filters: Optional[Dict[str, Any]] = None) -> bytes:
        """Export data to file"""
        try:
            logger.info(f"Starting export for {data_type} in {format} format with filters: {filters}")

            # Get data from database
            data = await dataset_management_service.get_all_data(data_type, filters)
            logger.info(f"Retrieved {len(data)} items from database")

            if not data:
                logger.warning(f"No data found for {data_type} with filters: {filters}")
                # Return empty file with headers
                if format == 'csv':
                    return b""
                elif format == 'xlsx':
                    output = io.BytesIO()
                    df = pd.DataFrame()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Data', index=False)
                    return output.getvalue()
                elif format == 'json':
                    return json.dumps([], indent=2).encode('utf-8')

            if format == 'csv':
                df = pd.DataFrame(data)
                output = io.StringIO()
                df.to_csv(output, index=False)
                return output.getvalue().encode('utf-8')

            elif format == 'xlsx':
                output = io.BytesIO()
                df = pd.DataFrame(data)
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)
                return output.getvalue()

            elif format == 'json':
                return json.dumps(data, indent=2, default=str).encode('utf-8')

            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            raise


# Global instance
import_export_service = ImportExportService()
