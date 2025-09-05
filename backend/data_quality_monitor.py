#!/usr/bin/env python3
"""
Data Quality Monitor for Mental Health Data Pipeline

This module implements comprehensive data quality monitoring and scoring:
- Multi-dimensional quality assessment
- Real-time quality tracking
- Automated quality alerts
- Historical quality trends
- Quality improvement recommendations
- Integration with data pipeline components

Author: Mental Health Data Pipeline Team
Date: January 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import statistics
from collections import defaultdict
import warnings
from pathlib import Path
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_quality_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Quality dimensions for assessment"""
    COMPLETENESS = "completeness"  # Missing data assessment
    ACCURACY = "accuracy"  # Data correctness
    CONSISTENCY = "consistency"  # Data uniformity
    VALIDITY = "validity"  # Format and constraint compliance
    UNIQUENESS = "uniqueness"  # Duplicate detection
    TIMELINESS = "timeliness"  # Data freshness
    RELEVANCE = "relevance"  # Data usefulness
    INTEGRITY = "integrity"  # Referential integrity

class QualityLevel(Enum):
    """Quality level classifications"""
    EXCELLENT = "excellent"  # 0.9 - 1.0
    GOOD = "good"  # 0.8 - 0.9
    ACCEPTABLE = "acceptable"  # 0.7 - 0.8
    POOR = "poor"  # 0.5 - 0.7
    CRITICAL = "critical"  # 0.0 - 0.5

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class QualityMetric:
    """Individual quality metric"""
    dimension: QualityDimension
    score: float
    weight: float
    details: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]

@dataclass
class QualityAssessment:
    """Complete quality assessment for a dataset"""
    dataset_name: str
    timestamp: datetime
    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[QualityDimension, QualityMetric]
    record_count: int
    field_count: int
    issues_summary: Dict[str, int]
    recommendations: List[str]
    execution_time: float

@dataclass
class QualityAlert:
    """Quality alert notification"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    dimension: QualityDimension
    dataset_name: str
    message: str
    current_score: float
    threshold: float
    details: Dict[str, Any]

@dataclass
class QualityTrend:
    """Quality trend analysis"""
    dimension: QualityDimension
    dataset_name: str
    time_period: str
    trend_direction: str  # 'improving', 'declining', 'stable'
    change_rate: float
    historical_scores: List[Tuple[datetime, float]]
    significance: float

class DataQualityMonitor:
    """
    Comprehensive data quality monitoring system for mental health data.
    
    Features:
    - Multi-dimensional quality assessment
    - Real-time quality tracking
    - Automated quality alerts
    - Historical quality trends
    - Quality improvement recommendations
    - Integration with pipeline components
    """
    
    def __init__(self, config_file: Optional[str] = None, db_path: str = "quality_monitor.db"):
        """
        Initialize the DataQualityMonitor.
        
        Args:
            config_file: Path to configuration file
            db_path: Path to SQLite database for storing quality history
        """
        self.db_path = db_path
        self.quality_thresholds = self._load_default_thresholds()
        self.dimension_weights = self._load_default_weights()
        self.alert_rules = self._load_default_alert_rules()
        self.quality_history: List[QualityAssessment] = []
        self.active_alerts: List[QualityAlert] = []
        self._lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        if config_file:
            self.load_config(config_file)
        
        logger.info("DataQualityMonitor initialized")
    
    def _load_default_thresholds(self) -> Dict[QualityDimension, Dict[str, float]]:
        """Load default quality thresholds for each dimension."""
        return {
            QualityDimension.COMPLETENESS: {
                'excellent': 0.95,
                'good': 0.85,
                'acceptable': 0.75,
                'poor': 0.60,
                'alert_threshold': 0.70
            },
            QualityDimension.ACCURACY: {
                'excellent': 0.98,
                'good': 0.90,
                'acceptable': 0.80,
                'poor': 0.65,
                'alert_threshold': 0.75
            },
            QualityDimension.CONSISTENCY: {
                'excellent': 0.95,
                'good': 0.85,
                'acceptable': 0.75,
                'poor': 0.60,
                'alert_threshold': 0.70
            },
            QualityDimension.VALIDITY: {
                'excellent': 0.98,
                'good': 0.90,
                'acceptable': 0.80,
                'poor': 0.65,
                'alert_threshold': 0.75
            },
            QualityDimension.UNIQUENESS: {
                'excellent': 0.98,
                'good': 0.90,
                'acceptable': 0.80,
                'poor': 0.65,
                'alert_threshold': 0.75
            },
            QualityDimension.TIMELINESS: {
                'excellent': 0.95,
                'good': 0.85,
                'acceptable': 0.75,
                'poor': 0.60,
                'alert_threshold': 0.70
            },
            QualityDimension.RELEVANCE: {
                'excellent': 0.90,
                'good': 0.80,
                'acceptable': 0.70,
                'poor': 0.55,
                'alert_threshold': 0.65
            },
            QualityDimension.INTEGRITY: {
                'excellent': 0.98,
                'good': 0.90,
                'acceptable': 0.80,
                'poor': 0.65,
                'alert_threshold': 0.75
            }
        }
    
    def _load_default_weights(self) -> Dict[QualityDimension, float]:
        """Load default weights for quality dimensions."""
        return {
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.ACCURACY: 0.20,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.VALIDITY: 0.15,
            QualityDimension.UNIQUENESS: 0.10,
            QualityDimension.TIMELINESS: 0.08,
            QualityDimension.RELEVANCE: 0.07,
            QualityDimension.INTEGRITY: 0.05
        }
    
    def _load_default_alert_rules(self) -> Dict[str, Any]:
        """Load default alert rules."""
        return {
            'quality_degradation_threshold': 0.1,  # Alert if quality drops by 10%
            'consecutive_failures_threshold': 3,
            'alert_cooldown_minutes': 30,
            'critical_score_threshold': 0.5
        }
    
    def _init_database(self) -> None:
        """Initialize SQLite database for quality history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Quality assessments table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quality_assessments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_name TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        overall_score REAL NOT NULL,
                        quality_level TEXT NOT NULL,
                        record_count INTEGER NOT NULL,
                        field_count INTEGER NOT NULL,
                        execution_time REAL NOT NULL,
                        metrics_json TEXT NOT NULL,
                        issues_json TEXT NOT NULL,
                        recommendations_json TEXT NOT NULL
                    )
                """)
                
                # Quality alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quality_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        dimension TEXT NOT NULL,
                        dataset_name TEXT NOT NULL,
                        message TEXT NOT NULL,
                        current_score REAL NOT NULL,
                        threshold_score REAL NOT NULL,
                        details_json TEXT NOT NULL,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_dataset_time ON quality_assessments(dataset_name, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_dataset_time ON quality_alerts(dataset_name, timestamp)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def load_config(self, config_file: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update thresholds
            if 'quality_thresholds' in config:
                for dim_name, thresholds in config['quality_thresholds'].items():
                    dimension = QualityDimension(dim_name)
                    self.quality_thresholds[dimension].update(thresholds)
            
            # Update weights
            if 'dimension_weights' in config:
                for dim_name, weight in config['dimension_weights'].items():
                    dimension = QualityDimension(dim_name)
                    self.dimension_weights[dimension] = weight
            
            # Update alert rules
            if 'alert_rules' in config:
                self.alert_rules.update(config['alert_rules'])
            
            logger.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def assess_quality(self, df: pd.DataFrame, dataset_name: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> QualityAssessment:
        """Perform comprehensive quality assessment on a DataFrame.
        
        Args:
            df: Input DataFrame
            dataset_name: Name of the dataset
            metadata: Optional metadata about the dataset
            
        Returns:
            QualityAssessment object
        """
        start_time = time.time()
        logger.info(f"Starting quality assessment for {dataset_name}")
        
        if metadata is None:
            metadata = {}
        
        # Calculate quality metrics for each dimension
        metrics = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._assess_completeness, df, metadata): QualityDimension.COMPLETENESS,
                executor.submit(self._assess_accuracy, df, metadata): QualityDimension.ACCURACY,
                executor.submit(self._assess_consistency, df, metadata): QualityDimension.CONSISTENCY,
                executor.submit(self._assess_validity, df, metadata): QualityDimension.VALIDITY,
                executor.submit(self._assess_uniqueness, df, metadata): QualityDimension.UNIQUENESS,
                executor.submit(self._assess_timeliness, df, metadata): QualityDimension.TIMELINESS,
                executor.submit(self._assess_relevance, df, metadata): QualityDimension.RELEVANCE,
                executor.submit(self._assess_integrity, df, metadata): QualityDimension.INTEGRITY
            }
            
            for future in futures:
                dimension = futures[future]
                try:
                    metrics[dimension] = future.result()
                except Exception as e:
                    logger.error(f"Failed to assess {dimension.value}: {e}")
                    # Create a default metric with low score
                    metrics[dimension] = QualityMetric(
                        dimension=dimension,
                        score=0.0,
                        weight=self.dimension_weights[dimension],
                        details={'error': str(e)},
                        issues=[f"Assessment failed: {str(e)}"],
                        recommendations=[f"Review {dimension.value} assessment logic"]
                    )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics)
        
        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)
        
        # Aggregate issues and recommendations
        issues_summary = self._aggregate_issues(metrics)
        recommendations = self._aggregate_recommendations(metrics, overall_score)
        
        execution_time = time.time() - start_time
        
        # Create assessment object
        assessment = QualityAssessment(
            dataset_name=dataset_name,
            timestamp=datetime.now(),
            overall_score=overall_score,
            quality_level=quality_level,
            metrics=metrics,
            record_count=len(df),
            field_count=len(df.columns),
            issues_summary=issues_summary,
            recommendations=recommendations,
            execution_time=execution_time
        )
        
        # Store assessment
        self._store_assessment(assessment)
        
        # Check for alerts
        self._check_quality_alerts(assessment)
        
        logger.info(f"Quality assessment completed for {dataset_name}: "
                   f"score={overall_score:.3f}, level={quality_level.value}")
        
        return assessment
    
    def _assess_completeness(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data completeness (missing values)."""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness_rate = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        
        # Field-level completeness
        field_completeness = {}
        critical_fields = metadata.get('critical_fields', [])
        
        issues = []
        recommendations = []
        
        for column in df.columns:
            field_missing_rate = df[column].isnull().sum() / len(df) if len(df) > 0 else 0
            field_completeness[column] = 1 - field_missing_rate
            
            if field_missing_rate > 0.2:  # More than 20% missing
                issues.append(f"High missing rate in {column}: {field_missing_rate:.1%}")
                
            if column in critical_fields and field_missing_rate > 0.05:  # Critical field with >5% missing
                issues.append(f"Critical field {column} has missing values: {field_missing_rate:.1%}")
                recommendations.append(f"Implement data collection improvements for {column}")
        
        if completeness_rate < 0.8:
            recommendations.append("Implement comprehensive data validation at collection point")
        
        details = {
            'overall_completeness': completeness_rate,
            'total_cells': total_cells,
            'missing_cells': missing_cells,
            'field_completeness': field_completeness,
            'critical_fields_status': {field: field_completeness.get(field, 0) for field in critical_fields}
        }
        
        return QualityMetric(
            dimension=QualityDimension.COMPLETENESS,
            score=completeness_rate,
            weight=self.dimension_weights[QualityDimension.COMPLETENESS],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_accuracy(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data accuracy (format compliance, range validation)."""
        total_values = 0
        accurate_values = 0
        issues = []
        recommendations = []
        field_accuracy = {}
        
        validation_rules = metadata.get('validation_rules', {})
        
        for column in df.columns:
            column_total = df[column].notna().sum()
            column_accurate = column_total  # Start with all as accurate
            
            if column_total == 0:
                field_accuracy[column] = 1.0
                continue
            
            # Check numeric ranges
            if pd.api.types.is_numeric_dtype(df[column]):
                if column in validation_rules:
                    rules = validation_rules[column]
                    if 'min_value' in rules:
                        invalid_count = (df[column] < rules['min_value']).sum()
                        column_accurate -= invalid_count
                        if invalid_count > 0:
                            issues.append(f"{column}: {invalid_count} values below minimum {rules['min_value']}")
                    
                    if 'max_value' in rules:
                        invalid_count = (df[column] > rules['max_value']).sum()
                        column_accurate -= invalid_count
                        if invalid_count > 0:
                            issues.append(f"{column}: {invalid_count} values above maximum {rules['max_value']}")
            
            # Check string patterns
            elif df[column].dtype == 'object':
                if column in validation_rules and 'pattern' in validation_rules[column]:
                    pattern = validation_rules[column]['pattern']
                    invalid_count = ~df[column].str.match(pattern, na=False).sum()
                    column_accurate -= invalid_count
                    if invalid_count > 0:
                        issues.append(f"{column}: {invalid_count} values don't match required pattern")
            
            field_accuracy[column] = max(0, column_accurate / column_total) if column_total > 0 else 1.0
            total_values += column_total
            accurate_values += max(0, column_accurate)
        
        overall_accuracy = accurate_values / total_values if total_values > 0 else 1.0
        
        if overall_accuracy < 0.9:
            recommendations.append("Implement stricter data validation rules")
            recommendations.append("Add real-time data quality checks at input")
        
        details = {
            'overall_accuracy': overall_accuracy,
            'total_values': total_values,
            'accurate_values': accurate_values,
            'field_accuracy': field_accuracy,
            'validation_rules_applied': len(validation_rules)
        }
        
        return QualityMetric(
            dimension=QualityDimension.ACCURACY,
            score=overall_accuracy,
            weight=self.dimension_weights[QualityDimension.ACCURACY],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_consistency(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data consistency (format uniformity, standardization)."""
        consistency_scores = []
        issues = []
        recommendations = []
        field_consistency = {}
        
        for column in df.columns:
            if df[column].dtype == 'object':
                # Check string case consistency
                non_null_values = df[column].dropna()
                if len(non_null_values) > 0:
                    # Check if values are consistently cased
                    all_lower = non_null_values.str.islower().all()
                    all_upper = non_null_values.str.isupper().all()
                    all_title = non_null_values.str.istitle().all()
                    
                    case_consistency = 1.0 if (all_lower or all_upper or all_title) else 0.7
                    
                    # Check for leading/trailing whitespace
                    whitespace_issues = (non_null_values != non_null_values.str.strip()).sum()
                    whitespace_consistency = 1.0 - (whitespace_issues / len(non_null_values))
                    
                    # Check for consistent separators in categorical data
                    separator_consistency = 1.0  # Default
                    if non_null_values.str.contains('[,;|]').any():
                        # Mixed separators detected
                        comma_count = non_null_values.str.contains(',').sum()
                        semicolon_count = non_null_values.str.contains(';').sum()
                        pipe_count = non_null_values.str.contains('\\|').sum()
                        
                        if sum([comma_count > 0, semicolon_count > 0, pipe_count > 0]) > 1:
                            separator_consistency = 0.5
                            issues.append(f"{column}: Mixed separators detected")
                    
                    field_score = (case_consistency + whitespace_consistency + separator_consistency) / 3
                    field_consistency[column] = field_score
                    consistency_scores.append(field_score)
                    
                    if field_score < 0.8:
                        issues.append(f"{column}: Low consistency score {field_score:.2f}")
                else:
                    field_consistency[column] = 1.0
                    consistency_scores.append(1.0)
            
            elif pd.api.types.is_numeric_dtype(df[column]):
                # Check numeric precision consistency
                non_null_values = df[column].dropna()
                if len(non_null_values) > 0:
                    # Check decimal places consistency
                    decimal_places = non_null_values.apply(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0)
                    decimal_consistency = 1.0 - (decimal_places.std() / (decimal_places.mean() + 1e-6))
                    decimal_consistency = max(0, min(1, decimal_consistency))
                    
                    field_consistency[column] = decimal_consistency
                    consistency_scores.append(decimal_consistency)
                else:
                    field_consistency[column] = 1.0
                    consistency_scores.append(1.0)
            else:
                field_consistency[column] = 1.0
                consistency_scores.append(1.0)
        
        overall_consistency = statistics.mean(consistency_scores) if consistency_scores else 1.0
        
        if overall_consistency < 0.8:
            recommendations.append("Implement data standardization procedures")
            recommendations.append("Add format validation at data entry points")
        
        details = {
            'overall_consistency': overall_consistency,
            'field_consistency': field_consistency,
            'fields_assessed': len(consistency_scores)
        }
        
        return QualityMetric(
            dimension=QualityDimension.CONSISTENCY,
            score=overall_consistency,
            weight=self.dimension_weights[QualityDimension.CONSISTENCY],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_validity(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data validity (constraint compliance)."""
        total_checks = 0
        passed_checks = 0
        issues = []
        recommendations = []
        field_validity = {}
        
        constraints = metadata.get('constraints', {})
        
        for column in df.columns:
            column_checks = 0
            column_passed = 0
            
            if column in constraints:
                column_constraints = constraints[column]
                
                # Check data type constraints
                if 'data_type' in column_constraints:
                    expected_type = column_constraints['data_type']
                    if expected_type == 'numeric':
                        valid_count = pd.to_numeric(df[column], errors='coerce').notna().sum()
                        total_count = df[column].notna().sum()
                        column_checks += total_count
                        column_passed += valid_count
                        
                        if valid_count < total_count:
                            issues.append(f"{column}: {total_count - valid_count} non-numeric values")
                
                # Check enum constraints
                if 'allowed_values' in column_constraints:
                    allowed_values = set(column_constraints['allowed_values'])
                    valid_mask = df[column].isin(allowed_values) | df[column].isna()
                    valid_count = valid_mask.sum()
                    total_count = len(df)
                    column_checks += total_count
                    column_passed += valid_count
                    
                    if valid_count < total_count:
                        invalid_values = df[~valid_mask][column].unique()
                        issues.append(f"{column}: Invalid values {list(invalid_values)}")
                
                # Check length constraints
                if 'max_length' in column_constraints and df[column].dtype == 'object':
                    max_length = column_constraints['max_length']
                    valid_mask = df[column].str.len() <= max_length
                    valid_count = valid_mask.sum()
                    total_count = df[column].notna().sum()
                    column_checks += total_count
                    column_passed += valid_count
                    
                    if valid_count < total_count:
                        issues.append(f"{column}: {total_count - valid_count} values exceed max length {max_length}")
            
            field_validity[column] = column_passed / column_checks if column_checks > 0 else 1.0
            total_checks += column_checks
            passed_checks += column_passed
        
        overall_validity = passed_checks / total_checks if total_checks > 0 else 1.0
        
        if overall_validity < 0.9:
            recommendations.append("Review and update data validation constraints")
            recommendations.append("Implement stricter input validation")
        
        details = {
            'overall_validity': overall_validity,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'field_validity': field_validity,
            'constraints_applied': len(constraints)
        }
        
        return QualityMetric(
            dimension=QualityDimension.VALIDITY,
            score=overall_validity,
            weight=self.dimension_weights[QualityDimension.VALIDITY],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_uniqueness(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data uniqueness (duplicate detection)."""
        issues = []
        recommendations = []
        
        # Overall record uniqueness
        total_records = len(df)
        unique_records = len(df.drop_duplicates())
        record_uniqueness = unique_records / total_records if total_records > 0 else 1.0
        
        # Field-level uniqueness for ID fields
        unique_fields = metadata.get('unique_fields', [])
        field_uniqueness = {}
        
        for column in df.columns:
            if column in unique_fields or 'id' in column.lower():
                non_null_count = df[column].notna().sum()
                unique_count = df[column].nunique()
                field_uniqueness[column] = unique_count / non_null_count if non_null_count > 0 else 1.0
                
                if field_uniqueness[column] < 1.0:
                    duplicate_count = non_null_count - unique_count
                    issues.append(f"{column}: {duplicate_count} duplicate values")
        
        # Check for duplicate rows
        duplicate_rows = total_records - unique_records
        if duplicate_rows > 0:
            issues.append(f"Dataset contains {duplicate_rows} duplicate rows")
            recommendations.append("Implement duplicate detection and removal procedures")
        
        if record_uniqueness < 0.95:
            recommendations.append("Review data collection process for duplicate prevention")
        
        details = {
            'record_uniqueness': record_uniqueness,
            'total_records': total_records,
            'unique_records': unique_records,
            'duplicate_records': duplicate_rows,
            'field_uniqueness': field_uniqueness
        }
        
        return QualityMetric(
            dimension=QualityDimension.UNIQUENESS,
            score=record_uniqueness,
            weight=self.dimension_weights[QualityDimension.UNIQUENESS],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_timeliness(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data timeliness (freshness)."""
        issues = []
        recommendations = []
        
        # Look for timestamp columns
        timestamp_columns = metadata.get('timestamp_columns', [])
        if not timestamp_columns:
            # Auto-detect timestamp columns
            for column in df.columns:
                if any(keyword in column.lower() for keyword in ['time', 'date', 'created', 'updated']):
                    timestamp_columns.append(column)
        
        if not timestamp_columns:
            # No timestamp data available
            details = {
                'timeliness_score': 1.0,
                'message': 'No timestamp columns found for timeliness assessment'
            }
            return QualityMetric(
                dimension=QualityDimension.TIMELINESS,
                score=1.0,
                weight=self.dimension_weights[QualityDimension.TIMELINESS],
                details=details,
                issues=[],
                recommendations=["Add timestamp columns for better timeliness tracking"]
            )
        
        timeliness_scores = []
        current_time = datetime.now()
        
        for column in timestamp_columns:
            try:
                # Convert to datetime
                timestamps = pd.to_datetime(df[column], errors='coerce')
                valid_timestamps = timestamps.dropna()
                
                if len(valid_timestamps) == 0:
                    continue
                
                # Calculate age of data
                ages = (current_time - valid_timestamps).dt.total_seconds() / 3600  # Hours
                
                # Define freshness thresholds (configurable)
                fresh_threshold = metadata.get('fresh_threshold_hours', 24)  # 24 hours
                stale_threshold = metadata.get('stale_threshold_hours', 168)  # 1 week
                
                fresh_count = (ages <= fresh_threshold).sum()
                stale_count = (ages > stale_threshold).sum()
                
                freshness_score = fresh_count / len(valid_timestamps)
                timeliness_scores.append(freshness_score)
                
                if stale_count > 0:
                    issues.append(f"{column}: {stale_count} records older than {stale_threshold} hours")
                
            except Exception as e:
                issues.append(f"Failed to assess timeliness for {column}: {str(e)}")
        
        overall_timeliness = statistics.mean(timeliness_scores) if timeliness_scores else 1.0
        
        if overall_timeliness < 0.8:
            recommendations.append("Implement more frequent data updates")
            recommendations.append("Set up automated data freshness monitoring")
        
        details = {
            'overall_timeliness': overall_timeliness,
            'timestamp_columns_assessed': len(timestamp_columns),
            'timeliness_scores': dict(zip(timestamp_columns, timeliness_scores))
        }
        
        return QualityMetric(
            dimension=QualityDimension.TIMELINESS,
            score=overall_timeliness,
            weight=self.dimension_weights[QualityDimension.TIMELINESS],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_relevance(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data relevance (usefulness for intended purpose)."""
        issues = []
        recommendations = []
        
        # Check for required fields
        required_fields = metadata.get('required_fields', [])
        missing_required = [field for field in required_fields if field not in df.columns]
        
        if missing_required:
            issues.extend([f"Missing required field: {field}" for field in missing_required])
        
        # Check field population rates
        relevance_scores = []
        for column in df.columns:
            population_rate = df[column].notna().sum() / len(df) if len(df) > 0 else 0
            
            # Weight by importance (required fields are more important)
            if column in required_fields:
                weight = 1.0
            else:
                weight = 0.7
            
            relevance_scores.append(population_rate * weight)
            
            if population_rate < 0.1:  # Less than 10% populated
                issues.append(f"{column}: Very low population rate {population_rate:.1%}")
        
        # Check for business rule compliance
        business_rules = metadata.get('business_rules', [])
        rule_compliance = 1.0
        
        for rule in business_rules:
            # Simple rule evaluation (can be extended)
            if rule.get('type') == 'field_relationship':
                field1, field2 = rule['fields']
                if field1 in df.columns and field2 in df.columns:
                    # Example: if field1 is not null, field2 should also not be null
                    violations = ((df[field1].notna()) & (df[field2].isna())).sum()
                    if violations > 0:
                        rule_compliance *= 0.9  # Reduce score for violations
                        issues.append(f"Business rule violation: {rule['description']} ({violations} cases)")
        
        overall_relevance = statistics.mean(relevance_scores) * rule_compliance if relevance_scores else 0.0
        
        if overall_relevance < 0.7:
            recommendations.append("Review data collection requirements")
            recommendations.append("Remove or improve low-relevance fields")
        
        if missing_required:
            recommendations.append("Ensure all required fields are collected")
        
        details = {
            'overall_relevance': overall_relevance,
            'required_fields_present': len(required_fields) - len(missing_required),
            'total_required_fields': len(required_fields),
            'business_rule_compliance': rule_compliance,
            'field_population_rates': {col: df[col].notna().sum() / len(df) for col in df.columns}
        }
        
        return QualityMetric(
            dimension=QualityDimension.RELEVANCE,
            score=overall_relevance,
            weight=self.dimension_weights[QualityDimension.RELEVANCE],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_integrity(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> QualityMetric:
        """Assess data integrity (referential integrity, relationships)."""
        issues = []
        recommendations = []
        integrity_scores = []
        
        # Check referential integrity
        foreign_keys = metadata.get('foreign_keys', {})
        
        for fk_field, reference_info in foreign_keys.items():
            if fk_field in df.columns:
                # Check if foreign key values exist in reference
                reference_values = set(reference_info.get('valid_values', []))
                if reference_values:
                    fk_values = set(df[fk_field].dropna())
                    invalid_fks = fk_values - reference_values
                    
                    if invalid_fks:
                        issues.append(f"{fk_field}: {len(invalid_fks)} invalid foreign key values")
                        integrity_scores.append(0.5)
                    else:
                        integrity_scores.append(1.0)
                else:
                    integrity_scores.append(1.0)  # No reference to check against
        
        # Check data relationships
        relationships = metadata.get('relationships', [])
        
        for relationship in relationships:
            rel_type = relationship.get('type')
            fields = relationship.get('fields', [])
            
            if rel_type == 'one_to_many' and len(fields) >= 2:
                parent_field, child_field = fields[0], fields[1]
                if parent_field in df.columns and child_field in df.columns:
                    # Check if relationship holds
                    grouped = df.groupby(parent_field)[child_field].nunique()
                    violations = (grouped > 1).sum()
                    
                    if violations > 0:
                        issues.append(f"One-to-many relationship violated: {parent_field} -> {child_field}")
                        integrity_scores.append(0.7)
                    else:
                        integrity_scores.append(1.0)
        
        # Check for orphaned records
        parent_child_relationships = metadata.get('parent_child_fields', {})
        for parent_field, child_field in parent_child_relationships.items():
            if parent_field in df.columns and child_field in df.columns:
                parent_values = set(df[parent_field].dropna())
                child_values = set(df[child_field].dropna())
                orphaned = child_values - parent_values
                
                if orphaned:
                    issues.append(f"Orphaned records in {child_field}: {len(orphaned)} values")
                    integrity_scores.append(0.8)
                else:
                    integrity_scores.append(1.0)
        
        overall_integrity = statistics.mean(integrity_scores) if integrity_scores else 1.0
        
        if overall_integrity < 0.9:
            recommendations.append("Review and fix referential integrity issues")
            recommendations.append("Implement foreign key constraints")
        
        details = {
            'overall_integrity': overall_integrity,
            'foreign_keys_checked': len(foreign_keys),
            'relationships_checked': len(relationships),
            'integrity_violations': len(issues)
        }
        
        return QualityMetric(
            dimension=QualityDimension.INTEGRITY,
            score=overall_integrity,
            weight=self.dimension_weights[QualityDimension.INTEGRITY],
            details=details,
            issues=issues,
            recommendations=recommendations
        )
    
    def _calculate_overall_score(self, metrics: Dict[QualityDimension, QualityMetric]) -> float:
        """Calculate weighted overall quality score."""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for dimension, metric in metrics.items():
            weighted_sum += metric.score * metric.weight
            total_weight += metric.weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on score."""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.8:
            return QualityLevel.GOOD
        elif score >= 0.7:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.5:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _aggregate_issues(self, metrics: Dict[QualityDimension, QualityMetric]) -> Dict[str, int]:
        """Aggregate issues by category."""
        issues_summary = defaultdict(int)
        
        for metric in metrics.values():
            for issue in metric.issues:
                # Categorize issues
                if 'missing' in issue.lower() or 'null' in issue.lower():
                    issues_summary['missing_data'] += 1
                elif 'duplicate' in issue.lower():
                    issues_summary['duplicates'] += 1
                elif 'invalid' in issue.lower() or 'violation' in issue.lower():
                    issues_summary['validation_errors'] += 1
                elif 'consistency' in issue.lower() or 'format' in issue.lower():
                    issues_summary['consistency_issues'] += 1
                else:
                    issues_summary['other'] += 1
        
        return dict(issues_summary)
    
    def _aggregate_recommendations(self, metrics: Dict[QualityDimension, QualityMetric], 
                                 overall_score: float) -> List[str]:
        """Aggregate and prioritize recommendations."""
        all_recommendations = []
        
        for metric in metrics.values():
            all_recommendations.extend(metric.recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        # Add overall recommendations based on score
        if overall_score < 0.5:
            unique_recommendations.insert(0, "CRITICAL: Immediate data quality intervention required")
        elif overall_score < 0.7:
            unique_recommendations.insert(0, "Implement comprehensive data quality improvement plan")
        
        return unique_recommendations
    
    def _store_assessment(self, assessment: QualityAssessment) -> None:
        """Store quality assessment in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO quality_assessments 
                    (dataset_name, timestamp, overall_score, quality_level, record_count, 
                     field_count, execution_time, metrics_json, issues_json, recommendations_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment.dataset_name,
                    assessment.timestamp.isoformat(),
                    assessment.overall_score,
                    assessment.quality_level.value,
                    assessment.record_count,
                    assessment.field_count,
                    assessment.execution_time,
                    json.dumps({dim.value: asdict(metric) for dim, metric in assessment.metrics.items()}, default=str),
                    json.dumps(assessment.issues_summary),
                    json.dumps(assessment.recommendations)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store assessment: {e}")
    
    def _check_quality_alerts(self, assessment: QualityAssessment) -> None:
        """Check for quality alerts based on assessment."""
        with self._lock:
            # Check overall score alert
            if assessment.overall_score < self.alert_rules['critical_score_threshold']:
                alert = QualityAlert(
                    alert_id=f"critical_quality_{assessment.dataset_name}_{int(time.time())}",
                    timestamp=datetime.now(),
                    severity=AlertSeverity.CRITICAL,
                    dimension=QualityDimension.ACCURACY,  # Use accuracy as default
                    dataset_name=assessment.dataset_name,
                    message=f"Critical quality score: {assessment.overall_score:.3f}",
                    current_score=assessment.overall_score,
                    threshold=self.alert_rules['critical_score_threshold'],
                    details={'assessment_id': assessment.dataset_name}
                )
                self._create_alert(alert)
            
            # Check dimension-specific alerts
            for dimension, metric in assessment.metrics.items():
                threshold = self.quality_thresholds[dimension]['alert_threshold']
                if metric.score < threshold:
                    severity = AlertSeverity.ERROR if metric.score < 0.5 else AlertSeverity.WARNING
                    
                    alert = QualityAlert(
                        alert_id=f"{dimension.value}_{assessment.dataset_name}_{int(time.time())}",
                        timestamp=datetime.now(),
                        severity=severity,
                        dimension=dimension,
                        dataset_name=assessment.dataset_name,
                        message=f"{dimension.value} quality below threshold: {metric.score:.3f}",
                        current_score=metric.score,
                        threshold=threshold,
                        details={'issues': metric.issues}
                    )
                    self._create_alert(alert)
    
    def _create_alert(self, alert: QualityAlert) -> None:
        """Create and store a quality alert."""
        try:
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR IGNORE INTO quality_alerts 
                    (alert_id, timestamp, severity, dimension, dataset_name, message, 
                     current_score, threshold_score, details_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.timestamp.isoformat(),
                    alert.severity.value,
                    alert.dimension.value,
                    alert.dataset_name,
                    alert.message,
                    alert.current_score,
                    alert.threshold,
                    json.dumps(alert.details)
                ))
                
                conn.commit()
            
            # Add to active alerts
            self.active_alerts.append(alert)
            
            logger.warning(f"Quality alert created: {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    def get_quality_trends(self, dataset_name: str, days: int = 30) -> List[QualityTrend]:
        """Get quality trends for a dataset over specified time period.
        
        Args:
            dataset_name: Name of the dataset
            days: Number of days to analyze
            
        Returns:
            List of quality trends by dimension
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get historical assessments
                since_date = (datetime.now() - timedelta(days=days)).isoformat()
                cursor.execute("""
                    SELECT timestamp, overall_score, metrics_json 
                    FROM quality_assessments 
                    WHERE dataset_name = ? AND timestamp >= ?
                    ORDER BY timestamp
                """, (dataset_name, since_date))
                
                rows = cursor.fetchall()
                
                if len(rows) < 2:
                    return []  # Need at least 2 points for trend
                
                trends = []
                
                # Analyze overall trend
                timestamps = [datetime.fromisoformat(row[0]) for row in rows]
                overall_scores = [row[1] for row in rows]
                
                # Calculate trend for overall score
                overall_trend = self._calculate_trend(timestamps, overall_scores)
                
                # Analyze dimension-specific trends
                dimension_scores = defaultdict(list)
                
                for row in rows:
                    metrics_data = json.loads(row[2])
                    for dim_name, metric_data in metrics_data.items():
                        dimension = QualityDimension(dim_name)
                        dimension_scores[dimension].append(metric_data['score'])
                
                for dimension, scores in dimension_scores.items():
                    if len(scores) >= 2:
                        trend = self._calculate_trend(timestamps, scores)
                        trends.append(QualityTrend(
                            dimension=dimension,
                            dataset_name=dataset_name,
                            time_period=f"{days} days",
                            trend_direction=trend['direction'],
                            change_rate=trend['change_rate'],
                            historical_scores=list(zip(timestamps, scores)),
                            significance=trend['significance']
                        ))
                
                return trends
                
        except Exception as e:
            logger.error(f"Failed to get quality trends: {e}")
            return []
    
    def _calculate_trend(self, timestamps: List[datetime], scores: List[float]) -> Dict[str, Any]:
        """Calculate trend statistics for a time series."""
        if len(scores) < 2:
            return {'direction': 'stable', 'change_rate': 0.0, 'significance': 0.0}
        
        # Simple linear trend calculation
        x = np.arange(len(scores))
        y = np.array(scores)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Determine direction
        if abs(slope) < 0.01:  # Less than 1% change
            direction = 'stable'
        elif slope > 0:
            direction = 'improving'
        else:
            direction = 'declining'
        
        # Calculate change rate (percentage change from first to last)
        change_rate = (scores[-1] - scores[0]) / scores[0] if scores[0] != 0 else 0
        
        # Calculate significance (correlation coefficient)
        correlation = np.corrcoef(x, y)[0, 1] if len(scores) > 2 else 0
        significance = abs(correlation)
        
        return {
            'direction': direction,
            'change_rate': change_rate,
            'significance': significance
        }
    
    def generate_quality_report(self, dataset_name: Optional[str] = None, 
                              output_file: str = "quality_report.json") -> None:
        """Generate comprehensive quality report.
        
        Args:
            dataset_name: Specific dataset name (None for all datasets)
            output_file: Output file path
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get recent assessments
                if dataset_name:
                    cursor.execute("""
                        SELECT * FROM quality_assessments 
                        WHERE dataset_name = ?
                        ORDER BY timestamp DESC LIMIT 10
                    """, (dataset_name,))
                else:
                    cursor.execute("""
                        SELECT * FROM quality_assessments 
                        ORDER BY timestamp DESC LIMIT 50
                    """)
                
                assessments = cursor.fetchall()
                
                # Get active alerts
                cursor.execute("""
                    SELECT * FROM quality_alerts 
                    WHERE resolved = FALSE
                    ORDER BY timestamp DESC
                """)
                
                alerts = cursor.fetchall()
                
                # Generate report
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'report_scope': dataset_name or 'all_datasets',
                    'summary': {
                        'total_assessments': len(assessments),
                        'active_alerts': len(alerts),
                        'datasets_monitored': len(set(row[1] for row in assessments))
                    },
                    'recent_assessments': [
                        {
                            'dataset_name': row[1],
                            'timestamp': row[2],
                            'overall_score': row[3],
                            'quality_level': row[4],
                            'record_count': row[5],
                            'field_count': row[6]
                        } for row in assessments
                    ],
                    'active_alerts': [
                        {
                            'alert_id': row[1],
                            'timestamp': row[2],
                            'severity': row[3],
                            'dimension': row[4],
                            'dataset_name': row[5],
                            'message': row[6],
                            'current_score': row[7],
                            'threshold': row[8]
                        } for row in alerts
                    ]
                }
                
                # Add trends if specific dataset
                if dataset_name:
                    trends = self.get_quality_trends(dataset_name)
                    report['quality_trends'] = [asdict(trend) for trend in trends]
                
                # Save report
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Quality report generated: {output_file}")
                
        except Exception as e:
            logger.error(f"Failed to generate quality report: {e}")
            raise

def main():
    """Main function for testing the DataQualityMonitor."""
    print("=" * 60)
    print("Mental Health Data Pipeline - Data Quality Monitor")
    print("=" * 60)
    
    try:
        # Initialize monitor
        monitor = DataQualityMonitor()
        
        # Example: Create sample data with quality issues
        print("\nTesting data quality monitoring...")
        
        sample_data = {
            'record_id': [1, 2, 3, 4, 5, 5],  # Duplicate ID
            'anxiety_score': [1, 2, None, 4, 15, 3],  # Missing value and out of range
            'stress_level': ['low', 'HIGH', 'medium', None, 'invalid', 'low'],  # Inconsistent case and invalid value
            'response_text': ['  feeling anxious  ', 'STRESSED', None, 'doing well', '', 'normal'],  # Formatting issues
            'created_at': ['2025-01-01', '2025-01-02', '2025-01-03', '2024-12-01', None, '2025-01-05']  # Old data and missing
        }
        
        df = pd.DataFrame(sample_data)
        print(f"\nSample data shape: {df.shape}")
        print("Sample data:")
        print(df)
        
        # Define metadata for assessment
        metadata = {
            'required_fields': ['record_id', 'anxiety_score'],
            'unique_fields': ['record_id'],
            'timestamp_columns': ['created_at'],
            'validation_rules': {
                'anxiety_score': {'min_value': 0, 'max_value': 10}
            },
            'constraints': {
                'stress_level': {
                    'allowed_values': ['low', 'medium', 'high']
                }
            }
        }
        
        # Perform quality assessment
        assessment = monitor.assess_quality(df, "sample_dataset", metadata)
        
        print(f"\nQuality Assessment Results:")
        print(f"Overall Score: {assessment.overall_score:.3f}")
        print(f"Quality Level: {assessment.quality_level.value}")
        print(f"Execution Time: {assessment.execution_time:.2f}s")
        
        print("\nDimension Scores:")
        for dimension, metric in assessment.metrics.items():
            print(f"  {dimension.value}: {metric.score:.3f}")
        
        print(f"\nIssues Summary: {assessment.issues_summary}")
        
        if assessment.recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(assessment.recommendations[:5], 1):
                print(f"  {i}. {rec}")
        
        # Check for alerts
        if monitor.active_alerts:
            print(f"\nActive Alerts: {len(monitor.active_alerts)}")
            for alert in monitor.active_alerts[-3:]:  # Show last 3
                print(f"  {alert.severity.value.upper()}: {alert.message}")
        
        # Generate report
        monitor.generate_quality_report("sample_dataset", "sample_quality_report.json")
        print("\nQuality report generated: sample_quality_report.json")
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        print(f"Testing failed: {e}")

if __name__ == "__main__":
    main()