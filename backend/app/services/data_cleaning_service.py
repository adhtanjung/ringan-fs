"""
Data Cleaning Service for Excel Mental Health Data
Handles format inconsistencies and data transformation
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)


class DataCleaningService:
    """Service for cleaning and transforming Excel mental health data"""

    def __init__(self):
        # Response type mapping
        self.response_type_mapping = {
            'scale (0–4)': 'scale',
            'scale (0-4)': 'scale',
            'scale (1–5)': 'scale',
            'scale (1-5)': 'scale',
            'scale (0–10)': 'scale',
            'scale (0-10)': 'scale',
            'Likert scale (1–5)': 'scale',
            'Likert scale (1-5)': 'scale',
            'scale_1_5': 'scale',
            'yes/no': 'multiple_choice',
            'yes_no': 'multiple_choice',
            'yes/no + text': 'multiple_choice',
            'Open text': 'text',
            'open_text': 'text',
            'multi_choice': 'multiple_choice',
            'date': 'text',
            'text': 'text',
            'scale': 'scale'
        }

        # Stage mapping
        self.stage_mapping = {
            'post_suggestion': 'post_suggestion',
            'ongoing': 'ongoing',
            'post-suggestion': 'post_suggestion',
            'post_suggestion ': 'post_suggestion',
            'ongoing ': 'ongoing'
        }

        # Next action mapping - extract standardized actions from complex text
        self.next_action_patterns = {
            r'continue_same': 'continue_same',
            r'show_problem_menu': 'show_problem_menu',
            r'end_session': 'end_session',
            r'escalate': 'escalate',
            r'schedule_followup': 'schedule_followup',
            r'\[yes\].*continue.*same': 'continue_same',
            r'\[no\].*continue.*same': 'continue_same',
            r'\[yes\].*show.*problem.*menu': 'show_problem_menu',
            r'\[no\].*show.*problem.*menu': 'show_problem_menu',
            r'\[yes\].*end.*session': 'end_session',
            r'\[no\].*end.*session': 'end_session',
            r'end.*session': 'end_session',
            r'continue.*coaching': 'continue_same',
            r'offer.*different.*resources': 'show_problem_menu',
            r'offer.*more.*same.*resources': 'continue_same'
        }

    def clean_dataframe(self, df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """Clean a dataframe based on sheet type"""
        if df.empty:
            return df

        # Remove completely empty rows
        df = df.dropna(how='all')

        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')

        # Clean based on sheet type
        if '1.2 Self Assessment' in sheet_name:
            df = self._clean_assessment_sheet(df)
        elif '1.4 Feedback Prompts' in sheet_name:
            df = self._clean_feedback_sheet(df)
        elif '1.6 FineTuning Examples' in sheet_name:
            df = self._clean_training_sheet(df)
        else:
            df = self._clean_general_sheet(df)

        return df

    def _clean_assessment_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean assessment questions sheet"""
        if df.empty:
            return df

        # Remove rows with missing essential data
        essential_cols = ['question_id', 'question_text']
        df = df.dropna(subset=essential_cols, how='any')

        # Clean response_type column - handle question IDs that got mixed up
        if 'response_type' in df.columns:
            df['response_type'] = df['response_type'].apply(self._clean_response_type)

                    # Fix question IDs that got into response_type column
        mask = df['response_type'].str.startswith('Q', na=False) & df['response_type'].str.len() <= 5
        if mask.any():
            # Move these to question_id if question_id is empty
            for idx in df[mask].index:
                if pd.isna(df.at[idx, 'question_id']) or df.at[idx, 'question_id'] == '':
                    df.at[idx, 'question_id'] = df.at[idx, 'response_type']
                    df.at[idx, 'response_type'] = 'text'  # Default to text

        # Clean sub_category_id
        if 'sub_category_id' in df.columns:
            df['sub_category_id'] = df['sub_category_id'].fillna('unknown')

        # Clean batch_id
        if 'batch_id' in df.columns:
            df['batch_id'] = df['batch_id'].fillna('batch_1')

        # Clean clusters
        if 'clusters' in df.columns:
            df['clusters'] = df['clusters'].fillna('general')

        return df

    def _clean_feedback_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean feedback prompts sheet"""
        if df.empty:
            return df

        # Remove rows with missing essential data
        essential_cols = ['prompt_text']
        df = df.dropna(subset=essential_cols, how='any')

        # Clean stage column
        if 'stage' in df.columns:
            df['stage'] = df['stage'].apply(self._clean_stage)

        # Clean next_action column
        if 'next_action' in df.columns:
            df['next_action'] = df['next_action'].apply(self._clean_next_action)

        # Clean prompt_id
        if 'prompt_id' in df.columns:
            # Fill NaN values with generated prompt IDs
            mask = df['prompt_id'].isna()
            df.loc[mask, 'prompt_id'] = [f'prompt_{i}' for i in df[mask].index]

        return df

    def _clean_training_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean training examples sheet"""
        if df.empty:
            return df

        # Check if required columns exist, if not, create them with default values
        if 'prompt' not in df.columns:
            df['prompt'] = ''
        if 'completion' not in df.columns:
            df['completion'] = ''

        # Remove rows with missing essential data (only if both are empty)
        df = df.dropna(subset=['prompt', 'completion'], how='all')

        # Clean id column
        if 'id' in df.columns:
            # Fill NaN values with generated train IDs
            mask = df['id'].isna()
            df.loc[mask, 'id'] = [f'train_{i}' for i in df[mask].index]

        # Clean problem column
        if 'problem' in df.columns:
            df['problem'] = df['problem'].fillna('general')

        # Clean ConversationID column
        if 'ConversationID' in df.columns:
            # Fill NaN values with generated conversation IDs
            mask = df['ConversationID'].isna()
            df.loc[mask, 'ConversationID'] = [f'conv_{i}' for i in df[mask].index]

        return df

    def _clean_general_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean general sheets"""
        if df.empty:
            return df

        # Remove rows where all important columns are empty
        important_cols = [col for col in df.columns if not col.startswith('Unnamed')]
        if important_cols:
            df = df.dropna(subset=important_cols, how='all')

        return df

    def _clean_response_type(self, value: Any) -> str:
        """Clean and standardize response_type values"""
        if pd.isna(value) or value == '':
            return 'text'

        value_str = str(value).strip().lower()

        # Check direct mapping
        if value_str in self.response_type_mapping:
            return self.response_type_mapping[value_str]

        # Check partial matches
        for pattern, mapped_value in self.response_type_mapping.items():
            if pattern.lower() in value_str:
                return mapped_value

        # Default to text for unknown values
        logger.warning(f"Unknown response_type: '{value}', defaulting to 'text'")
        return 'text'

    def _clean_stage(self, value: Any) -> str:
        """Clean and standardize stage values"""
        if pd.isna(value) or value == '':
            return 'post_suggestion'

        value_str = str(value).strip().lower()

        # Check direct mapping
        if value_str in self.stage_mapping:
            return self.stage_mapping[value_str]

        # Default to post_suggestion for unknown values
        logger.warning(f"Unknown stage: '{value}', defaulting to 'post_suggestion'")
        return 'post_suggestion'

    def _clean_next_action(self, value: Any) -> str:
        """Clean and standardize next_action values"""
        if pd.isna(value) or value == '':
            return 'continue_same'

        value_str = str(value).strip().lower()

        # Check for exact matches first
        if value_str in ['continue_same', 'show_problem_menu', 'end_session', 'escalate', 'schedule_followup']:
            return value_str

        # Check pattern matches
        for pattern, action in self.next_action_patterns.items():
            if re.search(pattern, value_str, re.IGNORECASE):
                return action

        # Default to continue_same for unknown values
        logger.warning(f"Unknown next_action: '{value}', defaulting to 'continue_same'")
        return 'continue_same'

    def validate_cleaned_data(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Validate cleaned data and return statistics"""
        if df.empty:
            # Allow empty sheets for certain types
            if '1.4 Feedback Prompts' in sheet_name or '1.6 FineTuning Examples' in sheet_name:
                return {
                    "valid": True,
                    "rows": 0,
                    "columns": 0,
                    "errors": ["Empty sheet - this is acceptable for this sheet type"]
                }
            else:
                return {
                    "valid": False,
                    "rows": 0,
                    "errors": ["Empty dataframe"]
                }

        stats = {
            "valid": True,
            "rows": len(df),
            "columns": len(df.columns),
            "errors": []
        }

        # Check for required columns based on sheet type
        if '1.2 Self Assessment' in sheet_name:
            required_cols = ['question_id', 'question_text', 'response_type']
            for col in required_cols:
                if col not in df.columns:
                    stats["errors"].append(f"Missing required column: {col}")
                    stats["valid"] = False

        elif '1.4 Feedback Prompts' in sheet_name:
            # Only require prompt_text for feedback prompts
            required_cols = ['prompt_text']
            for col in required_cols:
                if col not in df.columns:
                    stats["errors"].append(f"Missing required column: {col}")
                    stats["valid"] = False

        elif '1.6 FineTuning Examples' in sheet_name:
            # For training examples, we'll create missing columns with defaults
            # Only validate if we have some data
            if len(df) > 0:
                # Check if we have any meaningful data
                has_data = False
                for col in df.columns:
                    if not col.startswith('Unnamed') and df[col].notna().sum() > 0:
                        has_data = True
                        break

                if not has_data:
                    stats["errors"].append("No meaningful data found in training examples sheet")
                    stats["valid"] = False

        # Check for empty values in required columns (but be lenient)
        if stats["valid"]:
            for col in df.columns:
                empty_count = df[col].isna().sum()
                if empty_count > 0 and empty_count < len(df):  # Only warn if not all values are empty
                    stats["errors"].append(f"Column '{col}' has {empty_count} empty values")

        return stats


# Global instance
data_cleaning_service = DataCleaningService()
