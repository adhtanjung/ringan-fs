"""
Data Import Service for Excel Datasets
Handles importing and vectorizing mental health data from Excel files
"""

import logging
import pandas as pd
import asyncio
from typing import List, Dict, Optional, Any
from pathlib import Path
from qdrant_client.models import PointStruct

from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service
from app.services.data_cleaning_service import data_cleaning_service
from app.services.dataset_management_service import dataset_management_service
from app.core.database import get_mongodb
from app.models.dataset_models import (
    ProblemCategoryModel, AssessmentQuestionModel, TherapeuticSuggestionModel,
    FeedbackPromptModel, FineTuningExampleModel
)
from app.models.vector_models import (
    AssessmentQuestion, TherapeuticSuggestion,
    FeedbackPrompt, TrainingExample
)

logger = logging.getLogger(__name__)


class DataImportService:
    """Service for importing and processing Excel mental health datasets"""

    def __init__(self):
        # Get the absolute path to the data directory
        # Since the service runs from the backend directory, we can use a relative path
        self.data_dir = Path("data")
        self.excel_files = {
            "stress": "stress.xlsx",
            "anxiety": "anxiety.xlsx",
            "trauma": "trauma.xlsx",
            "general": "mentalhealthdata.xlsx"
        }
        # Counters to handle duplicate IDs
        self.id_counters = {
            'category': {},
            'question': {},
            'suggestion': {},
            'prompt': {},
            'action': {},
            'example': {}
        }
        # Initialize data cleaning service
        self.data_cleaning_service = data_cleaning_service

    async def initialize(self) -> bool:
        """Initialize the data import service"""
        try:
            # Initialize database connections first
            from app.core.database import init_db
            await init_db()

            # Initialize dataset management service (which handles MongoDB)
            await dataset_management_service.initialize()

            # Initialize vector and embedding services
            await vector_service.connect()
            await vector_service.create_collections()
            await embedding_service.initialize()

            logger.info("✅ Data import service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize data import service: {str(e)}")
            return False

    def read_excel_file(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """Read Excel file and return all sheets as DataFrames"""
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return {}

            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            sheets = {}

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # For assessment sheets, preserve original response_type before cleaning
                if '1.2 Self Assessment' in sheet_name and 'response_type' in df.columns:
                    df['original_response_type'] = df['response_type'].copy()
                    logger.info(f"🔄 Preserved original response_type for {sheet_name}")

                # Clean the dataframe
                cleaned_df = data_cleaning_service.clean_dataframe(df, sheet_name)

                # Validate cleaned data
                validation = data_cleaning_service.validate_cleaned_data(cleaned_df, sheet_name)

                if validation["valid"]:
                    sheets[sheet_name] = cleaned_df
                    logger.info(f"✅ Cleaned sheet '{sheet_name}': {validation['rows']} rows")
                else:
                    logger.warning(f"⚠️ Sheet '{sheet_name}' validation failed: {validation['errors']}")
                    # Still include the sheet but log the issues
                    sheets[sheet_name] = cleaned_df

            logger.info(f"✅ Read and cleaned {len(sheets)} sheets from {file_path.name}")
            return sheets

        except Exception as e:
            logger.error(f"❌ Failed to read Excel file {file_path}: {str(e)}")
            return {}

    # Removed duplicate _transform_category_id method - using the one below with 2-digit format

    def _transform_sub_category_id(self, original_id: str, domain: str) -> str:
        """Transform sub_category_id from Excel format (P001-1) to validation format (ANX_001_01)"""
        domain_prefixes = {
            'anxiety': 'ANX',
            'stress': 'STR',
            'trauma': 'TRA',
            'general': 'GEN'
        }

        prefix = domain_prefixes.get(domain, 'GEN')

        # Extract numbers from original ID (e.g., P004-1 -> 04, 01)
        import re
        match = re.search(r'(\d+)[-_](\d+)', original_id)
        if match:
            # Convert to int first to remove leading zeros, then format consistently
            main_num_int = int(match.group(1))
            sub_num_int = int(match.group(2))
            main_num = f"{main_num_int:02d}"  # 2 digits for category to match category_id
            sub_num = f"{sub_num_int:02d}"    # 2 digits for sub number

            # Generate consistent ID - same original_id should always map to same transformed ID
            base_id = f"{prefix}_{main_num}_{sub_num}"
            counter_key = f"{domain}_{original_id}"

            # Store the mapping for consistency, but don't increment for duplicates
            # Multiple assessments can have the same sub_category_id
            if counter_key not in self.id_counters['category']:
                self.id_counters['category'][counter_key] = base_id

            return self.id_counters['category'][counter_key]

        return f"{prefix}_01_01"  # Default fallback

    def _transform_category_id(self, original_id: str, domain: str) -> str:
        """Transform category_id from Excel format (P001) to validation format (STR_01)"""
        domain_prefixes = {
            'anxiety': 'ANX',
            'stress': 'STR',
            'trauma': 'TRA',
            'general': 'GEN'
        }

        prefix = domain_prefixes.get(domain, 'GEN')

        # Extract numbers from original ID (e.g., P004 -> 04)
        import re
        match = re.search(r'P(\d+)', original_id)
        if match:
            # Convert to int first to remove leading zeros, then format as 2 digits
            num_int = int(match.group(1))
            num = f"{num_int:02d}"  # Ensure 2 digits for category

            # Generate consistent ID - same original_id should always map to same transformed ID
            base_id = f"{prefix}_{num}"
            counter_key = f"{domain}_{original_id}"

            # Store the mapping for consistency, but don't increment for duplicates
            # Multiple problems can have the same category_id
            if counter_key not in self.id_counters['category']:
                self.id_counters['category'][counter_key] = base_id

            return self.id_counters['category'][counter_key]

        return f"{prefix}_01"  # Default fallback

    def _transform_suggestion_id(self, original_id: str, domain: str) -> str:
        """Transform suggestion_id from Excel format (S001) to validation format (S_STR_001)"""
        domain_prefixes = {
            'anxiety': 'ANX',
            'stress': 'STR',
            'trauma': 'TRA',
            'general': 'GEN'
        }

        prefix = domain_prefixes.get(domain, 'GEN')

        # Extract numbers from original ID (e.g., S001 -> 001)
        import re
        match = re.search(r'S(\d+)', original_id)
        if match:
            num = match.group(1).zfill(3)  # Ensure 3 digits

            # Generate consistent ID - same original_id should always map to same transformed ID
            base_id = f"S_{prefix}_{num}"
            counter_key = f"{domain}_{original_id}"

            # Store the mapping for consistency, but don't increment for duplicates
            # Multiple suggestions can have the same suggestion_id
            if counter_key not in self.id_counters['suggestion']:
                self.id_counters['suggestion'][counter_key] = base_id

            return self.id_counters['suggestion'][counter_key]

        return f"S_{prefix}_001"  # Default fallback

    def _transform_prompt_id(self, original_id: str, domain: str) -> str:
        """Transform prompt_id from Excel format (F001) to validation format (P_STR_001)"""
        domain_prefixes = {
            'anxiety': 'ANX',
            'stress': 'STR',
            'trauma': 'TRA',
            'general': 'GEN'
        }

        prefix = domain_prefixes.get(domain, 'GEN')

        # Extract numbers from original ID (e.g., F001 -> 001)
        import re
        match = re.search(r'F(\d+)', original_id)
        if match:
            num = match.group(1).zfill(3)  # Ensure 3 digits

            # Generate consistent ID - same original_id should always map to same transformed ID
            base_id = f"P_{prefix}_{num}"
            counter_key = f"{domain}_{original_id}"

            # Store the mapping for consistency, but don't increment for duplicates
            # Multiple feedback prompts can have the same prompt_id
            if counter_key not in self.id_counters['prompt']:
                self.id_counters['prompt'][counter_key] = base_id

            return self.id_counters['prompt'][counter_key]

        return f"P_{prefix}_001"  # Default fallback

    def _transform_question_id(self, original_id: str, domain: str) -> str:
        """Transform question_id from Excel format (Q001) to validation format (Q001) with domain offset"""
        domain_offsets = {
            'stress': 0,      # Q001-Q999
            'anxiety': 1000,  # Q1001-Q1999
            'trauma': 2000,   # Q2001-Q2999
            'general': 3000   # Q3001-Q3999
        }

        offset = domain_offsets.get(domain, 0)

        # Extract numbers from original ID (e.g., Q001 -> 001)
        import re
        match = re.search(r'Q(\d+)', original_id)
        if match:
            original_num = int(match.group(1))
            new_num = original_num + offset

            # Generate consistent ID - same original_id should always map to same transformed ID
            base_id = f"Q{new_num:04d}"
            counter_key = f"{domain}_{original_id}"

            # Store the mapping for consistency, but don't increment for duplicates
            # Multiple assessments can have the same question_id
            if counter_key not in self.id_counters['question']:
                self.id_counters['question'][counter_key] = base_id

            return self.id_counters['question'][counter_key]

        return f"Q{offset + 1:04d}"  # Default fallback

    def _transform_action_id(self, original_id: str, domain: str) -> str:
        """Transform action_id from Excel format (A01) to validation format (A_001) with domain offset"""
        domain_offsets = {
            'stress': 0,      # A_001-A_099
            'anxiety': 100,   # A_101-A_199
            'trauma': 200,    # A_201-A_299
            'general': 300    # A_301-A_399
        }

        offset = domain_offsets.get(domain, 0)

        # Extract numbers from original ID (e.g., A01 -> 01)
        import re
        match = re.search(r'A(\d+)', original_id)
        if match:
            original_num = int(match.group(1))
            new_num = original_num + offset
            return f"A_{new_num:03d}"  # Ensure 3 digits

        return f"A_{offset + 1:03d}"  # Default fallback

    async def process_problems_sheet(self, df: pd.DataFrame) -> List[ProblemCategoryModel]:
        """Process problems sheet and return ProblemCategoryModel objects"""
        try:
            problems = []

            for _, row in df.iterrows():
                try:
                    # Remove category_id if present in import data (it's derived from problem_types)
                    row_dict = row.to_dict()
                    if 'category_id' in row_dict:
                        logger.warning(f"Ignoring category_id in problems import (derived from problem_types)")
                        del row_dict['category_id']

                    # Use sub_category_id as-is
                    original_sub_category_id = str(row_dict.get('sub_category_id', ''))
                    transformed_sub_category_id = original_sub_category_id

                    logger.info(f"🔄 Transforming sub_category_id: {original_sub_category_id} -> {transformed_sub_category_id}")

                    problem = ProblemCategoryModel(
                        sub_category_id=transformed_sub_category_id,
                        category=str(row_dict.get('category', '')),  # Must exist in problem_types
                        problem_name=str(row_dict.get('problem_name', '')),
                        description=str(row_dict.get('description', ''))
                    )
                    problems.append(problem)
                except Exception as e:
                    logger.warning(f"Skipping invalid problem row: {e}")
                    continue

            logger.info(f"✅ Processed {len(problems)} problems")
            return problems

        except Exception as e:
            logger.error(f"❌ Failed to process problems sheet: {str(e)}")
            return []

    async def process_assessments_sheet(self, df: pd.DataFrame) -> List[AssessmentQuestion]:
        """Process assessments sheet and return AssessmentQuestion objects"""
        print(f"🔄 PROCESS_ASSESSMENTS_SHEET CALLED")
        logger.info(f"🔄 PROCESS_ASSESSMENTS_SHEET CALLED")
        try:
            print(f"🔄 Importing ResponseType...")
            from app.models.vector_models import ResponseType
            import re
            print(f"🔄 ResponseType imported successfully")
            questions = []
            print(f"🔄 DataFrame shape: {df.shape}")
            print(f"🔄 DataFrame columns: {list(df.columns)}")
            logger.info(f"🔄 STARTING process_assessments_sheet with {len(df)} rows")
            logger.info(f"DataFrame columns: {list(df.columns)}")
            logger.info(f"First few response_type values: {df['response_type'].head().tolist()}")
            print(f"🔄 Starting to process {len(df)} rows...")

            for idx, row in df.iterrows():
                if idx < 5:  # Debug first 5 rows
                    print(f"🔄 Processing row {idx}: question_id={row.get('question_id')}, response_type={row.get('response_type')}")
                try:
                    # Get the cleaned response type (already processed by data cleaning service)
                    response_type_cleaned = str(row.get('response_type', 'text')).strip().lower()

                    # Get the original response_type that we preserved before cleaning
                    original_response_type = str(row.get('original_response_type', response_type_cleaned)).strip()

                    if idx < 5:  # Debug first 5 rows
                        print(f"🔄 Row {idx}: cleaned='{response_type_cleaned}', original='{original_response_type}'")

                    # Skip rows with invalid response_type (like Q062, Q072 which are question IDs)
                    if response_type_cleaned.startswith('q') and response_type_cleaned[1:].isdigit():
                        logger.warning(f"Skipping row with invalid response_type (question ID): {response_type_cleaned} for question {row.get('question_id')}")
                        continue

                    # Skip rows with NaN response_type
                    if pd.isna(row.get('response_type')) or response_type_cleaned == 'nan':
                        logger.warning(f"Skipping row with NaN response_type for question {row.get('question_id')}")
                        continue

                    # Map response type to enum
                    if response_type_cleaned == 'scale':
                        response_type = ResponseType.SCALE
                    elif response_type_cleaned == 'multiple_choice':
                        response_type = ResponseType.MULTIPLE_CHOICE
                    elif response_type_cleaned == 'text':
                        response_type = ResponseType.TEXT
                    else:
                        response_type = ResponseType.TEXT  # Default

                    # Extract scale min/max if it's a scale question
                    scale_min = None
                    scale_max = None

                    if response_type == ResponseType.SCALE:
                        # Standardize to 1-4 scale
                        scale_min = 1
                        scale_max = 4

                        # Parse scale labels from columns
                        scale_labels = {
                            "1": row.get('scale_label_1', 'Not at all'),
                            "2": row.get('scale_label_2', 'A little'),
                            "3": row.get('scale_label_3', 'Quite a bit'),
                            "4": row.get('scale_label_4', 'Very much')
                        }

                        if idx < 5:
                            print(f"🔄 Row {idx}: Using standardized 1-4 scale with labels: {scale_labels}")

                    # Debug logging for scale questions
                    if response_type == ResponseType.SCALE and idx < 5:
                        logger.info(f"Creating scale question {row.get('question_id')}: response_type_str='{response_type_cleaned}', scale_min={scale_min}, scale_max={scale_max}")

                    try:
                        # Use IDs as-is
                        original_sub_category_id = str(row.get('sub_category_id', ''))
                        transformed_sub_category_id = original_sub_category_id

                        original_question_id = str(row.get('question_id', ''))
                        transformed_question_id = original_question_id

                        question = AssessmentQuestion(
                            question_id=transformed_question_id,
                            sub_category_id=transformed_sub_category_id,
                            batch_id=str(row.get('batch_id', '')),
                            question_text=str(row.get('question_text', '')),
                            response_type=response_type,
                            next_step=str(row.get('next_step', '')) if pd.notna(row.get('next_step')) else None,
                            clusters=str(row.get('clusters', '')).split(',') if pd.notna(row.get('clusters')) else None,
                            scale_min=scale_min,
                            scale_max=scale_max,
                            scale_labels=scale_labels if response_type == ResponseType.SCALE else None
                        )
                        questions.append(question)
                    except Exception as question_error:
                        logger.error(f"Failed to create AssessmentQuestion for {row.get('question_id')}: {question_error}")
                        continue
                except Exception as e:
                    logger.warning(f"Skipping invalid assessment row: {e}")
                    continue

            logger.info(f"✅ Processed {len(questions)} assessment questions")
            return questions

        except Exception as e:
            logger.error(f"❌ Failed to process assessments sheet: {str(e)}")
            return []

    async def process_suggestions_sheet(self, df: pd.DataFrame) -> List[TherapeuticSuggestion]:
        """Process suggestions sheet and return TherapeuticSuggestion objects"""
        try:
            suggestions = []

            for idx, row in df.iterrows():
                try:
                    # Use IDs as-is
                    original_sub_category_id = str(row.get('sub_category_id', ''))
                    transformed_sub_category_id = original_sub_category_id

                    # Use suggestion_id as-is
                    original_suggestion_id = str(row.get('suggestion_id', ''))
                    transformed_suggestion_id = original_suggestion_id

                    suggestion = TherapeuticSuggestion(
                        suggestion_id=transformed_suggestion_id,
                        sub_category_id=transformed_sub_category_id,
                        cluster=str(row.get('cluster', '')),
                        suggestion_text=str(row.get('suggestion_text', '')),
                        resource_link=str(row.get('resource_link', '')) if pd.notna(row.get('resource_link')) else None,
                        evidence_based=bool(row.get('evidence_based', True))
                    )
                    suggestions.append(suggestion)
                except Exception as e:
                    logger.warning(f"Skipping invalid suggestion row: {e}")
                    continue

            logger.info(f"✅ Processed {len(suggestions)} therapeutic suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"❌ Failed to process suggestions sheet: {str(e)}")
            return []

    def _map_next_action_to_id(self, next_action_text: str) -> str:
        """Map complex next_action text to simple action_id"""
        next_action_lower = next_action_text.lower()

        # Map based on keywords in the next_action text
        if 'continue' in next_action_lower and ('same' in next_action_lower or 'coaching' in next_action_lower):
            return 'continue_same'
        elif 'problem menu' in next_action_lower or 'show problem' in next_action_lower:
            return 'show_problem_menu'
        elif 'end session' in next_action_lower:
            return 'end_session'
        elif 'escalate' in next_action_lower:
            return 'escalate'
        elif 'schedule' in next_action_lower and 'followup' in next_action_lower:
            return 'schedule_followup'
        elif 'different' in next_action_lower and ('technique' in next_action_lower or 'prompts' in next_action_lower):
            return 'offer_resource'
        elif 'follow-up' in next_action_lower or 'deeper' in next_action_lower:
            return 'ask_clarification'
        else:
            # Default fallback
            return 'continue_same'

    async def process_feedback_sheet(self, df: pd.DataFrame) -> List[FeedbackPrompt]:
        """Process feedback sheet and return FeedbackPrompt objects"""
        try:
            prompts = []

            for idx, row in df.iterrows():
                try:
                    # Use prompt_id as-is
                    original_prompt_id = str(row.get('prompt_id', ''))
                    transformed_prompt_id = original_prompt_id

                    # Map next_action text to action_id
                    next_action_text = str(row.get('next_action', ''))
                    next_action_id = self._map_next_action_to_id(next_action_text)

                    prompt = FeedbackPrompt(
                        prompt_id=transformed_prompt_id,
                        stage=str(row.get('stage', '')),
                        prompt_text=str(row.get('prompt_text', '')),
                        next_action=next_action_id,
                        domain=domain
                    )
                    prompts.append(prompt)
                except Exception as e:
                    logger.warning(f"Skipping invalid feedback row: {e}")
                    continue

            logger.info(f"✅ Processed {len(prompts)} feedback prompts")
            return prompts

        except Exception as e:
            logger.error(f"❌ Failed to process feedback sheet: {str(e)}")
            return []

    async def process_training_sheet(self, df: pd.DataFrame) -> List[TrainingExample]:
        """Process training sheet and return TrainingExample objects"""
        try:
            examples = []

            for _, row in df.iterrows():
                try:
                    # Transform sub_category_id to expected format if present
                    original_sub_category_id = str(row.get('sub_category_id', '')) if pd.notna(row.get('sub_category_id')) else None
                    transformed_sub_category_id = self._transform_sub_category_id(original_sub_category_id, domain) if original_sub_category_id else None

                    # Convert ID to proper example_id format (E_DOMAIN_###)
                    raw_id = row.get('id', '')
                    if pd.notna(raw_id):
                        raw_id_str = str(raw_id)
                        try:
                            # Handle train_ prefixed IDs from data cleaning
                            if raw_id_str.startswith('train_'):
                                # Extract numeric part after 'train_'
                                numeric_part = raw_id_str.replace('train_', '')
                                numeric_id = int(numeric_part)
                            else:
                                # Convert to int first to remove decimal
                                numeric_id = int(float(raw_id))

                            # Format as E_DOMAIN_### (e.g., E_STR_001)
                            domain_prefixes = {
                                'anxiety': 'ANX',
                                'stress': 'STR',
                                'trauma': 'TRA',
                                'general': 'GEN'
                            }
                            domain_prefix = domain_prefixes.get(domain, 'GEN')

                            # Generate unique ID by checking for duplicates
                            base_id = f"E_{domain_prefix}_{numeric_id:03d}"
                            counter_key = f"{domain}_{raw_id_str}"

                            if counter_key in self.id_counters['example']:
                                # If duplicate, increment the number
                                self.id_counters['example'][counter_key] += 1
                                new_num = numeric_id + self.id_counters['example'][counter_key]
                                example_id = f"E_{domain_prefix}_{new_num:03d}"
                            else:
                                self.id_counters['example'][counter_key] = 0
                                example_id = base_id
                        except (ValueError, TypeError):
                            # Fallback to original value if conversion fails
                            domain_prefixes = {
                                'anxiety': 'ANX',
                                'stress': 'STR',
                                'trauma': 'TRA',
                                'general': 'GEN'
                            }
                            domain_prefix = domain_prefixes.get(domain, 'GEN')
                            example_id = f"E_{domain_prefix}_{str(raw_id)}"
                    else:
                        example_id = ''

                    example = TrainingExample(
                        example_id=example_id,
                        problem=str(row.get('problem', '')),
                        conversation_id=str(row.get('ConversationID', '')),
                        prompt=str(row.get('prompt', '')),
                        completion=str(row.get('completion', '')),
                        sub_category_id=transformed_sub_category_id
                    )
                    examples.append(example)
                except Exception as e:
                    logger.warning(f"Skipping invalid training row: {e}")
                    continue

            logger.info(f"✅ Processed {len(examples)} training examples")
            return examples

        except Exception as e:
            logger.error(f"❌ Failed to process training sheet: {str(e)}")
            return []

    async def vectorize_and_store_problems(self, problems: List[ProblemCategoryModel]) -> bool:
        """Vectorize and store problems in Qdrant"""
        try:
            if not problems:
                return True

            # Prepare text-metadata pairs
            text_metadata_pairs = []
            for problem in problems:
                text = f"{problem.problem_name} {problem.description}"
                metadata = {
                    "text": text,
                    "type": "problem",
                    "category_id": problem.category_id,
                    "sub_category_id": problem.sub_category_id,
                    "category": problem.category,
                    "problem_name": problem.problem_name,
                    "description": problem.description,
                    "domain": problem.domain
                }
                text_metadata_pairs.append({"text": text, "metadata": metadata})

            # Generate embeddings
            embeddings = await embedding_service.generate_embeddings_with_metadata_batch(
                text_metadata_pairs
            )

            # Create points for Qdrant
            points = []
            for i, (problem, embedding_result) in enumerate(zip(problems, embeddings)):
                if embedding_result:
                    point = PointStruct(
                        id=i,  # Use simple integer ID
                        vector=embedding_result["embedding"],
                        payload=embedding_result["metadata"]
                    )
                    points.append(point)

            # Store in Qdrant
            if points:
                success = await vector_service.upsert_points(
                    "mental-health-problems", points
                )
                return success

            return True

        except Exception as e:
            logger.error(f"❌ Failed to vectorize and store problems: {str(e)}")
            return False

    async def vectorize_and_store_assessments(self, questions: List[AssessmentQuestion]) -> bool:
        """Vectorize and store assessment questions in Qdrant"""
        try:
            if not questions:
                return True

            # Prepare text-metadata pairs
            text_metadata_pairs = []
            for question in questions:
                metadata = {
                    "text": question.question_text,
                    "type": "assessment",
                    "question_id": question.question_id,
                    "sub_category_id": question.sub_category_id,
                    "batch_id": question.batch_id,
                    "response_type": question.response_type,
                    "next_step": question.next_step,
                    "clusters": question.clusters,
                    "domain": question.domain
                }

                # Add scale information if it's a scale question
                if hasattr(question, 'scale_min') and hasattr(question, 'scale_max'):
                    metadata["scale_min"] = question.scale_min
                    metadata["scale_max"] = question.scale_max
                elif question.response_type == "scale":
                    # Default scale values if not provided
                    metadata["scale_min"] = 1
                    metadata["scale_max"] = 4
                text_metadata_pairs.append({"text": question.question_text, "metadata": metadata})

            # Generate embeddings
            embeddings = await embedding_service.generate_embeddings_with_metadata_batch(
                text_metadata_pairs
            )

            # Create points for Qdrant
            points = []
            for i, (question, embedding_result) in enumerate(zip(questions, embeddings)):
                if embedding_result:
                    point = PointStruct(
                        id=i,  # Use simple integer ID
                        vector=embedding_result["embedding"],
                        payload=embedding_result["metadata"]
                    )
                    points.append(point)

            # Store in Qdrant
            if points:
                success = await vector_service.upsert_points(
                    "mental-health-assessments", points
                )
                return success

            return True

        except Exception as e:
            logger.error(f"❌ Failed to vectorize and store assessments: {str(e)}")
            return False

    async def vectorize_and_store_suggestions(self, suggestions: List[TherapeuticSuggestion]) -> bool:
        """Vectorize and store therapeutic suggestions in Qdrant"""
        try:
            if not suggestions:
                return True

            # Prepare text-metadata pairs
            text_metadata_pairs = []
            for suggestion in suggestions:
                metadata = {
                    "text": suggestion.suggestion_text,
                    "type": "suggestion",
                    "suggestion_id": suggestion.suggestion_id,
                    "sub_category_id": suggestion.sub_category_id,
                    "cluster": suggestion.cluster,
                    "resource_link": suggestion.resource_link,
                    "evidence_based": suggestion.evidence_based,
                    "domain": suggestion.domain
                }
                text_metadata_pairs.append({"text": suggestion.suggestion_text, "metadata": metadata})

            # Generate embeddings
            embeddings = await embedding_service.generate_embeddings_with_metadata_batch(
                text_metadata_pairs
            )

            # Create points for Qdrant
            points = []
            for i, (suggestion, embedding_result) in enumerate(zip(suggestions, embeddings)):
                if embedding_result:
                    point = PointStruct(
                        id=i,  # Use simple integer ID
                        vector=embedding_result["embedding"],
                        payload=embedding_result["metadata"]
                    )
                    points.append(point)

            # Store in Qdrant
            if points:
                success = await vector_service.upsert_points(
                    "mental-health-suggestions", points
                )
                return success

            return True

        except Exception as e:
            logger.error(f"❌ Failed to vectorize and store suggestions: {str(e)}")
            return False

    async def vectorize_and_store_feedback(self, feedback_prompts: List[FeedbackPrompt]) -> bool:
        """Vectorize and store feedback prompts in Qdrant"""
        try:
            if not feedback_prompts:
                return True

            # Prepare text-metadata pairs
            text_metadata_pairs = []
            for prompt in feedback_prompts:
                metadata = {
                    "text": prompt.prompt_text,
                    "type": "feedback",
                    "prompt_id": prompt.prompt_id,
                    "stage": prompt.stage,
                    "next_action": prompt.next_action,
                    "domain": prompt.domain
                }
                text_metadata_pairs.append({"text": prompt.prompt_text, "metadata": metadata})

            # Generate embeddings
            embeddings = await embedding_service.generate_embeddings_with_metadata_batch(
                text_metadata_pairs
            )

            # Create points for Qdrant
            points = []
            for i, (prompt, embedding_result) in enumerate(zip(feedback_prompts, embeddings)):
                if embedding_result:
                    point = PointStruct(
                        id=i,  # Use simple integer ID
                        vector=embedding_result["embedding"],
                        payload=embedding_result["metadata"]
                    )
                    points.append(point)

            # Store in Qdrant
            if points:
                success = await vector_service.upsert_points(
                    "mental-health-feedback", points
                )
                return success

            return True

        except Exception as e:
            logger.error(f"❌ Failed to vectorize and store feedback: {str(e)}")
            return False

    async def vectorize_and_store_training(self, training_examples: List[TrainingExample]) -> bool:
        """Vectorize and store training examples in Qdrant"""
        try:
            if not training_examples:
                return True

            # Prepare text-metadata pairs
            text_metadata_pairs = []
            for example in training_examples:
                # Combine prompt and completion for better searchability
                text = f"{example.prompt} {example.completion}"
                metadata = {
                    "text": text,
                    "type": "training",
                    "example_id": example.example_id,
                    "problem": example.problem,
                    "conversation_id": example.conversation_id,
                    "prompt": example.prompt,
                    "completion": example.completion,
                    "domain": example.domain,
                    "sub_category_id": example.sub_category_id
                }
                text_metadata_pairs.append({"text": text, "metadata": metadata})

            # Generate embeddings
            embeddings = await embedding_service.generate_embeddings_with_metadata_batch(
                text_metadata_pairs
            )

            # Create points for Qdrant
            points = []
            for i, (example, embedding_result) in enumerate(zip(training_examples, embeddings)):
                if embedding_result:
                    point = PointStruct(
                        id=i,  # Use simple integer ID
                        vector=embedding_result["embedding"],
                        payload=embedding_result["metadata"]
                    )
                    points.append(point)

            # Store in Qdrant
            if points:
                success = await vector_service.upsert_points(
                    "mental-health-training", points
                )
                return success

            return True

        except Exception as e:
            logger.error(f"❌ Failed to vectorize and store training: {str(e)}")
            return False

    async def import_domain_data(self, domain: str) -> Dict[str, Any]:
        """Import and process data for a specific domain"""
        try:
            logger.info(f"🔄 Starting data import for domain: {domain}")

            if domain not in self.excel_files:
                return {"success": False, "error": f"Unknown domain: {domain}"}

            file_path = self.data_dir / self.excel_files[domain]
            sheets = self.read_excel_file(file_path)

            if not sheets:
                return {"success": False, "error": f"Failed to read Excel file for {domain}"}

            results = {
                "domain": domain,
                "problems": 0,
                "assessments": 0,
                "suggestions": 0,
                "next_actions": 0,
                "feedback": 0,
                "training": 0,
                "success": True
            }

            # Process problems
            if "1.1 Problems" in sheets:
                problems = await self.process_problems_sheet(sheets["1.1 Problems"], domain)
                if problems:
                    success = await self.store_problems_via_dataset_service(problems)
                    results["problems"] = len(problems)
                    if not success:
                        results["success"] = False

            # Process assessments
            if "1.2 Self Assessment" in sheets:
                questions = await self.process_assessments_sheet(sheets["1.2 Self Assessment"], domain)
                if questions:
                    success = await self.store_assessments_via_dataset_service(questions)
                    results["assessments"] = len(questions)
                    if not success:
                        results["success"] = False

            # Process suggestions
            if "1.3 Suggestions" in sheets:
                suggestions = await self.process_suggestions_sheet(sheets["1.3 Suggestions"], domain)
                if suggestions:
                    success = await self.store_suggestions_via_dataset_service(suggestions)
                    results["suggestions"] = len(suggestions)
                    if not success:
                        results["success"] = False

            # Process next actions first (required for feedback validation)
            if "1.5 Next Action After Feedback" in sheets and not sheets["1.5 Next Action After Feedback"].empty:
                next_actions = await self.process_next_actions_sheet(sheets["1.5 Next Action After Feedback"], domain)
                if next_actions:
                    success = await self.store_next_actions_via_dataset_service(next_actions)
                    results["next_actions"] = len(next_actions)
                    if not success:
                        results["success"] = False

            # Process feedback
            if "1.4 Feedback Prompts" in sheets and not sheets["1.4 Feedback Prompts"].empty:
                feedback = await self.process_feedback_sheet(sheets["1.4 Feedback Prompts"], domain)
                if feedback:
                    success = await self.store_feedback_via_dataset_service(feedback)
                    results["feedback"] = len(feedback)
                    if not success:
                        results["success"] = False

            # Process training examples
            if "1.6 FineTuning Examples" in sheets and not sheets["1.6 FineTuning Examples"].empty:
                training = await self.process_training_sheet(sheets["1.6 FineTuning Examples"], domain)
                if training:
                    success = await self.store_training_via_dataset_service(training)
                    results["training"] = len(training)
                    if not success:
                        results["success"] = False

            logger.info(f"✅ Completed data import for {domain}: {results}")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to import data for {domain}: {str(e)}")
            return {"success": False, "error": str(e)}

    def _reset_id_counters(self):
        """Reset ID counters for a fresh import"""
        self.id_counters = {
            'category': {},
            'question': {},
            'suggestion': {},
            'prompt': {},
            'action': {}
        }

    async def import_all_data(self) -> Dict[str, Any]:
        """Import and process all domain data"""
        try:
            logger.info("🔄 Starting import of all mental health data")

            # Reset ID counters for fresh import
            self._reset_id_counters()

            await self.initialize()

            all_results = {}
            total_stats = {
                "problems": 0,
                "assessments": 0,
                "suggestions": 0,
                "feedback": 0,
                "training": 0,
                "success": True
            }

            for domain in self.excel_files.keys():
                result = await self.import_domain_data(domain)
                all_results[domain] = result

                if result["success"]:
                    total_stats["problems"] += result["problems"]
                    total_stats["assessments"] += result["assessments"]
                    total_stats["suggestions"] += result["suggestions"]
                    total_stats["feedback"] += result["feedback"]
                    total_stats["training"] += result["training"]
                else:
                    total_stats["success"] = False

            all_results["total"] = total_stats
            logger.info(f"✅ Completed import of all data: {total_stats}")

            return all_results

        except Exception as e:
            logger.error(f"❌ Failed to import all data: {str(e)}")
            return {"success": False, "error": str(e)}

    async def store_problems_via_dataset_service(self, problems: List[ProblemCategoryModel]) -> bool:
        """Store problems using dataset management service"""
        try:
            for problem in problems:
                problem_data = {
                    "domain": problem.domain,
                    "category": problem.category,
                    "sub_category_id": problem.sub_category_id,
                    "problem_name": problem.problem_name,
                    "description": problem.description,
                    "severity_level": 3  # Default severity level since not provided in Excel files
                }
                await dataset_management_service.create_item("problems", problem_data)

            logger.info(f"✅ Stored {len(problems)} problems via dataset management service")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store problems via dataset service: {str(e)}")
            return False

    async def store_assessments_via_dataset_service(self, assessments: List[AssessmentQuestion]) -> bool:
        """Store assessments using dataset management service"""
        try:
            from app.models.dataset_models import ResponseType

            for assessment in assessments:
                # The response_type is already a ResponseType enum from processing
                response_type = assessment.response_type

                # Prepare all fields including conditional ones
                scale_min = getattr(assessment, 'scale_min', None)
                scale_max = getattr(assessment, 'scale_max', None)
                options = getattr(assessment, 'options', []) if response_type == ResponseType.MULTIPLE_CHOICE else None

                # Debug: Check what we're getting from the assessment object
                logger.info(f"Assessment object attributes: scale_min={scale_min}, scale_max={scale_max}, response_type={response_type}")
                logger.info(f"Assessment object dict: {assessment.model_dump()}")

                # Convert clusters from list to comma-separated string for dataset model
                clusters = getattr(assessment, 'clusters', None)
                if clusters and isinstance(clusters, list):
                    clusters = ','.join(clusters)

                assessment_data = {
                    "question_id": assessment.question_id,
                    "sub_category_id": assessment.sub_category_id,
                    "question_text": assessment.question_text,
                    "response_type": response_type,
                    "batch_id": getattr(assessment, 'batch_id', None),
                    "next_step": getattr(assessment, 'next_step', None),
                    "clusters": clusters,
                    "scale_min": scale_min,
                    "scale_max": scale_max,
                    "scale_labels": getattr(assessment, 'scale_labels', None),
                    "options": options
                }

                # Debug logging for sub_category_id format
                logger.debug(f"🔄 Sub-category ID format: '{assessment.sub_category_id}'")
                logger.debug(f"🔄 Assessment data being sent: {assessment_data}")
                logger.debug(f"🔄 Sub-category ID format: '{assessment.sub_category_id}'")

                # Debug logging
                logger.info(f"Processing assessment {assessment.question_id}: response_type={response_type}, scale_min={scale_min}, scale_max={scale_max}")
                if response_type == ResponseType.SCALE:
                    logger.info(f"Scale question validation: question_id={assessment.question_id}, scale_min={scale_min}, scale_max={scale_max}, both_not_none={scale_min is not None and scale_max is not None}")
                    logger.info(f"Assessment data for scale question: {assessment_data}")

                try:
                    await dataset_management_service.create_item("assessments", assessment_data)
                    logger.info(f"✅ Successfully stored assessment {assessment.question_id}")
                except Exception as item_error:
                    logger.error(f"❌ Failed to store assessment {assessment.question_id}: {str(item_error)}")
                    raise

            logger.info(f"✅ Stored {len(assessments)} assessments via dataset management service")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store assessments via dataset service: {str(e)}")
            return False

    async def store_suggestions_via_dataset_service(self, suggestions: List[TherapeuticSuggestion]) -> bool:
        """Store suggestions using dataset management service"""
        try:
            for suggestion in suggestions:
                suggestion_data = {
                    "suggestion_id": suggestion.suggestion_id,
                    "sub_category_id": suggestion.sub_category_id,
                    "suggestion_text": suggestion.suggestion_text,
                    "cluster": suggestion.cluster,
                    "domain": suggestion.domain
                }
                await dataset_management_service.create_item("suggestions", suggestion_data)

            logger.info(f"✅ Stored {len(suggestions)} suggestions via dataset management service")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store suggestions via dataset service: {str(e)}")
            return False

    async def store_feedback_via_dataset_service(self, feedback_prompts: List[FeedbackPrompt]) -> bool:
        """Store feedback prompts using dataset management service"""
        try:
            # Create mapping from label to formatted action_id
            label_to_action_id = await self._get_label_to_action_id_mapping()

            for feedback in feedback_prompts:
                # Map next_action label to formatted action_id
                next_action_label = getattr(feedback, 'next_action', 'continue_same')
                next_action_id = label_to_action_id.get(next_action_label, next_action_label)

                feedback_data = {
                    "prompt_id": feedback.prompt_id,
                    "stage": feedback.stage,
                    "prompt_text": feedback.prompt_text,
                    "next_action_id": next_action_id,
                    "context": None
                }
                await dataset_management_service.create_item("feedback_prompts", feedback_data)

            logger.info(f"✅ Stored {len(feedback_prompts)} feedback prompts via dataset management service")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store feedback prompts via dataset service: {str(e)}")
            return False

    async def store_training_via_dataset_service(self, training_examples: List[TrainingExample]) -> bool:
        """Store training examples using dataset management service"""
        try:
            for training in training_examples:
                training_data = {
                    "example_id": training.example_id,
                    "domain": training.domain,
                    "problem": getattr(training, 'problem', ''),
                    "conversation_id": getattr(training, 'conversation_id', ''),
                    "user_intent": "problem_identification",  # Default intent
                    "prompt": training.prompt,
                    "completion": training.completion,
                    "context": None,
                    "quality_score": 0.8,
                    "tags": [training.domain]
                }
                if hasattr(training, 'sub_category_id') and training.sub_category_id:
                    training_data["sub_category_id"] = training.sub_category_id

                await dataset_management_service.create_item("training_examples", training_data)

            logger.info(f"✅ Stored {len(training_examples)} training examples via dataset management service")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store training examples via dataset service: {str(e)}")
            return False

    async def process_next_actions_sheet(self, df: pd.DataFrame, domain: str) -> List[Dict[str, Any]]:
        """Process next actions sheet and return next action objects"""
        try:
            next_actions = []
            logger.info(f"🔄 Processing next actions sheet for domain: {domain} with {len(df)} rows")

            for idx, row in df.iterrows():
                try:
                    original_action_id = str(row.get('action_id', '')).strip()
                    label = str(row.get('label', '')).strip()
                    description = str(row.get('description', '')).strip()

                    if not original_action_id:
                        continue

                    # Transform action_id to include domain prefix
                    transformed_action_id = self._transform_action_id(original_action_id, domain)

                    # Clean the label to ensure it's a valid NextActionType
                    cleaned_action_type = self.data_cleaning_service._clean_next_action(label)

                    next_action = {
                        'action_id': transformed_action_id,
                        'action_type': cleaned_action_type,
                        'label': label,  # Keep original label for reference
                        'description': description,
                        'domain': domain,
                        'original_id': original_action_id
                    }

                    next_actions.append(next_action)

                except Exception as e:
                    logger.warning(f"⚠️ Failed to process next action row {idx}: {str(e)}")
                    continue

            logger.info(f"✅ Processed {len(next_actions)} next actions for domain: {domain}")
            return next_actions

        except Exception as e:
            logger.error(f"❌ Failed to process next actions sheet for {domain}: {str(e)}")
            return []

    async def store_next_actions_via_dataset_service(self, next_actions: List[Dict[str, Any]]) -> bool:
        """Store next actions using dataset management service"""
        try:
            for action in next_actions:
                next_action_data = {
                    "action_id": action['action_id'],
                    "action_type": action['action_type'],
                    "action_name": action.get('label', action.get('description', '')),  # Use label as action_name, fallback to description
                    "description": action.get('description', ''),
                    "domain": action.get('domain', '')
                }
                await dataset_management_service.create_item("next_actions", next_action_data)

            logger.info(f"✅ Stored {len(next_actions)} next actions via dataset management service")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store next actions via dataset service: {str(e)}")
            return False

    async def _get_label_to_action_id_mapping(self) -> Dict[str, str]:
        """Get mapping from simplified action names to formatted action_id from database"""
        try:
            db = get_mongodb()
            if db is None:
                return {}

            db = db.mental_health_db
            mapping = {}

            # Create mapping from simplified action names to formatted action_ids
            async for action in db.next_actions.find({}, {"action_id": 1, "action_name": 1}):
                action_name = action.get('action_name', '')
                action_id = action.get('action_id', '')
                if action_name and action_id:
                    # Map the action_name to action_id
                    mapping[action_name] = action_id

                    # Also create mappings for simplified action names
                    if action_name == 'continue_same':
                        mapping['continue_same'] = action_id
                    elif action_name == 'show_problem_menu':
                        mapping['show_problem_menu'] = action_id
                    elif action_name == 'end_session':
                        mapping['end_session'] = action_id
                    elif action_name == 'escalate':
                        mapping['escalate'] = action_id
                    elif action_name == 'schedule_followup':
                        mapping['schedule_followup'] = action_id
                    elif action_name == 'offer_resource':
                        mapping['offer_resource'] = action_id
                    elif action_name == 'ask_clarification':
                        mapping['ask_clarification'] = action_id

            logger.info(f"✅ Created label to action_id mapping with {len(mapping)} entries")
            return mapping

        except Exception as e:
            logger.error(f"❌ Failed to create label to action_id mapping: {str(e)}")
            return {}


# Global data import service instance
data_import_service = DataImportService()
