#!/usr/bin/env python3
"""
Null Value Handler for Mental Health Data Pipeline

This module implements context-aware null value handling strategies:
- Intelligent imputation based on data context
- Domain-specific handling for mental health data
- Statistical and ML-based imputation methods
- Validation and quality assessment
- Configurable strategies per field type

Author: Mental Health Data Pipeline Team
Date: January 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import LabelEncoder
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('null_handling.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImputationStrategy(Enum):
    """Available imputation strategies"""
    SKIP = "skip"  # Skip records with null values
    DROP_COLUMN = "drop_column"  # Remove columns with high null percentage
    MEAN = "mean"  # Use mean for numerical data
    MEDIAN = "median"  # Use median for numerical data
    MODE = "mode"  # Use mode for categorical data
    FORWARD_FILL = "forward_fill"  # Use previous value
    BACKWARD_FILL = "backward_fill"  # Use next value
    INTERPOLATE = "interpolate"  # Linear interpolation
    KNN = "knn"  # K-Nearest Neighbors imputation
    ITERATIVE = "iterative"  # Iterative imputation (MICE)
    DOMAIN_SPECIFIC = "domain_specific"  # Mental health domain rules
    CUSTOM = "custom"  # Custom function

class FieldType(Enum):
    """Field types for context-aware handling"""
    NUMERIC_SCORE = "numeric_score"  # Numerical scores (1-10, etc.)
    CATEGORICAL = "categorical"  # Categories (anxiety levels, etc.)
    TEXT_RESPONSE = "text_response"  # Free text responses
    BOOLEAN = "boolean"  # Yes/No, True/False
    DATETIME = "datetime"  # Date/time fields
    ID_FIELD = "id_field"  # Identifier fields
    LIKERT_SCALE = "likert_scale"  # Likert scale responses
    MULTIPLE_CHOICE = "multiple_choice"  # Multiple choice answers

@dataclass
class ImputationRule:
    """Configuration for field-specific imputation"""
    field_name: str
    field_type: FieldType
    strategy: ImputationStrategy
    threshold: float = 0.5  # Max null percentage before dropping
    custom_function: Optional[Callable] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class ImputationResult:
    """Results of imputation process"""
    original_nulls: int
    imputed_values: int
    dropped_records: int
    dropped_columns: List[str]
    strategy_used: str
    quality_score: float
    execution_time: float
    warnings: List[str]

class NullValueHandler:
    """
    Context-aware null value handler for mental health data.
    
    Features:
    - Domain-specific imputation strategies
    - Statistical and ML-based methods
    - Configurable rules per field type
    - Quality assessment and validation
    - Comprehensive logging and reporting
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the NullValueHandler.
        
        Args:
            config_file: Path to configuration file with imputation rules
        """
        self.imputation_rules: Dict[str, ImputationRule] = {}
        self.default_strategies = self._get_default_strategies()
        self.domain_knowledge = self._load_domain_knowledge()
        
        if config_file:
            self.load_config(config_file)
        
        logger.info("NullValueHandler initialized")
    
    def _get_default_strategies(self) -> Dict[FieldType, ImputationStrategy]:
        """Get default imputation strategies for each field type."""
        return {
            FieldType.NUMERIC_SCORE: ImputationStrategy.MEDIAN,
            FieldType.CATEGORICAL: ImputationStrategy.MODE,
            FieldType.TEXT_RESPONSE: ImputationStrategy.DOMAIN_SPECIFIC,
            FieldType.BOOLEAN: ImputationStrategy.MODE,
            FieldType.DATETIME: ImputationStrategy.INTERPOLATE,
            FieldType.ID_FIELD: ImputationStrategy.SKIP,
            FieldType.LIKERT_SCALE: ImputationStrategy.MEDIAN,
            FieldType.MULTIPLE_CHOICE: ImputationStrategy.MODE
        }
    
    def _load_domain_knowledge(self) -> Dict[str, Any]:
        """Load mental health domain-specific knowledge."""
        return {
            'anxiety_levels': ['none', 'mild', 'moderate', 'severe', 'extreme'],
            'stress_levels': ['low', 'medium', 'high', 'very_high'],
            'mood_states': ['very_poor', 'poor', 'fair', 'good', 'excellent'],
            'frequency_terms': ['never', 'rarely', 'sometimes', 'often', 'always'],
            'severity_scales': {
                'gad7': {'min': 0, 'max': 21, 'mild': 5, 'moderate': 10, 'severe': 15},
                'phq9': {'min': 0, 'max': 27, 'mild': 5, 'moderate': 10, 'severe': 15},
                'dass21': {'min': 0, 'max': 63, 'mild': 7, 'moderate': 14, 'severe': 21}
            },
            'common_responses': {
                'coping_strategies': ['exercise', 'meditation', 'therapy', 'medication', 'social_support'],
                'triggers': ['work_stress', 'relationships', 'health', 'finances', 'family']
            }
        }
    
    def add_imputation_rule(self, rule: ImputationRule) -> None:
        """Add a custom imputation rule for a specific field.
        
        Args:
            rule: ImputationRule configuration
        """
        self.imputation_rules[rule.field_name] = rule
        logger.info(f"Added imputation rule for {rule.field_name}: {rule.strategy.value}")
    
    def load_config(self, config_file: str) -> None:
        """Load imputation configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for field_config in config.get('imputation_rules', []):
                rule = ImputationRule(
                    field_name=field_config['field_name'],
                    field_type=FieldType(field_config['field_type']),
                    strategy=ImputationStrategy(field_config['strategy']),
                    threshold=field_config.get('threshold', 0.5),
                    parameters=field_config.get('parameters', {})
                )
                self.add_imputation_rule(rule)
            
            logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def analyze_null_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze null value patterns in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Analysis results
        """
        analysis = {
            'total_records': len(df),
            'total_fields': len(df.columns),
            'null_summary': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Analyze each column
        for column in df.columns:
            null_count = df[column].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            
            analysis['null_summary'][column] = {
                'null_count': int(null_count),
                'null_percentage': round(null_percentage, 2),
                'data_type': str(df[column].dtype),
                'unique_values': int(df[column].nunique()),
                'sample_values': df[column].dropna().head(3).tolist()
            }
        
        # Identify patterns
        high_null_columns = [col for col, info in analysis['null_summary'].items() 
                           if info['null_percentage'] > 50]
        
        analysis['patterns'] = {
            'high_null_columns': high_null_columns,
            'completely_null_columns': [col for col in df.columns if df[col].isnull().all()],
            'no_null_columns': [col for col in df.columns if not df[col].isnull().any()]
        }
        
        # Generate recommendations
        for column, info in analysis['null_summary'].items():
            if info['null_percentage'] > 80:
                analysis['recommendations'].append(f"Consider dropping column '{column}' (>{info['null_percentage']:.1f}% null)")
            elif info['null_percentage'] > 50:
                analysis['recommendations'].append(f"High null percentage in '{column}' ({info['null_percentage']:.1f}%) - review imputation strategy")
        
        return analysis
    
    def detect_field_type(self, series: pd.Series, column_name: str) -> FieldType:
        """Automatically detect field type based on data characteristics.
        
        Args:
            series: Pandas Series to analyze
            column_name: Name of the column
            
        Returns:
            Detected field type
        """
        column_lower = column_name.lower()
        
        # Check for ID fields
        if any(keyword in column_lower for keyword in ['id', 'key', 'identifier']):
            return FieldType.ID_FIELD
        
        # Check for datetime
        if 'date' in column_lower or 'time' in column_lower:
            return FieldType.DATETIME
        
        # Analyze non-null values
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return FieldType.CATEGORICAL  # Default for empty series
        
        # Check if numeric
        if pd.api.types.is_numeric_dtype(series):
            unique_values = non_null_series.nunique()
            value_range = non_null_series.max() - non_null_series.min() if unique_values > 1 else 0
            
            # Check for Likert scale (typically 1-5, 1-7, 1-10)
            if unique_values <= 10 and value_range <= 10:
                return FieldType.LIKERT_SCALE
            else:
                return FieldType.NUMERIC_SCORE
        
        # Check for boolean
        unique_values = set(str(v).lower() for v in non_null_series.unique())
        boolean_values = {'true', 'false', 'yes', 'no', '1', '0', 'y', 'n'}
        if unique_values.issubset(boolean_values):
            return FieldType.BOOLEAN
        
        # Check for text responses (longer strings)
        if series.dtype == 'object':
            avg_length = non_null_series.astype(str).str.len().mean()
            if avg_length > 50:  # Arbitrary threshold for text responses
                return FieldType.TEXT_RESPONSE
            elif non_null_series.nunique() <= 20:  # Limited unique values
                return FieldType.CATEGORICAL
            else:
                return FieldType.MULTIPLE_CHOICE
        
        return FieldType.CATEGORICAL  # Default fallback
    
    def handle_nulls(self, df: pd.DataFrame, 
                    sheet_name: Optional[str] = None) -> tuple[pd.DataFrame, ImputationResult]:
        """Handle null values in the DataFrame using configured strategies.
        
        Args:
            df: Input DataFrame
            sheet_name: Optional sheet name for context
            
        Returns:
            Tuple of (processed DataFrame, imputation results)
        """
        start_time = datetime.now()
        logger.info(f"Starting null value handling for {sheet_name or 'dataset'}")
        
        # Initialize result tracking
        original_nulls = df.isnull().sum().sum()
        dropped_records = 0
        dropped_columns = []
        warnings_list = []
        
        # Create a copy to work with
        processed_df = df.copy()
        
        # Analyze null patterns first
        null_analysis = self.analyze_null_patterns(processed_df)
        
        # Process each column
        for column in processed_df.columns:
            try:
                null_percentage = (processed_df[column].isnull().sum() / len(processed_df)) * 100
                
                # Get imputation rule for this column
                if column in self.imputation_rules:
                    rule = self.imputation_rules[column]
                else:
                    # Auto-detect field type and use default strategy
                    field_type = self.detect_field_type(processed_df[column], column)
                    strategy = self.default_strategies[field_type]
                    rule = ImputationRule(
                        field_name=column,
                        field_type=field_type,
                        strategy=strategy
                    )
                
                # Check if column should be dropped
                if null_percentage > (rule.threshold * 100):
                    if rule.strategy != ImputationStrategy.DROP_COLUMN:
                        warnings_list.append(f"Column '{column}' has {null_percentage:.1f}% nulls, exceeding threshold")
                    
                    if null_percentage > 80:  # Always drop if >80% null
                        processed_df = processed_df.drop(columns=[column])
                        dropped_columns.append(column)
                        logger.info(f"Dropped column '{column}' ({null_percentage:.1f}% null)")
                        continue
                
                # Apply imputation strategy
                processed_df = self._apply_imputation_strategy(
                    processed_df, column, rule, sheet_name
                )
                
            except Exception as e:
                logger.error(f"Error processing column '{column}': {e}")
                warnings_list.append(f"Failed to process column '{column}': {str(e)}")
        
        # Calculate final statistics
        final_nulls = processed_df.isnull().sum().sum()
        imputed_values = original_nulls - final_nulls - sum(
            df[col].isnull().sum() for col in dropped_columns
        )
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            original_nulls, final_nulls, len(dropped_columns), len(df.columns)
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Create result object
        result = ImputationResult(
            original_nulls=int(original_nulls),
            imputed_values=int(imputed_values),
            dropped_records=dropped_records,
            dropped_columns=dropped_columns,
            strategy_used="mixed",
            quality_score=quality_score,
            execution_time=execution_time,
            warnings=warnings_list
        )
        
        logger.info(f"Null handling completed: {imputed_values} values imputed, "
                   f"{len(dropped_columns)} columns dropped, quality score: {quality_score:.3f}")
        
        return processed_df, result
    
    def _apply_imputation_strategy(self, df: pd.DataFrame, column: str, 
                                 rule: ImputationRule, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Apply specific imputation strategy to a column.
        
        Args:
            df: DataFrame to process
            column: Column name to process
            rule: Imputation rule to apply
            sheet_name: Optional sheet name for context
            
        Returns:
            Processed DataFrame
        """
        if df[column].isnull().sum() == 0:
            return df  # No nulls to handle
        
        strategy = rule.strategy
        logger.debug(f"Applying {strategy.value} to column '{column}'")
        
        try:
            if strategy == ImputationStrategy.SKIP:
                # Remove rows with null values in this column
                df = df.dropna(subset=[column])
            
            elif strategy == ImputationStrategy.DROP_COLUMN:
                df = df.drop(columns=[column])
            
            elif strategy == ImputationStrategy.MEAN:
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].mean())
                else:
                    logger.warning(f"Cannot apply mean to non-numeric column '{column}', using mode instead")
                    df[column] = df[column].fillna(df[column].mode().iloc[0] if not df[column].mode().empty else 'unknown')
            
            elif strategy == ImputationStrategy.MEDIAN:
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].median())
                else:
                    logger.warning(f"Cannot apply median to non-numeric column '{column}', using mode instead")
                    df[column] = df[column].fillna(df[column].mode().iloc[0] if not df[column].mode().empty else 'unknown')
            
            elif strategy == ImputationStrategy.MODE:
                mode_value = df[column].mode()
                if not mode_value.empty:
                    df[column] = df[column].fillna(mode_value.iloc[0])
                else:
                    df[column] = df[column].fillna('unknown')
            
            elif strategy == ImputationStrategy.FORWARD_FILL:
                df[column] = df[column].fillna(method='ffill')
            
            elif strategy == ImputationStrategy.BACKWARD_FILL:
                df[column] = df[column].fillna(method='bfill')
            
            elif strategy == ImputationStrategy.INTERPOLATE:
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].interpolate()
                else:
                    # For non-numeric, use forward fill as fallback
                    df[column] = df[column].fillna(method='ffill')
            
            elif strategy == ImputationStrategy.KNN:
                df = self._apply_knn_imputation(df, column, rule.parameters)
            
            elif strategy == ImputationStrategy.ITERATIVE:
                df = self._apply_iterative_imputation(df, column, rule.parameters)
            
            elif strategy == ImputationStrategy.DOMAIN_SPECIFIC:
                df = self._apply_domain_specific_imputation(df, column, rule, sheet_name)
            
            elif strategy == ImputationStrategy.CUSTOM:
                if rule.custom_function:
                    df[column] = rule.custom_function(df[column])
                else:
                    logger.warning(f"No custom function provided for column '{column}', using mode instead")
                    mode_value = df[column].mode()
                    df[column] = df[column].fillna(mode_value.iloc[0] if not mode_value.empty else 'unknown')
        
        except Exception as e:
            logger.error(f"Failed to apply {strategy.value} to column '{column}': {e}")
            # Fallback to mode imputation
            mode_value = df[column].mode()
            df[column] = df[column].fillna(mode_value.iloc[0] if not mode_value.empty else 'unknown')
        
        return df
    
    def _apply_knn_imputation(self, df: pd.DataFrame, column: str, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Apply KNN imputation to a column."""
        try:
            n_neighbors = parameters.get('n_neighbors', 5)
            
            # Select numeric columns for KNN
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            if column not in numeric_columns:
                logger.warning(f"KNN imputation requires numeric data, column '{column}' is not numeric")
                return df
            
            # Apply KNN imputation
            imputer = KNNImputer(n_neighbors=n_neighbors)
            df[numeric_columns] = imputer.fit_transform(df[numeric_columns])
            
        except Exception as e:
            logger.error(f"KNN imputation failed for column '{column}': {e}")
        
        return df
    
    def _apply_iterative_imputation(self, df: pd.DataFrame, column: str, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Apply iterative (MICE) imputation to a column."""
        try:
            max_iter = parameters.get('max_iter', 10)
            random_state = parameters.get('random_state', 42)
            
            # Select numeric columns for iterative imputation
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            if column not in numeric_columns:
                logger.warning(f"Iterative imputation requires numeric data, column '{column}' is not numeric")
                return df
            
            # Apply iterative imputation
            imputer = IterativeImputer(max_iter=max_iter, random_state=random_state)
            df[numeric_columns] = imputer.fit_transform(df[numeric_columns])
            
        except Exception as e:
            logger.error(f"Iterative imputation failed for column '{column}': {e}")
        
        return df
    
    def _apply_domain_specific_imputation(self, df: pd.DataFrame, column: str, 
                                        rule: ImputationRule, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Apply domain-specific imputation based on mental health context."""
        column_lower = column.lower()
        
        try:
            # Handle anxiety-related fields
            if any(keyword in column_lower for keyword in ['anxiety', 'gad', 'worry']):
                df = self._impute_anxiety_field(df, column)
            
            # Handle stress-related fields
            elif any(keyword in column_lower for keyword in ['stress', 'pressure', 'tension']):
                df = self._impute_stress_field(df, column)
            
            # Handle mood-related fields
            elif any(keyword in column_lower for keyword in ['mood', 'feeling', 'emotion']):
                df = self._impute_mood_field(df, column)
            
            # Handle severity scores
            elif any(keyword in column_lower for keyword in ['score', 'severity', 'level']):
                df = self._impute_severity_score(df, column, sheet_name)
            
            # Handle frequency fields
            elif any(keyword in column_lower for keyword in ['frequency', 'often', 'how_much']):
                df = self._impute_frequency_field(df, column)
            
            # Handle text responses
            elif rule.field_type == FieldType.TEXT_RESPONSE:
                df = self._impute_text_response(df, column)
            
            else:
                # Default to mode for categorical or median for numeric
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].median())
                else:
                    mode_value = df[column].mode()
                    df[column] = df[column].fillna(mode_value.iloc[0] if not mode_value.empty else 'not_specified')
        
        except Exception as e:
            logger.error(f"Domain-specific imputation failed for column '{column}': {e}")
            # Fallback to simple imputation
            if pd.api.types.is_numeric_dtype(df[column]):
                df[column] = df[column].fillna(df[column].median())
            else:
                mode_value = df[column].mode()
                df[column] = df[column].fillna(mode_value.iloc[0] if not mode_value.empty else 'unknown')
        
        return df
    
    def _impute_anxiety_field(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Impute anxiety-related fields with domain knowledge."""
        if pd.api.types.is_numeric_dtype(df[column]):
            # For numeric anxiety scores, use median
            median_value = df[column].median()
            df[column] = df[column].fillna(median_value)
        else:
            # For categorical anxiety levels, use 'moderate' as default
            mode_value = df[column].mode()
            default_value = mode_value.iloc[0] if not mode_value.empty else 'moderate'
            df[column] = df[column].fillna(default_value)
        
        return df
    
    def _impute_stress_field(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Impute stress-related fields with domain knowledge."""
        if pd.api.types.is_numeric_dtype(df[column]):
            # For numeric stress scores, use median
            median_value = df[column].median()
            df[column] = df[column].fillna(median_value)
        else:
            # For categorical stress levels, use 'medium' as default
            mode_value = df[column].mode()
            default_value = mode_value.iloc[0] if not mode_value.empty else 'medium'
            df[column] = df[column].fillna(default_value)
        
        return df
    
    def _impute_mood_field(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Impute mood-related fields with domain knowledge."""
        if pd.api.types.is_numeric_dtype(df[column]):
            # For numeric mood scores, use median
            median_value = df[column].median()
            df[column] = df[column].fillna(median_value)
        else:
            # For categorical mood states, use 'fair' as default
            mode_value = df[column].mode()
            default_value = mode_value.iloc[0] if not mode_value.empty else 'fair'
            df[column] = df[column].fillna(default_value)
        
        return df
    
    def _impute_severity_score(self, df: pd.DataFrame, column: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Impute severity scores based on known scales."""
        if not pd.api.types.is_numeric_dtype(df[column]):
            return df
        
        # Try to identify the scale based on sheet name or column name
        column_lower = column.lower()
        sheet_lower = (sheet_name or '').lower()
        
        # Determine appropriate median based on scale
        if 'gad' in column_lower or 'gad' in sheet_lower:
            # GAD-7 scale (0-21), use mild threshold as default
            default_value = 5
        elif 'phq' in column_lower or 'phq' in sheet_lower:
            # PHQ-9 scale (0-27), use mild threshold as default
            default_value = 5
        elif 'dass' in column_lower or 'dass' in sheet_lower:
            # DASS-21 scale (0-63), use mild threshold as default
            default_value = 7
        else:
            # Use actual median from data
            default_value = df[column].median()
        
        df[column] = df[column].fillna(default_value)
        return df
    
    def _impute_frequency_field(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Impute frequency fields with domain knowledge."""
        if pd.api.types.is_numeric_dtype(df[column]):
            # For numeric frequency, use median
            median_value = df[column].median()
            df[column] = df[column].fillna(median_value)
        else:
            # For categorical frequency, use 'sometimes' as default
            mode_value = df[column].mode()
            default_value = mode_value.iloc[0] if not mode_value.empty else 'sometimes'
            df[column] = df[column].fillna(default_value)
        
        return df
    
    def _impute_text_response(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Impute text response fields."""
        # For text responses, use a generic placeholder
        df[column] = df[column].fillna('no_response_provided')
        return df
    
    def _calculate_quality_score(self, original_nulls: int, final_nulls: int, 
                               dropped_columns: int, total_columns: int) -> float:
        """Calculate quality score for imputation process.
        
        Args:
            original_nulls: Number of null values before processing
            final_nulls: Number of null values after processing
            dropped_columns: Number of columns dropped
            total_columns: Total number of columns
            
        Returns:
            Quality score between 0 and 1
        """
        if original_nulls == 0:
            return 1.0  # Perfect score if no nulls to begin with
        
        # Calculate imputation success rate
        imputation_rate = (original_nulls - final_nulls) / original_nulls
        
        # Penalize for dropped columns
        column_retention_rate = (total_columns - dropped_columns) / total_columns
        
        # Combine scores with weights
        quality_score = (0.7 * imputation_rate) + (0.3 * column_retention_rate)
        
        return max(0.0, min(1.0, quality_score))
    
    def generate_imputation_report(self, results: List[ImputationResult], 
                                 output_file: str = "imputation_report.json") -> None:
        """Generate a comprehensive imputation report.
        
        Args:
            results: List of imputation results
            output_file: Output file path
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_datasets': len(results),
                'total_original_nulls': sum(r.original_nulls for r in results),
                'total_imputed_values': sum(r.imputed_values for r in results),
                'total_dropped_columns': sum(len(r.dropped_columns) for r in results),
                'average_quality_score': sum(r.quality_score for r in results) / len(results) if results else 0,
                'total_execution_time': sum(r.execution_time for r in results)
            },
            'detailed_results': [asdict(result) for result in results],
            'recommendations': self._generate_recommendations(results)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Imputation report saved to {output_file}")
    
    def _generate_recommendations(self, results: List[ImputationResult]) -> List[str]:
        """Generate recommendations based on imputation results."""
        recommendations = []
        
        avg_quality = sum(r.quality_score for r in results) / len(results) if results else 0
        total_warnings = sum(len(r.warnings) for r in results)
        
        if avg_quality < 0.7:
            recommendations.append("Consider reviewing imputation strategies - average quality score is below 0.7")
        
        if total_warnings > 0:
            recommendations.append(f"Address {total_warnings} warnings from imputation process")
        
        high_drop_rate = sum(len(r.dropped_columns) for r in results) / sum(len(results) for _ in results) if results else 0
        if high_drop_rate > 0.2:
            recommendations.append("High column drop rate detected - consider alternative imputation strategies")
        
        return recommendations

def main():
    """Main function for testing the NullValueHandler."""
    print("=" * 60)
    print("Mental Health Data Pipeline - Null Value Handler")
    print("=" * 60)
    
    try:
        # Initialize handler
        handler = NullValueHandler()
        
        # Example: Load and process a sample dataset
        print("\nTesting null value handling...")
        
        # Create sample data with nulls
        sample_data = {
            'anxiety_score': [1, 2, None, 4, 5, None, 3],
            'stress_level': ['low', None, 'high', 'medium', None, 'low', 'high'],
            'mood_rating': [3.5, None, 2.1, None, 4.8, 3.2, None],
            'response_text': ['feeling anxious', None, 'stressed about work', None, 'doing well', None, 'need help']
        }
        
        df = pd.DataFrame(sample_data)
        print(f"\nOriginal data shape: {df.shape}")
        print(f"Original null count: {df.isnull().sum().sum()}")
        
        # Analyze null patterns
        analysis = handler.analyze_null_patterns(df)
        print(f"\nNull analysis: {analysis['patterns']}")
        
        # Handle nulls
        processed_df, result = handler.handle_nulls(df, "sample_sheet")
        
        print(f"\nProcessed data shape: {processed_df.shape}")
        print(f"Final null count: {processed_df.isnull().sum().sum()}")
        print(f"Quality score: {result.quality_score:.3f}")
        print(f"Imputed values: {result.imputed_values}")
        
        # Generate report
        handler.generate_imputation_report([result], "sample_imputation_report.json")
        print("\nImputation report generated: sample_imputation_report.json")
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        print(f"Testing failed: {e}")

if __name__ == "__main__":
    main()