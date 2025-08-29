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
from app.models.vector_models import (
    ProblemCategory, AssessmentQuestion, TherapeuticSuggestion,
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

    async def initialize(self) -> bool:
        """Initialize the data import service"""
        try:
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

    async def process_problems_sheet(self, df: pd.DataFrame, domain: str) -> List[ProblemCategory]:
        """Process problems sheet and return ProblemCategory objects"""
        try:
            problems = []

            for _, row in df.iterrows():
                try:
                    problem = ProblemCategory(
                        category_id=str(row.get('category_id', '')),
                        sub_category_id=str(row.get('sub_category_id', '')),
                        category=str(row.get('category', '')),
                        problem_name=str(row.get('problem_name', '')),
                        description=str(row.get('description', '')),
                        domain=domain
                    )
                    problems.append(problem)
                except Exception as e:
                    logger.warning(f"Skipping invalid problem row: {e}")
                    continue

            logger.info(f"✅ Processed {len(problems)} problems for {domain}")
            return problems

        except Exception as e:
            logger.error(f"❌ Failed to process problems sheet for {domain}: {str(e)}")
            return []

    async def process_assessments_sheet(self, df: pd.DataFrame, domain: str) -> List[AssessmentQuestion]:
        """Process assessments sheet and return AssessmentQuestion objects"""
        try:
            questions = []

            for _, row in df.iterrows():
                try:
                    question = AssessmentQuestion(
                        question_id=str(row.get('question_id', '')),
                        sub_category_id=str(row.get('sub_category_id', '')),
                        batch_id=str(row.get('batch_id', '')),
                        question_text=str(row.get('question_text', '')),
                        response_type=str(row.get('response_type', 'text')),
                        next_step=str(row.get('next_step', '')) if pd.notna(row.get('next_step')) else None,
                        clusters=str(row.get('clusters', '')).split(',') if pd.notna(row.get('clusters')) else None,
                        domain=domain
                    )
                    questions.append(question)
                except Exception as e:
                    logger.warning(f"Skipping invalid assessment row: {e}")
                    continue

            logger.info(f"✅ Processed {len(questions)} assessment questions for {domain}")
            return questions

        except Exception as e:
            logger.error(f"❌ Failed to process assessments sheet for {domain}: {str(e)}")
            return []

    async def process_suggestions_sheet(self, df: pd.DataFrame, domain: str) -> List[TherapeuticSuggestion]:
        """Process suggestions sheet and return TherapeuticSuggestion objects"""
        try:
            suggestions = []

            for _, row in df.iterrows():
                try:
                    suggestion = TherapeuticSuggestion(
                        suggestion_id=str(row.get('suggestion_id', '')),
                        sub_category_id=str(row.get('sub_category_id', '')),
                        cluster=str(row.get('cluster', '')),
                        suggestion_text=str(row.get('suggestion_text', '')),
                        resource_link=str(row.get('resource_link', '')) if pd.notna(row.get('resource_link')) else None,
                        evidence_based=bool(row.get('evidence_based', True)),
                        domain=domain
                    )
                    suggestions.append(suggestion)
                except Exception as e:
                    logger.warning(f"Skipping invalid suggestion row: {e}")
                    continue

            logger.info(f"✅ Processed {len(suggestions)} therapeutic suggestions for {domain}")
            return suggestions

        except Exception as e:
            logger.error(f"❌ Failed to process suggestions sheet for {domain}: {str(e)}")
            return []

    async def process_feedback_sheet(self, df: pd.DataFrame, domain: str) -> List[FeedbackPrompt]:
        """Process feedback sheet and return FeedbackPrompt objects"""
        try:
            prompts = []

            for _, row in df.iterrows():
                try:
                    prompt = FeedbackPrompt(
                        prompt_id=str(row.get('prompt_id', '')),
                        stage=str(row.get('stage', '')),
                        prompt_text=str(row.get('prompt_text', '')),
                        next_action=str(row.get('next_action', '')),
                        domain=domain
                    )
                    prompts.append(prompt)
                except Exception as e:
                    logger.warning(f"Skipping invalid feedback row: {e}")
                    continue

            logger.info(f"✅ Processed {len(prompts)} feedback prompts for {domain}")
            return prompts

        except Exception as e:
            logger.error(f"❌ Failed to process feedback sheet for {domain}: {str(e)}")
            return []

    async def process_training_sheet(self, df: pd.DataFrame, domain: str) -> List[TrainingExample]:
        """Process training sheet and return TrainingExample objects"""
        try:
            examples = []

            for _, row in df.iterrows():
                try:
                    example = TrainingExample(
                        example_id=str(row.get('id', '')),
                        problem=str(row.get('problem', '')),
                        conversation_id=str(row.get('ConversationID', '')),
                        prompt=str(row.get('prompt', '')),
                        completion=str(row.get('completion', '')),
                        domain=domain,
                        sub_category_id=str(row.get('sub_category_id', '')) if pd.notna(row.get('sub_category_id')) else None
                    )
                    examples.append(example)
                except Exception as e:
                    logger.warning(f"Skipping invalid training row: {e}")
                    continue

            logger.info(f"✅ Processed {len(examples)} training examples for {domain}")
            return examples

        except Exception as e:
            logger.error(f"❌ Failed to process training sheet for {domain}: {str(e)}")
            return []

    async def vectorize_and_store_problems(self, problems: List[ProblemCategory]) -> bool:
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
                "feedback": 0,
                "training": 0,
                "success": True
            }

            # Process problems
            if "1.1 Problems" in sheets:
                problems = await self.process_problems_sheet(sheets["1.1 Problems"], domain)
                if problems:
                    success = await self.vectorize_and_store_problems(problems)
                    results["problems"] = len(problems)
                    if not success:
                        results["success"] = False

            # Process assessments
            if "1.2 Self Assessment" in sheets:
                questions = await self.process_assessments_sheet(sheets["1.2 Self Assessment"], domain)
                if questions:
                    success = await self.vectorize_and_store_assessments(questions)
                    results["assessments"] = len(questions)
                    if not success:
                        results["success"] = False

            # Process suggestions
            if "1.3 Suggestions" in sheets:
                suggestions = await self.process_suggestions_sheet(sheets["1.3 Suggestions"], domain)
                if suggestions:
                    success = await self.vectorize_and_store_suggestions(suggestions)
                    results["suggestions"] = len(suggestions)
                    if not success:
                        results["success"] = False

            # Process feedback (not vectorized for now)
            if "1.4 Feedback Prompts" in sheets and not sheets["1.4 Feedback Prompts"].empty:
                feedback = await self.process_feedback_sheet(sheets["1.4 Feedback Prompts"], domain)
                results["feedback"] = len(feedback)

            # Process training examples (not vectorized for now)
            if "1.6 FineTuning Examples" in sheets and not sheets["1.6 FineTuning Examples"].empty:
                training = await self.process_training_sheet(sheets["1.6 FineTuning Examples"], domain)
                results["training"] = len(training)

            logger.info(f"✅ Completed data import for {domain}: {results}")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to import data for {domain}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def import_all_data(self) -> Dict[str, Any]:
        """Import and process all domain data"""
        try:
            logger.info("🔄 Starting import of all mental health data")

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


# Global data import service instance
data_import_service = DataImportService()
