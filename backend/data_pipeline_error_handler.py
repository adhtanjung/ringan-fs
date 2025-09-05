#!/usr/bin/env python3
"""
Data Pipeline Error Handler for Mental Health Data Pipeline

This module implements comprehensive error handling and recovery strategies:
- Automatic error detection and classification
- Recovery strategies for common failure scenarios
- Circuit breaker pattern for external services
- Retry mechanisms with exponential backoff
- Error logging and alerting
- Pipeline health monitoring
- Graceful degradation strategies

Author: Mental Health Data Pipeline Team
Date: January 2025
"""

import logging
import time
import json
import traceback
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import sqlite3
from pathlib import Path
import functools
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from collections import defaultdict, deque
import psutil
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Types of pipeline errors"""
    CONNECTION_ERROR = "connection_error"
    DATA_VALIDATION_ERROR = "data_validation_error"
    PROCESSING_ERROR = "processing_error"
    RESOURCE_ERROR = "resource_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    UNKNOWN_ERROR = "unknown_error"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecoveryStrategy(Enum):
    """Recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    CIRCUIT_BREAK = "circuit_break"
    GRACEFUL_DEGRADATION = "graceful_degradation"

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ErrorContext:
    """Context information for an error"""
    error_id: str
    timestamp: datetime
    error_type: ErrorType
    severity: ErrorSeverity
    component: str
    operation: str
    error_message: str
    stack_trace: str
    metadata: Dict[str, Any]
    recovery_attempts: int = 0
    resolved: bool = False

@dataclass
class RecoveryAction:
    """Recovery action configuration"""
    strategy: RecoveryStrategy
    max_attempts: int
    delay_seconds: float
    backoff_multiplier: float
    fallback_function: Optional[Callable] = None
    conditions: Dict[str, Any] = None

@dataclass
class CircuitBreaker:
    """Circuit breaker for external services"""
    service_name: str
    failure_threshold: int
    recovery_timeout: int
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    success_count: int = 0

@dataclass
class PipelineHealth:
    """Pipeline health status"""
    component: str
    status: str  # healthy, degraded, unhealthy
    last_check: datetime
    error_rate: float
    response_time: float
    details: Dict[str, Any]

class DataPipelineErrorHandler:
    """
    Comprehensive error handling and recovery system for data pipeline.
    
    Features:
    - Automatic error detection and classification
    - Recovery strategies with retry mechanisms
    - Circuit breaker pattern for external services
    - Error logging and alerting
    - Pipeline health monitoring
    - Graceful degradation strategies
    """
    
    def __init__(self, config_file: Optional[str] = None, db_path: str = "pipeline_errors.db"):
        """
        Initialize the DataPipelineErrorHandler.
        
        Args:
            config_file: Path to configuration file
            db_path: Path to SQLite database for error storage
        """
        self.db_path = db_path
        self.error_history: List[ErrorContext] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.recovery_strategies: Dict[ErrorType, RecoveryAction] = self._load_default_strategies()
        self.health_status: Dict[str, PipelineHealth] = {}
        self.alert_config = self._load_default_alert_config()
        self._lock = threading.Lock()
        self.error_counts = defaultdict(int)
        self.recent_errors = deque(maxlen=100)
        
        # Initialize database
        self._init_database()
        
        if config_file:
            self.load_config(config_file)
        
        # Start health monitoring thread
        self._start_health_monitor()
        
        logger.info("DataPipelineErrorHandler initialized")
    
    def _load_default_strategies(self) -> Dict[ErrorType, RecoveryAction]:
        """Load default recovery strategies for each error type."""
        return {
            ErrorType.CONNECTION_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=3,
                delay_seconds=1.0,
                backoff_multiplier=2.0
            ),
            ErrorType.DATA_VALIDATION_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.SKIP,
                max_attempts=1,
                delay_seconds=0.0,
                backoff_multiplier=1.0
            ),
            ErrorType.PROCESSING_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=2,
                delay_seconds=0.5,
                backoff_multiplier=1.5
            ),
            ErrorType.RESOURCE_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                max_attempts=1,
                delay_seconds=5.0,
                backoff_multiplier=1.0
            ),
            ErrorType.TIMEOUT_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=2,
                delay_seconds=2.0,
                backoff_multiplier=2.0
            ),
            ErrorType.AUTHENTICATION_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.ABORT,
                max_attempts=1,
                delay_seconds=0.0,
                backoff_multiplier=1.0
            ),
            ErrorType.PERMISSION_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.ABORT,
                max_attempts=1,
                delay_seconds=0.0,
                backoff_multiplier=1.0
            ),
            ErrorType.CONFIGURATION_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.ABORT,
                max_attempts=1,
                delay_seconds=0.0,
                backoff_multiplier=1.0
            ),
            ErrorType.EXTERNAL_SERVICE_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.CIRCUIT_BREAK,
                max_attempts=3,
                delay_seconds=1.0,
                backoff_multiplier=2.0
            ),
            ErrorType.UNKNOWN_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=1,
                delay_seconds=1.0,
                backoff_multiplier=1.0
            )
        }
    
    def _load_default_alert_config(self) -> Dict[str, Any]:
        """Load default alert configuration."""
        return {
            'email_enabled': False,
            'webhook_enabled': False,
            'smtp_server': 'localhost',
            'smtp_port': 587,
            'email_from': 'pipeline@example.com',
            'email_to': ['admin@example.com'],
            'webhook_url': '',
            'alert_thresholds': {
                'error_rate_per_hour': 10,
                'critical_errors_per_hour': 1,
                'consecutive_failures': 5
            }
        }
    
    def _init_database(self) -> None:
        """Initialize SQLite database for error storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Error contexts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS error_contexts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_id TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        error_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        component TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        stack_trace TEXT NOT NULL,
                        metadata_json TEXT NOT NULL,
                        recovery_attempts INTEGER DEFAULT 0,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Circuit breaker states table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS circuit_breakers (
                        service_name TEXT PRIMARY KEY,
                        state TEXT NOT NULL,
                        failure_count INTEGER DEFAULT 0,
                        last_failure_time TEXT,
                        success_count INTEGER DEFAULT 0,
                        failure_threshold INTEGER NOT NULL,
                        recovery_timeout INTEGER NOT NULL
                    )
                """)
                
                # Health status table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS health_status (
                        component TEXT PRIMARY KEY,
                        status TEXT NOT NULL,
                        last_check TEXT NOT NULL,
                        error_rate REAL NOT NULL,
                        response_time REAL NOT NULL,
                        details_json TEXT NOT NULL
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON error_contexts(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_component ON error_contexts(component)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_type ON error_contexts(error_type)")
                
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
            
            # Update recovery strategies
            if 'recovery_strategies' in config:
                for error_type_name, strategy_config in config['recovery_strategies'].items():
                    error_type = ErrorType(error_type_name)
                    self.recovery_strategies[error_type] = RecoveryAction(**strategy_config)
            
            # Update alert configuration
            if 'alert_config' in config:
                self.alert_config.update(config['alert_config'])
            
            # Initialize circuit breakers
            if 'circuit_breakers' in config:
                for service_name, cb_config in config['circuit_breakers'].items():
                    self.circuit_breakers[service_name] = CircuitBreaker(
                        service_name=service_name,
                        **cb_config
                    )
            
            logger.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def handle_error(self, error: Exception, component: str, operation: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception that occurred
            component: Component where error occurred
            operation: Operation that failed
            metadata: Additional context metadata
            
        Returns:
            True if error was recovered, False otherwise
        """
        error_id = f"{component}_{operation}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Classify error
        error_type = self._classify_error(error)
        severity = self._determine_severity(error_type, error)
        
        # Create error context
        error_context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.now(),
            error_type=error_type,
            severity=severity,
            component=component,
            operation=operation,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            metadata=metadata or {}
        )
        
        # Store error
        self._store_error(error_context)
        
        # Update error statistics
        with self._lock:
            self.error_counts[error_type] += 1
            self.recent_errors.append(error_context)
        
        # Log error
        logger.error(f"Error in {component}.{operation}: {error_type.value} - {str(error)}")
        
        # Attempt recovery
        recovery_success = self._attempt_recovery(error_context)
        
        # Send alerts if necessary
        self._check_alert_conditions(error_context)
        
        # Update health status
        self._update_health_status(component, not recovery_success)
        
        return recovery_success
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error based on exception type and message."""
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        # Connection-related errors
        if any(keyword in error_str for keyword in ['connection', 'network', 'socket', 'dns']):
            return ErrorType.CONNECTION_ERROR
        
        if any(keyword in error_type_name for keyword in ['connection', 'socket', 'network']):
            return ErrorType.CONNECTION_ERROR
        
        # Authentication/Permission errors
        if any(keyword in error_str for keyword in ['authentication', 'unauthorized', 'forbidden', 'access denied']):
            return ErrorType.AUTHENTICATION_ERROR
        
        if any(keyword in error_str for keyword in ['permission', 'not allowed', 'insufficient privileges']):
            return ErrorType.PERMISSION_ERROR
        
        # Timeout errors
        if any(keyword in error_str for keyword in ['timeout', 'timed out']):
            return ErrorType.TIMEOUT_ERROR
        
        if 'timeout' in error_type_name:
            return ErrorType.TIMEOUT_ERROR
        
        # Resource errors
        if any(keyword in error_str for keyword in ['memory', 'disk space', 'resource', 'quota']):
            return ErrorType.RESOURCE_ERROR
        
        # Data validation errors
        if any(keyword in error_str for keyword in ['validation', 'invalid', 'format', 'schema']):
            return ErrorType.DATA_VALIDATION_ERROR
        
        if any(keyword in error_type_name for keyword in ['validation', 'value', 'type']):
            return ErrorType.DATA_VALIDATION_ERROR
        
        # Configuration errors
        if any(keyword in error_str for keyword in ['configuration', 'config', 'setting', 'parameter']):
            return ErrorType.CONFIGURATION_ERROR
        
        # External service errors
        if any(keyword in error_str for keyword in ['service unavailable', 'bad gateway', 'service error']):
            return ErrorType.EXTERNAL_SERVICE_ERROR
        
        # Processing errors (default for many exceptions)
        if any(keyword in error_type_name for keyword in ['runtime', 'processing', 'execution']):
            return ErrorType.PROCESSING_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def _determine_severity(self, error_type: ErrorType, error: Exception) -> ErrorSeverity:
        """Determine error severity based on type and context."""
        # Critical errors that require immediate attention
        if error_type in [ErrorType.AUTHENTICATION_ERROR, ErrorType.PERMISSION_ERROR, 
                         ErrorType.CONFIGURATION_ERROR]:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if error_type in [ErrorType.RESOURCE_ERROR, ErrorType.EXTERNAL_SERVICE_ERROR]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if error_type in [ErrorType.CONNECTION_ERROR, ErrorType.TIMEOUT_ERROR, 
                         ErrorType.PROCESSING_ERROR]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        if error_type == ErrorType.DATA_VALIDATION_ERROR:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM  # Default
    
    def _attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Attempt to recover from an error using configured strategy."""
        error_type = error_context.error_type
        
        if error_type not in self.recovery_strategies:
            logger.warning(f"No recovery strategy defined for {error_type.value}")
            return False
        
        strategy = self.recovery_strategies[error_type]
        
        if strategy.strategy == RecoveryStrategy.ABORT:
            logger.info(f"Aborting due to {error_type.value}")
            return False
        
        elif strategy.strategy == RecoveryStrategy.SKIP:
            logger.info(f"Skipping operation due to {error_type.value}")
            error_context.resolved = True
            return True
        
        elif strategy.strategy == RecoveryStrategy.RETRY:
            return self._retry_operation(error_context, strategy)
        
        elif strategy.strategy == RecoveryStrategy.CIRCUIT_BREAK:
            return self._handle_circuit_breaker(error_context, strategy)
        
        elif strategy.strategy == RecoveryStrategy.FALLBACK:
            return self._execute_fallback(error_context, strategy)
        
        elif strategy.strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
            return self._graceful_degradation(error_context, strategy)
        
        return False
    
    def _retry_operation(self, error_context: ErrorContext, strategy: RecoveryAction) -> bool:
        """Retry operation with exponential backoff."""
        max_attempts = strategy.max_attempts
        delay = strategy.delay_seconds
        
        for attempt in range(max_attempts):
            if attempt > 0:
                sleep_time = delay * (strategy.backoff_multiplier ** (attempt - 1))
                logger.info(f"Retrying {error_context.operation} in {sleep_time:.2f}s (attempt {attempt + 1}/{max_attempts})")
                time.sleep(sleep_time)
            
            try:
                # This is a placeholder - in real implementation, you would
                # re-execute the failed operation here
                logger.info(f"Retry attempt {attempt + 1} for {error_context.operation}")
                
                # Simulate retry logic
                if self._simulate_retry_success(error_context, attempt):
                    error_context.recovery_attempts = attempt + 1
                    error_context.resolved = True
                    logger.info(f"Recovery successful for {error_context.operation} after {attempt + 1} attempts")
                    return True
                
            except Exception as retry_error:
                logger.warning(f"Retry attempt {attempt + 1} failed: {retry_error}")
                error_context.recovery_attempts = attempt + 1
        
        logger.error(f"All retry attempts failed for {error_context.operation}")
        return False
    
    def _simulate_retry_success(self, error_context: ErrorContext, attempt: int) -> bool:
        """Simulate retry success based on error type and attempt number."""
        # This is a simulation - replace with actual retry logic
        success_probability = {
            ErrorType.CONNECTION_ERROR: 0.7,
            ErrorType.TIMEOUT_ERROR: 0.6,
            ErrorType.PROCESSING_ERROR: 0.5,
            ErrorType.EXTERNAL_SERVICE_ERROR: 0.4
        }
        
        base_probability = success_probability.get(error_context.error_type, 0.3)
        # Increase probability with each attempt
        adjusted_probability = min(0.9, base_probability + (attempt * 0.1))
        
        return random.random() < adjusted_probability
    
    def _handle_circuit_breaker(self, error_context: ErrorContext, strategy: RecoveryAction) -> bool:
        """Handle circuit breaker pattern for external services."""
        service_name = error_context.metadata.get('service_name', error_context.component)
        
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name,
                failure_threshold=5,
                recovery_timeout=60
            )
        
        circuit = self.circuit_breakers[service_name]
        
        if circuit.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (datetime.now() - circuit.last_failure_time).seconds >= circuit.recovery_timeout:
                circuit.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker for {service_name} moved to HALF_OPEN")
            else:
                logger.warning(f"Circuit breaker for {service_name} is OPEN - failing fast")
                return False
        
        # Attempt operation
        if circuit.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]:
            success = self._retry_operation(error_context, strategy)
            
            if success:
                circuit.success_count += 1
                circuit.failure_count = 0
                if circuit.state == CircuitState.HALF_OPEN:
                    circuit.state = CircuitState.CLOSED
                    logger.info(f"Circuit breaker for {service_name} moved to CLOSED")
                return True
            else:
                circuit.failure_count += 1
                circuit.last_failure_time = datetime.now()
                
                if circuit.failure_count >= circuit.failure_threshold:
                    circuit.state = CircuitState.OPEN
                    logger.warning(f"Circuit breaker for {service_name} moved to OPEN")
                
                return False
        
        return False
    
    def _execute_fallback(self, error_context: ErrorContext, strategy: RecoveryAction) -> bool:
        """Execute fallback function if available."""
        if strategy.fallback_function:
            try:
                logger.info(f"Executing fallback for {error_context.operation}")
                result = strategy.fallback_function(error_context)
                error_context.resolved = True
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback function failed: {fallback_error}")
                return False
        else:
            logger.warning(f"No fallback function defined for {error_context.operation}")
            return False
    
    def _graceful_degradation(self, error_context: ErrorContext, strategy: RecoveryAction) -> bool:
        """Implement graceful degradation strategy."""
        logger.info(f"Implementing graceful degradation for {error_context.operation}")
        
        # Reduce system load
        self._reduce_system_load()
        
        # Mark as partially resolved
        error_context.resolved = True
        error_context.metadata['degraded_mode'] = True
        
        return True
    
    def _reduce_system_load(self) -> None:
        """Reduce system load during graceful degradation."""
        # This is a placeholder for load reduction strategies
        logger.info("Reducing system load: limiting concurrent operations")
        
        # Example strategies:
        # - Reduce thread pool size
        # - Increase batch processing intervals
        # - Disable non-essential features
        # - Implement rate limiting
    
    def _store_error(self, error_context: ErrorContext) -> None:
        """Store error context in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO error_contexts 
                    (error_id, timestamp, error_type, severity, component, operation, 
                     error_message, stack_trace, metadata_json, recovery_attempts, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    error_context.error_id,
                    error_context.timestamp.isoformat(),
                    error_context.error_type.value,
                    error_context.severity.value,
                    error_context.component,
                    error_context.operation,
                    error_context.error_message,
                    error_context.stack_trace,
                    json.dumps(error_context.metadata),
                    error_context.recovery_attempts,
                    error_context.resolved
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store error context: {e}")
    
    def _check_alert_conditions(self, error_context: ErrorContext) -> None:
        """Check if alert conditions are met and send alerts."""
        thresholds = self.alert_config['alert_thresholds']
        
        # Check error rate
        recent_errors_count = len([e for e in self.recent_errors 
                                 if (datetime.now() - e.timestamp).seconds <= 3600])
        
        if recent_errors_count >= thresholds['error_rate_per_hour']:
            self._send_alert(f"High error rate: {recent_errors_count} errors in the last hour", 
                           ErrorSeverity.HIGH)
        
        # Check critical errors
        if error_context.severity == ErrorSeverity.CRITICAL:
            critical_errors_count = len([e for e in self.recent_errors 
                                       if e.severity == ErrorSeverity.CRITICAL and 
                                       (datetime.now() - e.timestamp).seconds <= 3600])
            
            if critical_errors_count >= thresholds['critical_errors_per_hour']:
                self._send_alert(f"Critical error threshold exceeded: {critical_errors_count} critical errors", 
                               ErrorSeverity.CRITICAL)
        
        # Check consecutive failures
        consecutive_failures = 0
        for error in reversed(list(self.recent_errors)):
            if not error.resolved:
                consecutive_failures += 1
            else:
                break
        
        if consecutive_failures >= thresholds['consecutive_failures']:
            self._send_alert(f"Consecutive failures detected: {consecutive_failures} unresolved errors", 
                           ErrorSeverity.HIGH)
    
    def _send_alert(self, message: str, severity: ErrorSeverity) -> None:
        """Send alert notification."""
        logger.warning(f"ALERT ({severity.value.upper()}): {message}")
        
        # Email alert
        if self.alert_config['email_enabled']:
            self._send_email_alert(message, severity)
        
        # Webhook alert
        if self.alert_config['webhook_enabled']:
            self._send_webhook_alert(message, severity)
    
    def _send_email_alert(self, message: str, severity: ErrorSeverity) -> None:
        """Send email alert."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.alert_config['email_from']
            msg['To'] = ', '.join(self.alert_config['email_to'])
            msg['Subject'] = f"Pipeline Alert - {severity.value.upper()}"
            
            body = f"""
            Pipeline Alert
            
            Severity: {severity.value.upper()}
            Message: {message}
            Timestamp: {datetime.now().isoformat()}
            
            Please check the pipeline status and take appropriate action.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.alert_config['smtp_server'], self.alert_config['smtp_port'])
            server.starttls()
            text = msg.as_string()
            server.sendmail(self.alert_config['email_from'], self.alert_config['email_to'], text)
            server.quit()
            
            logger.info("Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_webhook_alert(self, message: str, severity: ErrorSeverity) -> None:
        """Send webhook alert."""
        try:
            webhook_url = self.alert_config['webhook_url']
            if not webhook_url:
                return
            
            payload = {
                'severity': severity.value,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'source': 'data_pipeline'
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Webhook alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def _update_health_status(self, component: str, has_error: bool) -> None:
        """Update health status for a component."""
        current_time = datetime.now()
        
        if component not in self.health_status:
            self.health_status[component] = PipelineHealth(
                component=component,
                status="healthy",
                last_check=current_time,
                error_rate=0.0,
                response_time=0.0,
                details={}
            )
        
        health = self.health_status[component]
        health.last_check = current_time
        
        # Calculate error rate (errors per hour)
        component_errors = [e for e in self.recent_errors 
                          if e.component == component and 
                          (current_time - e.timestamp).seconds <= 3600]
        
        health.error_rate = len(component_errors)
        
        # Determine status
        if health.error_rate == 0:
            health.status = "healthy"
        elif health.error_rate <= 5:
            health.status = "degraded"
        else:
            health.status = "unhealthy"
        
        # Store in database
        self._store_health_status(health)
    
    def _store_health_status(self, health: PipelineHealth) -> None:
        """Store health status in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO health_status 
                    (component, status, last_check, error_rate, response_time, details_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    health.component,
                    health.status,
                    health.last_check.isoformat(),
                    health.error_rate,
                    health.response_time,
                    json.dumps(health.details)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store health status: {e}")
    
    def _start_health_monitor(self) -> None:
        """Start background health monitoring thread."""
        def monitor_health():
            while True:
                try:
                    self._perform_health_checks()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_health, daemon=True)
        monitor_thread.start()
        logger.info("Health monitoring thread started")
    
    def _perform_health_checks(self) -> None:
        """Perform periodic health checks."""
        current_time = datetime.now()
        
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        # Update system health
        system_health = PipelineHealth(
            component="system",
            status="healthy",
            last_check=current_time,
            error_rate=0.0,
            response_time=0.0,
            details={
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent
            }
        )
        
        # Determine system status
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            system_health.status = "unhealthy"
        elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 80:
            system_health.status = "degraded"
        
        self.health_status["system"] = system_health
        self._store_health_status(system_health)
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with error statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                
                # Get error counts by type
                cursor.execute("""
                    SELECT error_type, COUNT(*) as count
                    FROM error_contexts 
                    WHERE timestamp >= ?
                    GROUP BY error_type
                """, (since_time,))
                
                error_counts = dict(cursor.fetchall())
                
                # Get error counts by severity
                cursor.execute("""
                    SELECT severity, COUNT(*) as count
                    FROM error_contexts 
                    WHERE timestamp >= ?
                    GROUP BY severity
                """, (since_time,))
                
                severity_counts = dict(cursor.fetchall())
                
                # Get resolution rate
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_errors,
                        SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) as resolved_errors
                    FROM error_contexts 
                    WHERE timestamp >= ?
                """, (since_time,))
                
                total_errors, resolved_errors = cursor.fetchone()
                resolution_rate = (resolved_errors / total_errors) if total_errors > 0 else 0
                
                return {
                    'time_period_hours': hours,
                    'total_errors': total_errors,
                    'resolved_errors': resolved_errors,
                    'resolution_rate': resolution_rate,
                    'error_counts_by_type': error_counts,
                    'error_counts_by_severity': severity_counts,
                    'active_circuit_breakers': len([cb for cb in self.circuit_breakers.values() 
                                                  if cb.state == CircuitState.OPEN])
                }
                
        except Exception as e:
            logger.error(f"Failed to get error statistics: {e}")
            return {}
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get current health report for all components.
        
        Returns:
            Dictionary with health status for all components
        """
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        unhealthy_count = 0
        degraded_count = 0
        
        for component, health in self.health_status.items():
            health_report['components'][component] = {
                'status': health.status,
                'last_check': health.last_check.isoformat(),
                'error_rate': health.error_rate,
                'response_time': health.response_time,
                'details': health.details
            }
            
            if health.status == 'unhealthy':
                unhealthy_count += 1
            elif health.status == 'degraded':
                degraded_count += 1
        
        # Determine overall status
        if unhealthy_count > 0:
            health_report['overall_status'] = 'unhealthy'
        elif degraded_count > 0:
            health_report['overall_status'] = 'degraded'
        
        return health_report
    
    def reset_circuit_breaker(self, service_name: str) -> bool:
        """Manually reset a circuit breaker.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if reset successful, False otherwise
        """
        if service_name in self.circuit_breakers:
            circuit = self.circuit_breakers[service_name]
            circuit.state = CircuitState.CLOSED
            circuit.failure_count = 0
            circuit.success_count = 0
            circuit.last_failure_time = None
            
            logger.info(f"Circuit breaker for {service_name} manually reset")
            return True
        
        logger.warning(f"Circuit breaker for {service_name} not found")
        return False

# Decorator for automatic error handling
def handle_pipeline_errors(component: str, operation: str = None, 
                         error_handler: DataPipelineErrorHandler = None):
    """Decorator for automatic error handling in pipeline functions.
    
    Args:
        component: Component name
        operation: Operation name (defaults to function name)
        error_handler: Error handler instance
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__
            handler = error_handler or getattr(wrapper, '_error_handler', None)
            
            if not handler:
                # Create default handler if none provided
                handler = DataPipelineErrorHandler()
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                metadata = {
                    'function_name': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                
                recovery_success = handler.handle_error(e, component, op_name, metadata)
                
                if not recovery_success:
                    raise  # Re-raise if recovery failed
                
                # Return None or default value if recovered
                return None
        
        return wrapper
    return decorator

def main():
    """Main function for testing the DataPipelineErrorHandler."""
    print("=" * 60)
    print("Mental Health Data Pipeline - Error Handler")
    print("=" * 60)
    
    try:
        # Initialize error handler
        error_handler = DataPipelineErrorHandler()
        
        print("\nTesting error handling scenarios...")
        
        # Test different error types
        test_errors = [
            (ConnectionError("Database connection failed"), "database", "connect"),
            (ValueError("Invalid data format"), "validator", "validate_data"),
            (TimeoutError("Operation timed out"), "processor", "process_batch"),
            (PermissionError("Access denied"), "file_handler", "read_file"),
            (Exception("Unknown error occurred"), "unknown_component", "unknown_operation")
        ]
        
        for i, (error, component, operation) in enumerate(test_errors, 1):
            print(f"\n{i}. Testing {type(error).__name__}: {error}")
            
            metadata = {'test_case': i, 'error_type': type(error).__name__}
            recovery_success = error_handler.handle_error(error, component, operation, metadata)
            
            print(f"   Recovery: {'SUCCESS' if recovery_success else 'FAILED'}")
        
        # Get error statistics
        print("\nError Statistics (last 24 hours):")
        stats = error_handler.get_error_statistics(24)
        print(f"  Total errors: {stats.get('total_errors', 0)}")
        print(f"  Resolution rate: {stats.get('resolution_rate', 0):.1%}")
        
        if stats.get('error_counts_by_type'):
            print("  Errors by type:")
            for error_type, count in stats['error_counts_by_type'].items():
                print(f"    {error_type}: {count}")
        
        # Get health report
        print("\nHealth Report:")
        health_report = error_handler.get_health_report()
        print(f"  Overall status: {health_report['overall_status']}")
        
        if health_report['components']:
            print("  Component status:")
            for component, status in health_report['components'].items():
                print(f"    {component}: {status['status']} (error rate: {status['error_rate']})")
        
        # Test decorator
        print("\nTesting error handling decorator...")
        
        @handle_pipeline_errors("test_component", "test_operation", error_handler)
        def test_function():
            raise ValueError("Test error for decorator")
        
        try:
            test_function()
            print("  Decorator test: Function completed (error was handled)")
        except Exception as e:
            print(f"  Decorator test: Exception not handled - {e}")
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        print(f"Testing failed: {e}")

if __name__ == "__main__":
    main()