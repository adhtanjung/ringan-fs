#!/usr/bin/env python3
"""
Data Standardizer for Mental Health Data Pipeline

This module implements comprehensive data standardization functions:
- ID format standardization and validation
- Text encoding normalization
- Response type standardization
- Data type conversion and validation
- Field name normalization
- Value range validation

Author: Mental Health Data Pipeline Team
Date: January 2025
"""

import pandas as pd
import numpy as np
import re
import unicodedata
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import hashlib
import uuid
from urllib.parse import quote, unquote
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_standardization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StandardizationType(Enum):
    """Types of standardization operations"""
    ID_FORMAT = "id_format"
    TEXT_ENCODING = "text_encoding"
    RESPONSE_TYPE = "response_type"
    FIELD_NAME = "field_name"
    DATA_TYPE = "data_type"
    VALUE_RANGE = "value_range"
    CATEGORICAL = "categorical"
    NUMERIC = "numeric"

class IDFormat(Enum):
    """Supported ID formats"""
    UUID = "uuid"  # UUID format
    SEQUENTIAL = "sequential"  # Sequential numbers
    PREFIXED = "prefixed"  # Prefix + number (e.g., ANX001)
    HASH = "hash"  # Hash-based IDs
    CUSTOM = "custom"  # Custom format

@dataclass
class StandardizationRule:
    """Configuration for field-specific standardization"""
    field_name: str
    standardization_type: StandardizationType
    target_format: Optional[str] = None
    validation_pattern: Optional[str] = None
    transformation_function: Optional[Callable] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class StandardizationResult:
    """Results of standardization process"""
    total_records: int
    standardized_fields: int
    validation_errors: int
    transformation_errors: int
    warnings: List[str]
    execution_time: float
    quality_score: float
    field_statistics: Dict[str, Any]

class DataStandardizer:
    """
    Comprehensive data standardization system for mental health data.
    
    Features:
    - ID format standardization and validation
    - Text encoding normalization (UTF-8)
    - Response type standardization
    - Field name normalization
    - Data type conversion
    - Value range validation
    - Categorical value mapping
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the DataStandardizer.
        
        Args:
            config_file: Path to configuration file with standardization rules
        """
        self.standardization_rules: Dict[str, StandardizationRule] = {}
        self.field_mappings = self._load_field_mappings()
        self.response_mappings = self._load_response_mappings()
        self.encoding_settings = self._load_encoding_settings()
        
        if config_file:
            self.load_config(config_file)
        
        logger.info("DataStandardizer initialized")
    
    def _load_field_mappings(self) -> Dict[str, str]:
        """Load standard field name mappings."""
        return {
            # ID fields
            'id': 'record_id',
            'identifier': 'record_id',
            'key': 'record_id',
            'uid': 'record_id',
            
            # Anxiety fields
            'anxiety_score': 'anxiety_score',
            'anxiety_level': 'anxiety_level',
            'gad_score': 'gad7_score',
            'gad7': 'gad7_score',
            'worry_score': 'worry_score',
            
            # Stress fields
            'stress_score': 'stress_score',
            'stress_level': 'stress_level',
            'pressure_level': 'stress_level',
            'tension_score': 'stress_score',
            
            # Depression fields
            'depression_score': 'depression_score',
            'depression_level': 'depression_level',
            'phq_score': 'phq9_score',
            'phq9': 'phq9_score',
            'mood_score': 'mood_score',
            
            # General fields
            'timestamp': 'created_at',
            'date': 'created_at',
            'time': 'created_at',
            'response': 'response_text',
            'answer': 'response_text',
            'comment': 'response_text',
            'feedback': 'feedback_text'
        }
    
    def _load_response_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load standard response value mappings."""
        return {
            'anxiety_levels': {
                'none': 'none',
                'no': 'none',
                'minimal': 'mild',
                'low': 'mild',
                'slight': 'mild',
                'mild': 'mild',
                'moderate': 'moderate',
                'medium': 'moderate',
                'severe': 'severe',
                'high': 'severe',
                'extreme': 'severe',
                'very_high': 'severe'
            },
            'stress_levels': {
                'none': 'low',
                'no_stress': 'low',
                'minimal': 'low',
                'low': 'low',
                'medium': 'medium',
                'moderate': 'medium',
                'high': 'high',
                'severe': 'high',
                'extreme': 'high',
                'very_high': 'high'
            },
            'frequency_responses': {
                'never': 'never',
                'no': 'never',
                'rarely': 'rarely',
                'seldom': 'rarely',
                'sometimes': 'sometimes',
                'occasionally': 'sometimes',
                'often': 'often',
                'frequently': 'often',
                'always': 'always',
                'constantly': 'always'
            },
            'boolean_responses': {
                'yes': 'true',
                'y': 'true',
                '1': 'true',
                'true': 'true',
                'no': 'false',
                'n': 'false',
                '0': 'false',
                'false': 'false'
            },
            'severity_levels': {
                'minimal': 'mild',
                'mild': 'mild',
                'moderate': 'moderate',
                'moderately_severe': 'severe',
                'severe': 'severe'
            }
        }
    
    def _load_encoding_settings(self) -> Dict[str, Any]:
        """Load text encoding settings."""
        return {
            'target_encoding': 'utf-8',
            'normalize_unicode': True,
            'remove_control_chars': True,
            'standardize_whitespace': True,
            'lowercase_text': False,  # Preserve case for responses
            'remove_extra_spaces': True
        }
    
    def add_standardization_rule(self, rule: StandardizationRule) -> None:
        """Add a custom standardization rule for a specific field.
        
        Args:
            rule: StandardizationRule configuration
        """
        self.standardization_rules[rule.field_name] = rule
        logger.info(f"Added standardization rule for {rule.field_name}: {rule.standardization_type.value}")
    
    def load_config(self, config_file: str) -> None:
        """Load standardization configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for rule_config in config.get('standardization_rules', []):
                rule = StandardizationRule(
                    field_name=rule_config['field_name'],
                    standardization_type=StandardizationType(rule_config['standardization_type']),
                    target_format=rule_config.get('target_format'),
                    validation_pattern=rule_config.get('validation_pattern'),
                    parameters=rule_config.get('parameters', {})
                )
                self.add_standardization_rule(rule)
            
            logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def standardize_dataframe(self, df: pd.DataFrame, 
                            sheet_name: Optional[str] = None) -> Tuple[pd.DataFrame, StandardizationResult]:
        """Standardize an entire DataFrame.
        
        Args:
            df: Input DataFrame
            sheet_name: Optional sheet name for context
            
        Returns:
            Tuple of (standardized DataFrame, standardization results)
        """
        start_time = datetime.now()
        logger.info(f"Starting data standardization for {sheet_name or 'dataset'}")
        
        # Initialize result tracking
        warnings_list = []
        validation_errors = 0
        transformation_errors = 0
        field_statistics = {}
        
        # Create a copy to work with
        standardized_df = df.copy()
        
        # Step 1: Standardize field names
        standardized_df, field_stats = self._standardize_field_names(standardized_df)
        field_statistics['field_names'] = field_stats
        
        # Step 2: Standardize data types and formats
        for column in standardized_df.columns:
            try:
                original_column = column
                
                # Get or create standardization rule
                if column in self.standardization_rules:
                    rule = self.standardization_rules[column]
                else:
                    rule = self._auto_detect_standardization_rule(standardized_df[column], column)
                
                # Apply standardization
                standardized_df[column], col_stats = self._apply_standardization_rule(
                    standardized_df[column], rule, sheet_name
                )
                
                field_statistics[column] = col_stats
                
                # Track errors
                validation_errors += col_stats.get('validation_errors', 0)
                transformation_errors += col_stats.get('transformation_errors', 0)
                
                if col_stats.get('warnings'):
                    warnings_list.extend(col_stats['warnings'])
                
            except Exception as e:
                logger.error(f"Error standardizing column '{column}': {e}")
                transformation_errors += 1
                warnings_list.append(f"Failed to standardize column '{column}': {str(e)}")
        
        # Step 3: Validate overall data consistency
        consistency_warnings = self._validate_data_consistency(standardized_df)
        warnings_list.extend(consistency_warnings)
        
        # Calculate quality score
        quality_score = self._calculate_standardization_quality_score(
            len(standardized_df), len(standardized_df.columns),
            validation_errors, transformation_errors, len(warnings_list)
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Create result object
        result = StandardizationResult(
            total_records=len(standardized_df),
            standardized_fields=len(standardized_df.columns),
            validation_errors=validation_errors,
            transformation_errors=transformation_errors,
            warnings=warnings_list,
            execution_time=execution_time,
            quality_score=quality_score,
            field_statistics=field_statistics
        )
        
        logger.info(f"Data standardization completed: {len(standardized_df.columns)} fields processed, "
                   f"quality score: {quality_score:.3f}")
        
        return standardized_df, result
    
    def _standardize_field_names(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Standardize field names according to conventions.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (DataFrame with standardized names, statistics)
        """
        original_columns = df.columns.tolist()
        column_mapping = {}
        
        for column in df.columns:
            standardized_name = self._standardize_single_field_name(column)
            column_mapping[column] = standardized_name
        
        # Rename columns
        df_renamed = df.rename(columns=column_mapping)
        
        # Handle duplicate column names
        df_renamed = self._handle_duplicate_column_names(df_renamed)
        
        stats = {
            'original_columns': original_columns,
            'standardized_columns': df_renamed.columns.tolist(),
            'column_mapping': column_mapping,
            'duplicates_resolved': len(original_columns) != len(set(column_mapping.values()))
        }
        
        logger.debug(f"Standardized {len(original_columns)} field names")
        return df_renamed, stats
    
    def _standardize_single_field_name(self, field_name: str) -> str:
        """Standardize a single field name.
        
        Args:
            field_name: Original field name
            
        Returns:
            Standardized field name
        """
        # Convert to lowercase and replace spaces/special chars with underscores
        standardized = re.sub(r'[^a-zA-Z0-9_]', '_', str(field_name).lower())
        
        # Remove multiple consecutive underscores
        standardized = re.sub(r'_+', '_', standardized)
        
        # Remove leading/trailing underscores
        standardized = standardized.strip('_')
        
        # Apply field mappings if available
        if standardized in self.field_mappings:
            standardized = self.field_mappings[standardized]
        
        # Ensure field name is not empty
        if not standardized:
            standardized = 'unnamed_field'
        
        return standardized
    
    def _handle_duplicate_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle duplicate column names by adding suffixes.
        
        Args:
            df: DataFrame with potentially duplicate column names
            
        Returns:
            DataFrame with unique column names
        """
        columns = df.columns.tolist()
        seen = {}
        new_columns = []
        
        for col in columns:
            if col in seen:
                seen[col] += 1
                new_col = f"{col}_{seen[col]}"
            else:
                seen[col] = 0
                new_col = col
            new_columns.append(new_col)
        
        df.columns = new_columns
        return df
    
    def _auto_detect_standardization_rule(self, series: pd.Series, column_name: str) -> StandardizationRule:
        """Automatically detect appropriate standardization rule for a column.
        
        Args:
            series: Pandas Series to analyze
            column_name: Name of the column
            
        Returns:
            Appropriate standardization rule
        """
        column_lower = column_name.lower()
        
        # Detect ID fields
        if any(keyword in column_lower for keyword in ['id', 'key', 'identifier']):
            return StandardizationRule(
                field_name=column_name,
                standardization_type=StandardizationType.ID_FORMAT,
                target_format=IDFormat.SEQUENTIAL.value
            )
        
        # Detect text fields
        if series.dtype == 'object':
            # Check if it's categorical with limited values
            unique_count = series.nunique()
            if unique_count <= 20:  # Likely categorical
                return StandardizationRule(
                    field_name=column_name,
                    standardization_type=StandardizationType.CATEGORICAL
                )
            else:  # Likely text response
                return StandardizationRule(
                    field_name=column_name,
                    standardization_type=StandardizationType.TEXT_ENCODING
                )
        
        # Detect numeric fields
        elif pd.api.types.is_numeric_dtype(series):
            return StandardizationRule(
                field_name=column_name,
                standardization_type=StandardizationType.NUMERIC
            )
        
        # Default to text encoding
        return StandardizationRule(
            field_name=column_name,
            standardization_type=StandardizationType.TEXT_ENCODING
        )
    
    def _apply_standardization_rule(self, series: pd.Series, rule: StandardizationRule, 
                                  sheet_name: Optional[str] = None) -> Tuple[pd.Series, Dict[str, Any]]:
        """Apply a standardization rule to a pandas Series.
        
        Args:
            series: Input series
            rule: Standardization rule to apply
            sheet_name: Optional sheet name for context
            
        Returns:
            Tuple of (standardized series, statistics)
        """
        stats = {
            'original_dtype': str(series.dtype),
            'original_unique_count': series.nunique(),
            'validation_errors': 0,
            'transformation_errors': 0,
            'warnings': []
        }
        
        try:
            if rule.standardization_type == StandardizationType.ID_FORMAT:
                standardized_series = self._standardize_id_format(series, rule)
            
            elif rule.standardization_type == StandardizationType.TEXT_ENCODING:
                standardized_series = self._standardize_text_encoding(series)
            
            elif rule.standardization_type == StandardizationType.CATEGORICAL:
                standardized_series = self._standardize_categorical_values(series, rule.field_name)
            
            elif rule.standardization_type == StandardizationType.NUMERIC:
                standardized_series = self._standardize_numeric_values(series, rule)
            
            elif rule.standardization_type == StandardizationType.RESPONSE_TYPE:
                standardized_series = self._standardize_response_types(series, rule.field_name)
            
            else:
                # Default: just clean the text
                standardized_series = self._standardize_text_encoding(series)
            
            # Update statistics
            stats['final_dtype'] = str(standardized_series.dtype)
            stats['final_unique_count'] = standardized_series.nunique()
            stats['transformation_success'] = True
            
        except Exception as e:
            logger.error(f"Failed to apply standardization rule for {rule.field_name}: {e}")
            standardized_series = series  # Return original on error
            stats['transformation_errors'] += 1
            stats['warnings'].append(f"Standardization failed: {str(e)}")
            stats['transformation_success'] = False
        
        return standardized_series, stats
    
    def _standardize_id_format(self, series: pd.Series, rule: StandardizationRule) -> pd.Series:
        """Standardize ID format.
        
        Args:
            series: Input series with IDs
            rule: Standardization rule
            
        Returns:
            Standardized series
        """
        target_format = rule.target_format or IDFormat.SEQUENTIAL.value
        
        if target_format == IDFormat.UUID.value:
            # Convert to UUID format
            return series.apply(lambda x: str(uuid.uuid4()) if pd.isna(x) else self._to_uuid(x))
        
        elif target_format == IDFormat.SEQUENTIAL.value:
            # Convert to sequential numbers
            return pd.Series(range(1, len(series) + 1), index=series.index)
        
        elif target_format == IDFormat.PREFIXED.value:
            # Convert to prefixed format (e.g., REC001)
            prefix = rule.parameters.get('prefix', 'REC')
            return series.apply(lambda x, i=iter(range(1, len(series) + 1)): 
                              f"{prefix}{next(i):03d}" if not pd.isna(x) else f"{prefix}{next(i):03d}")
        
        elif target_format == IDFormat.HASH.value:
            # Convert to hash-based IDs
            return series.apply(lambda x: self._to_hash_id(x) if not pd.isna(x) else self._to_hash_id(str(uuid.uuid4())))
        
        else:
            # Keep original format but clean it
            return series.astype(str).str.strip()
    
    def _to_uuid(self, value: Any) -> str:
        """Convert value to UUID format."""
        try:
            # If already a valid UUID, return it
            uuid.UUID(str(value))
            return str(value)
        except ValueError:
            # Generate new UUID based on value
            return str(uuid.uuid5(uuid.NAMESPACE_OID, str(value)))
    
    def _to_hash_id(self, value: Any) -> str:
        """Convert value to hash-based ID."""
        hash_object = hashlib.md5(str(value).encode())
        return hash_object.hexdigest()[:12]  # Use first 12 characters
    
    def _standardize_text_encoding(self, series: pd.Series) -> pd.Series:
        """Standardize text encoding and formatting.
        
        Args:
            series: Input series with text data
            
        Returns:
            Standardized series
        """
        def clean_text(text):
            if pd.isna(text):
                return text
            
            text = str(text)
            
            # Normalize Unicode
            if self.encoding_settings['normalize_unicode']:
                text = unicodedata.normalize('NFKC', text)
            
            # Remove control characters
            if self.encoding_settings['remove_control_chars']:
                text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
            
            # Standardize whitespace
            if self.encoding_settings['standardize_whitespace']:
                text = re.sub(r'\s+', ' ', text)
            
            # Remove extra spaces
            if self.encoding_settings['remove_extra_spaces']:
                text = text.strip()
            
            return text
        
        return series.apply(clean_text)
    
    def _standardize_categorical_values(self, series: pd.Series, field_name: str) -> pd.Series:
        """Standardize categorical values.
        
        Args:
            series: Input series with categorical data
            field_name: Name of the field for context
            
        Returns:
            Standardized series
        """
        field_lower = field_name.lower()
        
        # Determine appropriate mapping based on field name
        mapping = None
        if any(keyword in field_lower for keyword in ['anxiety', 'worry']):
            mapping = self.response_mappings['anxiety_levels']
        elif any(keyword in field_lower for keyword in ['stress', 'pressure']):
            mapping = self.response_mappings['stress_levels']
        elif any(keyword in field_lower for keyword in ['frequency', 'often', 'how_much']):
            mapping = self.response_mappings['frequency_responses']
        elif any(keyword in field_lower for keyword in ['boolean', 'yes_no', 'true_false']):
            mapping = self.response_mappings['boolean_responses']
        elif any(keyword in field_lower for keyword in ['severity', 'level']):
            mapping = self.response_mappings['severity_levels']
        
        if mapping:
            def standardize_value(value):
                if pd.isna(value):
                    return value
                value_str = str(value).lower().strip()
                return mapping.get(value_str, value)
            
            return series.apply(standardize_value)
        else:
            # Generic categorical standardization
            return series.astype(str).str.lower().str.strip()
    
    def _standardize_numeric_values(self, series: pd.Series, rule: StandardizationRule) -> pd.Series:
        """Standardize numeric values.
        
        Args:
            series: Input series with numeric data
            rule: Standardization rule
            
        Returns:
            Standardized series
        """
        # Convert to numeric if not already
        if not pd.api.types.is_numeric_dtype(series):
            series = pd.to_numeric(series, errors='coerce')
        
        # Apply value range validation if specified
        if 'min_value' in rule.parameters or 'max_value' in rule.parameters:
            min_val = rule.parameters.get('min_value', float('-inf'))
            max_val = rule.parameters.get('max_value', float('inf'))
            
            # Clip values to range
            series = series.clip(lower=min_val, upper=max_val)
        
        # Round to specified decimal places
        if 'decimal_places' in rule.parameters:
            decimal_places = rule.parameters['decimal_places']
            series = series.round(decimal_places)
        
        return series
    
    def _standardize_response_types(self, series: pd.Series, field_name: str) -> pd.Series:
        """Standardize response types based on field context.
        
        Args:
            series: Input series with response data
            field_name: Name of the field for context
            
        Returns:
            Standardized series
        """
        # This is similar to categorical standardization but more specific to responses
        return self._standardize_categorical_values(series, field_name)
    
    def _validate_data_consistency(self, df: pd.DataFrame) -> List[str]:
        """Validate overall data consistency.
        
        Args:
            df: Standardized DataFrame
            
        Returns:
            List of consistency warnings
        """
        warnings = []
        
        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            warnings.append("Duplicate column names detected after standardization")
        
        # Check for completely empty columns
        empty_columns = [col for col in df.columns if df[col].isna().all()]
        if empty_columns:
            warnings.append(f"Completely empty columns: {empty_columns}")
        
        # Check for columns with only one unique value
        single_value_columns = [col for col in df.columns 
                              if df[col].nunique() == 1 and not df[col].isna().all()]
        if single_value_columns:
            warnings.append(f"Columns with single unique value: {single_value_columns}")
        
        return warnings
    
    def _calculate_standardization_quality_score(self, total_records: int, total_fields: int,
                                               validation_errors: int, transformation_errors: int,
                                               warning_count: int) -> float:
        """Calculate quality score for standardization process.
        
        Args:
            total_records: Total number of records
            total_fields: Total number of fields
            validation_errors: Number of validation errors
            transformation_errors: Number of transformation errors
            warning_count: Number of warnings
            
        Returns:
            Quality score between 0 and 1
        """
        if total_records == 0 or total_fields == 0:
            return 0.0
        
        total_operations = total_records * total_fields
        total_errors = validation_errors + transformation_errors
        
        # Calculate error rate
        error_rate = total_errors / total_operations if total_operations > 0 else 0
        
        # Calculate warning penalty
        warning_penalty = min(warning_count * 0.01, 0.2)  # Max 20% penalty for warnings
        
        # Calculate quality score
        quality_score = max(0.0, 1.0 - error_rate - warning_penalty)
        
        return quality_score
    
    def generate_standardization_report(self, results: List[StandardizationResult],
                                      output_file: str = "standardization_report.json") -> None:
        """Generate a comprehensive standardization report.
        
        Args:
            results: List of standardization results
            output_file: Output file path
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_datasets': len(results),
                'total_records': sum(r.total_records for r in results),
                'total_fields': sum(r.standardized_fields for r in results),
                'total_validation_errors': sum(r.validation_errors for r in results),
                'total_transformation_errors': sum(r.transformation_errors for r in results),
                'average_quality_score': sum(r.quality_score for r in results) / len(results) if results else 0,
                'total_execution_time': sum(r.execution_time for r in results)
            },
            'detailed_results': [asdict(result) for result in results],
            'recommendations': self._generate_standardization_recommendations(results)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Standardization report saved to {output_file}")
    
    def _generate_standardization_recommendations(self, results: List[StandardizationResult]) -> List[str]:
        """Generate recommendations based on standardization results."""
        recommendations = []
        
        avg_quality = sum(r.quality_score for r in results) / len(results) if results else 0
        total_errors = sum(r.validation_errors + r.transformation_errors for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        
        if avg_quality < 0.8:
            recommendations.append("Consider reviewing standardization rules - average quality score is below 0.8")
        
        if total_errors > 0:
            recommendations.append(f"Address {total_errors} validation and transformation errors")
        
        if total_warnings > 10:
            recommendations.append(f"Review {total_warnings} warnings from standardization process")
        
        return recommendations

def main():
    """Main function for testing the DataStandardizer."""
    print("=" * 60)
    print("Mental Health Data Pipeline - Data Standardizer")
    print("=" * 60)
    
    try:
        # Initialize standardizer
        standardizer = DataStandardizer()
        
        # Example: Create sample data with various formats
        print("\nTesting data standardization...")
        
        sample_data = {
            'ID': ['1', '2', '3', '4', '5'],
            'Anxiety Score': [1, 2, None, 4, 5],
            'Stress Level': ['LOW', 'High', 'MEDIUM', None, 'extreme'],
            'Response Text': ['  feeling anxious  ', 'STRESSED ABOUT WORK', None, 'doing well', 'need help!!!'],
            'Frequency': ['never', 'ALWAYS', 'sometimes', 'often', None]
        }
        
        df = pd.DataFrame(sample_data)
        print(f"\nOriginal data shape: {df.shape}")
        print("Original data:")
        print(df)
        
        # Standardize data
        standardized_df, result = standardizer.standardize_dataframe(df, "sample_sheet")
        
        print(f"\nStandardized data shape: {standardized_df.shape}")
        print("Standardized data:")
        print(standardized_df)
        print(f"\nQuality score: {result.quality_score:.3f}")
        print(f"Validation errors: {result.validation_errors}")
        print(f"Transformation errors: {result.transformation_errors}")
        
        if result.warnings:
            print(f"Warnings: {result.warnings}")
        
        # Generate report
        standardizer.generate_standardization_report([result], "sample_standardization_report.json")
        print("\nStandardization report generated: sample_standardization_report.json")
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        print(f"Testing failed: {e}")

if __name__ == "__main__":
    main()