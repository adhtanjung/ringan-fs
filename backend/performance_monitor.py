#!/usr/bin/env python3
"""
Performance Monitor for Mental Health Data Pipeline

This module implements comprehensive performance monitoring and optimization:
- Real-time performance metrics tracking
- Import operation performance analysis
- Vector database operation monitoring
- Resource utilization tracking
- Performance bottleneck detection
- Optimization recommendations
- Historical performance trends
- Performance alerting and reporting

Author: Mental Health Data Pipeline Team
Date: January 2025
"""

import logging
import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import sqlite3
from pathlib import Path
import psutil
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import functools
import gc
import sys
import tracemalloc
import cProfile
import pstats
import io
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OperationType(Enum):
    """Types of operations to monitor"""
    DATA_IMPORT = "data_import"
    DATA_EXPORT = "data_export"
    DATA_VALIDATION = "data_validation"
    DATA_CLEANING = "data_cleaning"
    DATA_TRANSFORMATION = "data_transformation"
    VECTOR_GENERATION = "vector_generation"
    VECTOR_SEARCH = "vector_search"
    VECTOR_UPDATE = "vector_update"
    DATABASE_QUERY = "database_query"
    DATABASE_INSERT = "database_insert"
    DATABASE_UPDATE = "database_update"
    FILE_IO = "file_io"
    NETWORK_REQUEST = "network_request"
    COMPUTATION = "computation"
    OTHER = "other"

class PerformanceLevel(Enum):
    """Performance levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class ResourceType(Enum):
    """System resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    operation_id: str
    operation_type: OperationType
    component: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_io_mb: float
    network_io_mb: float
    records_processed: int
    throughput_records_per_second: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceSnapshot:
    """System resource snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int
    open_files: int

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    timestamp: datetime
    alert_type: str
    severity: str
    component: str
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    resolved: bool = False

@dataclass
class PerformanceTrend:
    """Performance trend analysis"""
    metric_name: str
    time_period: str
    trend_direction: str  # improving, degrading, stable
    change_percentage: float
    current_average: float
    previous_average: float
    confidence_score: float

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    recommendation_id: str
    component: str
    issue_description: str
    recommendation: str
    expected_improvement: str
    priority: str
    implementation_effort: str

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for data pipeline.
    
    Features:
    - Real-time performance metrics tracking
    - Resource utilization monitoring
    - Performance bottleneck detection
    - Optimization recommendations
    - Historical trend analysis
    - Performance alerting
    - Profiling and benchmarking
    """
    
    def __init__(self, db_path: str = "performance_monitor.db", 
                 monitoring_interval: int = 30):
        """
        Initialize the PerformanceMonitor.
        
        Args:
            db_path: Path to SQLite database for performance data
            monitoring_interval: Interval in seconds for resource monitoring
        """
        self.db_path = db_path
        self.monitoring_interval = monitoring_interval
        self.metrics_history: List[PerformanceMetric] = []
        self.resource_history: deque = deque(maxlen=1000)
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.performance_thresholds = self._load_default_thresholds()
        self.alerts: List[PerformanceAlert] = []
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitor_thread = None
        
        # Initialize database
        self._init_database()
        
        # Start resource monitoring
        self.start_monitoring()
        
        # Initialize profiling
        self._profiler = None
        self._profiling_active = False
        
        logger.info("PerformanceMonitor initialized")
    
    def _load_default_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load default performance thresholds."""
        return {
            'response_time': {
                'data_import': 30.0,  # seconds
                'vector_generation': 10.0,
                'vector_search': 2.0,
                'database_query': 5.0,
                'file_io': 15.0
            },
            'throughput': {
                'data_import': 100.0,  # records per second
                'vector_generation': 50.0,
                'database_insert': 200.0
            },
            'resource_usage': {
                'cpu_percent': 80.0,
                'memory_percent': 85.0,
                'disk_usage_percent': 90.0
            },
            'error_rate': {
                'max_error_rate': 0.05  # 5%
            }
        }
    
    def _init_database(self) -> None:
        """Initialize SQLite database for performance data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Performance metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation_id TEXT NOT NULL,
                        operation_type TEXT NOT NULL,
                        component TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        duration_seconds REAL NOT NULL,
                        cpu_usage_percent REAL NOT NULL,
                        memory_usage_mb REAL NOT NULL,
                        disk_io_mb REAL NOT NULL,
                        network_io_mb REAL NOT NULL,
                        records_processed INTEGER NOT NULL,
                        throughput_records_per_second REAL NOT NULL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        metadata_json TEXT NOT NULL
                    )
                """)
                
                # Resource snapshots table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS resource_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        memory_available_mb REAL NOT NULL,
                        disk_usage_percent REAL NOT NULL,
                        disk_io_read_mb REAL NOT NULL,
                        disk_io_write_mb REAL NOT NULL,
                        network_sent_mb REAL NOT NULL,
                        network_recv_mb REAL NOT NULL,
                        active_threads INTEGER NOT NULL,
                        open_files INTEGER NOT NULL
                    )
                """)
                
                # Performance alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        component TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        current_value REAL NOT NULL,
                        threshold_value REAL NOT NULL,
                        message TEXT NOT NULL,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(start_time)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_component ON performance_metrics(component)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_operation ON performance_metrics(operation_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_timestamp ON resource_snapshots(timestamp)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def start_monitoring(self) -> None:
        """Start background resource monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        
        def monitor_resources():
            while self._monitoring_active:
                try:
                    self._collect_resource_snapshot()
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    logger.error(f"Resource monitoring error: {e}")
                    time.sleep(self.monitoring_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        self._monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop background resource monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def _collect_resource_snapshot(self) -> None:
        """Collect current system resource snapshot."""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage and I/O
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            # Process information
            process = psutil.Process()
            
            snapshot = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=(disk_usage.used / disk_usage.total) * 100,
                disk_io_read_mb=disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                disk_io_write_mb=disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                network_sent_mb=network_io.bytes_sent / (1024 * 1024) if network_io else 0,
                network_recv_mb=network_io.bytes_recv / (1024 * 1024) if network_io else 0,
                active_threads=threading.active_count(),
                open_files=len(process.open_files())
            )
            
            with self._lock:
                self.resource_history.append(snapshot)
            
            # Store in database
            self._store_resource_snapshot(snapshot)
            
            # Check for alerts
            self._check_resource_alerts(snapshot)
            
        except Exception as e:
            logger.error(f"Failed to collect resource snapshot: {e}")
    
    def _store_resource_snapshot(self, snapshot: ResourceSnapshot) -> None:
        """Store resource snapshot in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO resource_snapshots 
                    (timestamp, cpu_percent, memory_percent, memory_available_mb,
                     disk_usage_percent, disk_io_read_mb, disk_io_write_mb,
                     network_sent_mb, network_recv_mb, active_threads, open_files)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot.timestamp.isoformat(),
                    snapshot.cpu_percent,
                    snapshot.memory_percent,
                    snapshot.memory_available_mb,
                    snapshot.disk_usage_percent,
                    snapshot.disk_io_read_mb,
                    snapshot.disk_io_write_mb,
                    snapshot.network_sent_mb,
                    snapshot.network_recv_mb,
                    snapshot.active_threads,
                    snapshot.open_files
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store resource snapshot: {e}")
    
    @contextmanager
    def track_operation(self, operation_type: OperationType, component: str, 
                       operation_name: str = None, records_count: int = 0,
                       metadata: Dict[str, Any] = None):
        """Context manager for tracking operation performance.
        
        Args:
            operation_type: Type of operation
            component: Component performing the operation
            operation_name: Optional operation name
            records_count: Number of records being processed
            metadata: Additional metadata
        """
        operation_id = f"{component}_{operation_type.value}_{int(time.time())}_{id(threading.current_thread())}"
        
        # Record start state
        start_time = datetime.now()
        start_resources = self._get_current_resources()
        
        with self._lock:
            self.active_operations[operation_id] = {
                'operation_type': operation_type,
                'component': component,
                'operation_name': operation_name,
                'start_time': start_time,
                'start_resources': start_resources,
                'records_count': records_count,
                'metadata': metadata or {}
            }
        
        success = True
        error_message = None
        
        try:
            yield operation_id
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            # Record end state
            end_time = datetime.now()
            end_resources = self._get_current_resources()
            
            # Calculate metrics
            duration = (end_time - start_time).total_seconds()
            throughput = records_count / duration if duration > 0 else 0
            
            # Create performance metric
            metric = PerformanceMetric(
                operation_id=operation_id,
                operation_type=operation_type,
                component=component,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                cpu_usage_percent=end_resources['cpu_percent'] - start_resources['cpu_percent'],
                memory_usage_mb=end_resources['memory_mb'] - start_resources['memory_mb'],
                disk_io_mb=end_resources['disk_io_mb'] - start_resources['disk_io_mb'],
                network_io_mb=end_resources['network_io_mb'] - start_resources['network_io_mb'],
                records_processed=records_count,
                throughput_records_per_second=throughput,
                success=success,
                error_message=error_message,
                metadata=metadata or {}
            )
            
            # Store metric
            self._store_performance_metric(metric)
            
            # Check for performance alerts
            self._check_performance_alerts(metric)
            
            # Clean up active operations
            with self._lock:
                if operation_id in self.active_operations:
                    del self.active_operations[operation_id]
    
    def _get_current_resources(self) -> Dict[str, float]:
        """Get current resource usage."""
        try:
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_mb': memory.used / (1024 * 1024),
                'disk_io_mb': (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024) if disk_io else 0,
                'network_io_mb': (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024) if network_io else 0
            }
        except Exception as e:
            logger.error(f"Failed to get current resources: {e}")
            return {'cpu_percent': 0, 'memory_mb': 0, 'disk_io_mb': 0, 'network_io_mb': 0}
    
    def _store_performance_metric(self, metric: PerformanceMetric) -> None:
        """Store performance metric in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO performance_metrics 
                    (operation_id, operation_type, component, start_time, end_time,
                     duration_seconds, cpu_usage_percent, memory_usage_mb, disk_io_mb,
                     network_io_mb, records_processed, throughput_records_per_second,
                     success, error_message, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.operation_id,
                    metric.operation_type.value,
                    metric.component,
                    metric.start_time.isoformat(),
                    metric.end_time.isoformat(),
                    metric.duration_seconds,
                    metric.cpu_usage_percent,
                    metric.memory_usage_mb,
                    metric.disk_io_mb,
                    metric.network_io_mb,
                    metric.records_processed,
                    metric.throughput_records_per_second,
                    metric.success,
                    metric.error_message,
                    json.dumps(metric.metadata)
                ))
                
                conn.commit()
                
            with self._lock:
                self.metrics_history.append(metric)
                
        except Exception as e:
            logger.error(f"Failed to store performance metric: {e}")
    
    def _check_resource_alerts(self, snapshot: ResourceSnapshot) -> None:
        """Check for resource-based performance alerts."""
        thresholds = self.performance_thresholds['resource_usage']
        
        alerts_to_create = []
        
        # CPU usage alert
        if snapshot.cpu_percent > thresholds['cpu_percent']:
            alerts_to_create.append({
                'alert_type': 'high_cpu_usage',
                'severity': 'high',
                'component': 'system',
                'metric_name': 'cpu_percent',
                'current_value': snapshot.cpu_percent,
                'threshold_value': thresholds['cpu_percent'],
                'message': f"High CPU usage: {snapshot.cpu_percent:.1f}% (threshold: {thresholds['cpu_percent']:.1f}%)"
            })
        
        # Memory usage alert
        if snapshot.memory_percent > thresholds['memory_percent']:
            alerts_to_create.append({
                'alert_type': 'high_memory_usage',
                'severity': 'high',
                'component': 'system',
                'metric_name': 'memory_percent',
                'current_value': snapshot.memory_percent,
                'threshold_value': thresholds['memory_percent'],
                'message': f"High memory usage: {snapshot.memory_percent:.1f}% (threshold: {thresholds['memory_percent']:.1f}%)"
            })
        
        # Disk usage alert
        if snapshot.disk_usage_percent > thresholds['disk_usage_percent']:
            alerts_to_create.append({
                'alert_type': 'high_disk_usage',
                'severity': 'critical',
                'component': 'system',
                'metric_name': 'disk_usage_percent',
                'current_value': snapshot.disk_usage_percent,
                'threshold_value': thresholds['disk_usage_percent'],
                'message': f"High disk usage: {snapshot.disk_usage_percent:.1f}% (threshold: {thresholds['disk_usage_percent']:.1f}%)"
            })
        
        # Create alerts
        for alert_data in alerts_to_create:
            self._create_alert(**alert_data)
    
    def _check_performance_alerts(self, metric: PerformanceMetric) -> None:
        """Check for operation performance alerts."""
        operation_type = metric.operation_type.value
        
        # Response time alerts
        if operation_type in self.performance_thresholds['response_time']:
            threshold = self.performance_thresholds['response_time'][operation_type]
            if metric.duration_seconds > threshold:
                self._create_alert(
                    alert_type='slow_operation',
                    severity='medium',
                    component=metric.component,
                    metric_name='duration_seconds',
                    current_value=metric.duration_seconds,
                    threshold_value=threshold,
                    message=f"Slow {operation_type}: {metric.duration_seconds:.2f}s (threshold: {threshold:.2f}s)"
                )
        
        # Throughput alerts
        if operation_type in self.performance_thresholds['throughput']:
            threshold = self.performance_thresholds['throughput'][operation_type]
            if metric.throughput_records_per_second < threshold:
                self._create_alert(
                    alert_type='low_throughput',
                    severity='medium',
                    component=metric.component,
                    metric_name='throughput_records_per_second',
                    current_value=metric.throughput_records_per_second,
                    threshold_value=threshold,
                    message=f"Low throughput for {operation_type}: {metric.throughput_records_per_second:.1f} rec/s (threshold: {threshold:.1f} rec/s)"
                )
    
    def _create_alert(self, alert_type: str, severity: str, component: str,
                     metric_name: str, current_value: float, threshold_value: float,
                     message: str) -> None:
        """Create a performance alert."""
        alert_id = f"{alert_type}_{component}_{int(time.time())}"
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            component=component,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            message=message
        )
        
        # Store alert
        self._store_alert(alert)
        
        # Log alert
        logger.warning(f"PERFORMANCE ALERT ({severity.upper()}): {message}")
    
    def _store_alert(self, alert: PerformanceAlert) -> None:
        """Store performance alert in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO performance_alerts 
                    (alert_id, timestamp, alert_type, severity, component,
                     metric_name, current_value, threshold_value, message, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.timestamp.isoformat(),
                    alert.alert_type,
                    alert.severity,
                    alert.component,
                    alert.metric_name,
                    alert.current_value,
                    alert.threshold_value,
                    alert.message,
                    alert.resolved
                ))
                
                conn.commit()
                
            with self._lock:
                self.alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with performance report
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                
                # Get operation statistics
                cursor.execute("""
                    SELECT 
                        operation_type,
                        component,
                        COUNT(*) as operation_count,
                        AVG(duration_seconds) as avg_duration,
                        MIN(duration_seconds) as min_duration,
                        MAX(duration_seconds) as max_duration,
                        AVG(throughput_records_per_second) as avg_throughput,
                        SUM(records_processed) as total_records,
                        AVG(cpu_usage_percent) as avg_cpu_usage,
                        AVG(memory_usage_mb) as avg_memory_usage,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_operations,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_operations
                    FROM performance_metrics 
                    WHERE start_time >= ?
                    GROUP BY operation_type, component
                    ORDER BY operation_count DESC
                """, (since_time,))
                
                operation_stats = []
                for row in cursor.fetchall():
                    operation_stats.append({
                        'operation_type': row[0],
                        'component': row[1],
                        'operation_count': row[2],
                        'avg_duration': round(row[3], 3),
                        'min_duration': round(row[4], 3),
                        'max_duration': round(row[5], 3),
                        'avg_throughput': round(row[6], 1),
                        'total_records': row[7],
                        'avg_cpu_usage': round(row[8], 1),
                        'avg_memory_usage': round(row[9], 1),
                        'successful_operations': row[10],
                        'failed_operations': row[11],
                        'success_rate': round(row[10] / (row[10] + row[11]) * 100, 1) if (row[10] + row[11]) > 0 else 0
                    })
                
                # Get resource statistics
                cursor.execute("""
                    SELECT 
                        AVG(cpu_percent) as avg_cpu,
                        MAX(cpu_percent) as max_cpu,
                        AVG(memory_percent) as avg_memory,
                        MAX(memory_percent) as max_memory,
                        AVG(disk_usage_percent) as avg_disk,
                        MAX(disk_usage_percent) as max_disk,
                        AVG(active_threads) as avg_threads,
                        MAX(active_threads) as max_threads
                    FROM resource_snapshots 
                    WHERE timestamp >= ?
                """, (since_time,))
                
                resource_row = cursor.fetchone()
                resource_stats = {
                    'avg_cpu_percent': round(resource_row[0] or 0, 1),
                    'max_cpu_percent': round(resource_row[1] or 0, 1),
                    'avg_memory_percent': round(resource_row[2] or 0, 1),
                    'max_memory_percent': round(resource_row[3] or 0, 1),
                    'avg_disk_percent': round(resource_row[4] or 0, 1),
                    'max_disk_percent': round(resource_row[5] or 0, 1),
                    'avg_active_threads': round(resource_row[6] or 0, 1),
                    'max_active_threads': int(resource_row[7] or 0)
                }
                
                # Get alert statistics
                cursor.execute("""
                    SELECT 
                        alert_type,
                        severity,
                        COUNT(*) as alert_count,
                        SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) as resolved_count
                    FROM performance_alerts 
                    WHERE timestamp >= ?
                    GROUP BY alert_type, severity
                    ORDER BY alert_count DESC
                """, (since_time,))
                
                alert_stats = []
                for row in cursor.fetchall():
                    alert_stats.append({
                        'alert_type': row[0],
                        'severity': row[1],
                        'alert_count': row[2],
                        'resolved_count': row[3],
                        'resolution_rate': round(row[3] / row[2] * 100, 1) if row[2] > 0 else 0
                    })
                
                # Generate optimization recommendations
                recommendations = self._generate_optimization_recommendations(operation_stats, resource_stats)
                
                # Calculate overall performance level
                overall_performance = self._calculate_overall_performance(operation_stats, resource_stats, alert_stats)
                
                return {
                    'report_timestamp': datetime.now().isoformat(),
                    'time_period_hours': hours,
                    'overall_performance_level': overall_performance,
                    'operation_statistics': operation_stats,
                    'resource_statistics': resource_stats,
                    'alert_statistics': alert_stats,
                    'optimization_recommendations': recommendations,
                    'active_operations': len(self.active_operations),
                    'total_alerts': len(alert_stats)
                }
                
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {}
    
    def _generate_optimization_recommendations(self, operation_stats: List[Dict], 
                                             resource_stats: Dict) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on performance data."""
        recommendations = []
        
        # Check for slow operations
        for op_stat in operation_stats:
            if op_stat['avg_duration'] > 10.0:  # Operations taking more than 10 seconds
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"slow_op_{op_stat['operation_type']}_{op_stat['component']}",
                    component=op_stat['component'],
                    issue_description=f"Slow {op_stat['operation_type']} operations (avg: {op_stat['avg_duration']:.2f}s)",
                    recommendation="Consider optimizing database queries, adding indexes, or implementing caching",
                    expected_improvement="20-50% reduction in response time",
                    priority="high",
                    implementation_effort="medium"
                ))
        
        # Check for low throughput
        for op_stat in operation_stats:
            if op_stat['avg_throughput'] < 10.0 and op_stat['total_records'] > 100:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"low_throughput_{op_stat['operation_type']}_{op_stat['component']}",
                    component=op_stat['component'],
                    issue_description=f"Low throughput for {op_stat['operation_type']} (avg: {op_stat['avg_throughput']:.1f} rec/s)",
                    recommendation="Implement batch processing, parallel processing, or optimize data structures",
                    expected_improvement="2-5x improvement in throughput",
                    priority="medium",
                    implementation_effort="high"
                ))
        
        # Check for high resource usage
        if resource_stats['avg_cpu_percent'] > 70:
            recommendations.append(OptimizationRecommendation(
                recommendation_id="high_cpu_usage",
                component="system",
                issue_description=f"High average CPU usage ({resource_stats['avg_cpu_percent']:.1f}%)",
                recommendation="Profile CPU-intensive operations, optimize algorithms, or scale horizontally",
                expected_improvement="30-50% reduction in CPU usage",
                priority="high",
                implementation_effort="medium"
            ))
        
        if resource_stats['avg_memory_percent'] > 80:
            recommendations.append(OptimizationRecommendation(
                recommendation_id="high_memory_usage",
                component="system",
                issue_description=f"High average memory usage ({resource_stats['avg_memory_percent']:.1f}%)",
                recommendation="Implement memory pooling, optimize data structures, or increase available memory",
                expected_improvement="20-40% reduction in memory usage",
                priority="high",
                implementation_effort="medium"
            ))
        
        # Check for high error rates
        for op_stat in operation_stats:
            if op_stat['success_rate'] < 95.0 and op_stat['operation_count'] > 10:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"high_error_rate_{op_stat['operation_type']}_{op_stat['component']}",
                    component=op_stat['component'],
                    issue_description=f"High error rate for {op_stat['operation_type']} ({100 - op_stat['success_rate']:.1f}%)",
                    recommendation="Implement better error handling, input validation, and retry mechanisms",
                    expected_improvement="Reduce error rate to <2%",
                    priority="critical",
                    implementation_effort="medium"
                ))
        
        return recommendations
    
    def _calculate_overall_performance(self, operation_stats: List[Dict], 
                                     resource_stats: Dict, alert_stats: List[Dict]) -> PerformanceLevel:
        """Calculate overall performance level."""
        score = 100  # Start with perfect score
        
        # Deduct points for slow operations
        for op_stat in operation_stats:
            if op_stat['avg_duration'] > 10.0:
                score -= 10
            elif op_stat['avg_duration'] > 5.0:
                score -= 5
        
        # Deduct points for low success rates
        for op_stat in operation_stats:
            if op_stat['success_rate'] < 90.0:
                score -= 15
            elif op_stat['success_rate'] < 95.0:
                score -= 10
        
        # Deduct points for high resource usage
        if resource_stats['avg_cpu_percent'] > 80:
            score -= 15
        elif resource_stats['avg_cpu_percent'] > 60:
            score -= 10
        
        if resource_stats['avg_memory_percent'] > 85:
            score -= 15
        elif resource_stats['avg_memory_percent'] > 70:
            score -= 10
        
        # Deduct points for alerts
        total_alerts = sum(alert['alert_count'] for alert in alert_stats)
        if total_alerts > 10:
            score -= 20
        elif total_alerts > 5:
            score -= 10
        
        # Determine performance level
        if score >= 90:
            return PerformanceLevel.EXCELLENT
        elif score >= 75:
            return PerformanceLevel.GOOD
        elif score >= 60:
            return PerformanceLevel.FAIR
        elif score >= 40:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    def start_profiling(self, output_file: str = "performance_profile.prof") -> None:
        """Start code profiling.
        
        Args:
            output_file: Output file for profiling results
        """
        if self._profiling_active:
            logger.warning("Profiling is already active")
            return
        
        self._profiler = cProfile.Profile()
        self._profiler.enable()
        self._profiling_active = True
        self._profile_output_file = output_file
        
        logger.info(f"Code profiling started, output will be saved to {output_file}")
    
    def stop_profiling(self) -> str:
        """Stop code profiling and return results.
        
        Returns:
            String with profiling results
        """
        if not self._profiling_active or not self._profiler:
            logger.warning("Profiling is not active")
            return ""
        
        self._profiler.disable()
        self._profiling_active = False
        
        # Save to file
        self._profiler.dump_stats(self._profile_output_file)
        
        # Generate text report
        s = io.StringIO()
        ps = pstats.Stats(self._profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        results = s.getvalue()
        logger.info(f"Code profiling stopped, results saved to {self._profile_output_file}")
        
        return results
    
    def benchmark_operation(self, operation_func: Callable, *args, 
                          iterations: int = 10, **kwargs) -> Dict[str, Any]:
        """Benchmark a specific operation.
        
        Args:
            operation_func: Function to benchmark
            iterations: Number of iterations to run
            *args, **kwargs: Arguments for the function
            
        Returns:
            Dictionary with benchmark results
        """
        logger.info(f"Benchmarking {operation_func.__name__} with {iterations} iterations")
        
        execution_times = []
        memory_usage = []
        success_count = 0
        
        for i in range(iterations):
            # Measure memory before
            gc.collect()  # Force garbage collection
            memory_before = psutil.Process().memory_info().rss / (1024 * 1024)
            
            # Measure execution time
            start_time = time.time()
            
            try:
                result = operation_func(*args, **kwargs)
                success_count += 1
            except Exception as e:
                logger.warning(f"Benchmark iteration {i+1} failed: {e}")
                continue
            
            end_time = time.time()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # Measure memory after
            memory_after = psutil.Process().memory_info().rss / (1024 * 1024)
            memory_usage.append(memory_after - memory_before)
        
        if not execution_times:
            return {'error': 'All benchmark iterations failed'}
        
        # Calculate statistics
        avg_time = statistics.mean(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        std_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        avg_memory = statistics.mean(memory_usage)
        max_memory = max(memory_usage)
        
        return {
            'function_name': operation_func.__name__,
            'iterations': iterations,
            'successful_iterations': success_count,
            'success_rate': (success_count / iterations) * 100,
            'execution_time': {
                'average_seconds': round(avg_time, 4),
                'minimum_seconds': round(min_time, 4),
                'maximum_seconds': round(max_time, 4),
                'std_deviation': round(std_time, 4)
            },
            'memory_usage': {
                'average_mb': round(avg_memory, 2),
                'maximum_mb': round(max_memory, 2)
            },
            'performance_rating': self._rate_benchmark_performance(avg_time, success_count / iterations)
        }
    
    def _rate_benchmark_performance(self, avg_time: float, success_rate: float) -> str:
        """Rate benchmark performance."""
        if success_rate < 0.9:
            return "poor"
        elif avg_time < 0.1:
            return "excellent"
        elif avg_time < 1.0:
            return "good"
        elif avg_time < 5.0:
            return "fair"
        else:
            return "poor"
    
    def get_active_operations(self) -> List[Dict[str, Any]]:
        """Get list of currently active operations.
        
        Returns:
            List of active operation details
        """
        with self._lock:
            active_ops = []
            current_time = datetime.now()
            
            for op_id, op_data in self.active_operations.items():
                duration = (current_time - op_data['start_time']).total_seconds()
                active_ops.append({
                    'operation_id': op_id,
                    'operation_type': op_data['operation_type'].value,
                    'component': op_data['component'],
                    'operation_name': op_data['operation_name'],
                    'start_time': op_data['start_time'].isoformat(),
                    'duration_seconds': round(duration, 2),
                    'records_count': op_data['records_count'],
                    'metadata': op_data['metadata']
                })
            
            return sorted(active_ops, key=lambda x: x['duration_seconds'], reverse=True)
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Clean up old performance data.
        
        Args:
            days: Number of days of data to keep
        """
        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old metrics
                cursor.execute("DELETE FROM performance_metrics WHERE start_time < ?", (cutoff_time,))
                metrics_deleted = cursor.rowcount
                
                # Clean up old resource snapshots
                cursor.execute("DELETE FROM resource_snapshots WHERE timestamp < ?", (cutoff_time,))
                snapshots_deleted = cursor.rowcount
                
                # Clean up old resolved alerts
                cursor.execute("DELETE FROM performance_alerts WHERE timestamp < ? AND resolved = 1", (cutoff_time,))
                alerts_deleted = cursor.rowcount
                
                conn.commit()
                
                # Vacuum database to reclaim space
                cursor.execute("VACUUM")
                
            logger.info(f"Cleaned up old data: {metrics_deleted} metrics, {snapshots_deleted} snapshots, {alerts_deleted} alerts")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

# Decorator for automatic performance tracking
def track_performance(operation_type: OperationType, component: str = None, 
                     records_count: int = 0, monitor: PerformanceMonitor = None):
    """Decorator for automatic performance tracking.
    
    Args:
        operation_type: Type of operation
        component: Component name (defaults to module name)
        records_count: Number of records being processed
        monitor: Performance monitor instance
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            comp_name = component or func.__module__.split('.')[-1]
            perf_monitor = monitor or getattr(wrapper, '_performance_monitor', None)
            
            if not perf_monitor:
                # Create default monitor if none provided
                perf_monitor = PerformanceMonitor()
            
            with perf_monitor.track_operation(
                operation_type=operation_type,
                component=comp_name,
                operation_name=func.__name__,
                records_count=records_count,
                metadata={'function_name': func.__name__}
            ):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def main():
    """Main function for testing the PerformanceMonitor."""
    print("=" * 60)
    print("Mental Health Data Pipeline - Performance Monitor")
    print("=" * 60)
    
    try:
        # Initialize performance monitor
        monitor = PerformanceMonitor(monitoring_interval=5)  # Check every 5 seconds for testing
        
        print("\nTesting performance monitoring...")
        
        # Test operation tracking
        print("\n1. Testing operation tracking:")
        
        with monitor.track_operation(
            operation_type=OperationType.DATA_IMPORT,
            component="test_importer",
            operation_name="import_test_data",
            records_count=1000,
            metadata={'file_type': 'excel', 'test_mode': True}
        ):
            # Simulate some work
            time.sleep(2)
            # Simulate processing records
            for i in range(1000):
                if i % 100 == 0:
                    time.sleep(0.01)  # Simulate processing time
        
        print("   ✓ Data import operation tracked")
        
        # Test vector operation
        with monitor.track_operation(
            operation_type=OperationType.VECTOR_GENERATION,
            component="test_vectorizer",
            operation_name="generate_embeddings",
            records_count=500
        ):
            time.sleep(1.5)
        
        print("   ✓ Vector generation operation tracked")
        
        # Test decorator
        print("\n2. Testing performance decorator:")
        
        @track_performance(OperationType.DATA_VALIDATION, "test_validator", 100, monitor)
        def validate_data():
            time.sleep(1)
            return "validation_complete"
        
        result = validate_data()
        print(f"   ✓ Decorated function executed: {result}")
        
        # Test benchmarking
        print("\n3. Testing benchmarking:")
        
        def test_function(n):
            return sum(range(n))
        
        benchmark_results = monitor.benchmark_operation(test_function, 10000, iterations=5)
        print(f"   ✓ Benchmark completed: {benchmark_results['performance_rating']} performance")
        print(f"     Average time: {benchmark_results['execution_time']['average_seconds']:.4f}s")
        
        # Wait a bit for resource monitoring
        print("\n4. Collecting resource data...")
        time.sleep(10)
        
        # Generate performance report
        print("\n5. Generating performance report:")
        report = monitor.get_performance_report(hours=1)
        
        print(f"   Overall performance: {report.get('overall_performance_level', 'unknown')}")
        print(f"   Active operations: {report.get('active_operations', 0)}")
        print(f"   Total operations: {len(report.get('operation_statistics', []))}")
        
        if report.get('operation_statistics'):
            print("   Operation statistics:")
            for op_stat in report['operation_statistics'][:3]:  # Show top 3
                print(f"     {op_stat['operation_type']} ({op_stat['component']}): "
                      f"{op_stat['operation_count']} ops, "
                      f"{op_stat['avg_duration']:.3f}s avg, "
                      f"{op_stat['success_rate']:.1f}% success")
        
        if report.get('resource_statistics'):
            res_stats = report['resource_statistics']
            print(f"   Resource usage: CPU {res_stats['avg_cpu_percent']:.1f}%, "
                  f"Memory {res_stats['avg_memory_percent']:.1f}%, "
                  f"Threads {res_stats['avg_active_threads']:.0f}")
        
        if report.get('optimization_recommendations'):
            print(f"   Optimization recommendations: {len(report['optimization_recommendations'])}")
            for rec in report['optimization_recommendations'][:2]:  # Show top 2
                print(f"     {rec.priority.upper()}: {rec.issue_description}")
        
        # Test active operations
        print("\n6. Testing active operations tracking:")
        
        # Start a long-running operation in background
        def long_operation():
            with monitor.track_operation(
                operation_type=OperationType.COMPUTATION,
                component="background_processor",
                records_count=5000
            ):
                time.sleep(5)
        
        import threading
        bg_thread = threading.Thread(target=long_operation)
        bg_thread.start()
        
        time.sleep(1)  # Let it start
        
        active_ops = monitor.get_active_operations()
        if active_ops:
            print(f"   ✓ Found {len(active_ops)} active operation(s)")
            for op in active_ops:
                print(f"     {op['operation_type']} ({op['component']}): "
                      f"{op['duration_seconds']:.1f}s running")
        
        bg_thread.join()  # Wait for completion
        
        # Test profiling
        print("\n7. Testing code profiling:")
        
        monitor.start_profiling("test_profile.prof")
        
        # Do some work to profile
        for i in range(1000):
            sum(range(100))
        
        profile_results = monitor.stop_profiling()
        print("   ✓ Profiling completed")
        print(f"   Profile summary (first 200 chars): {profile_results[:200]}...")
        
        # Cleanup
        print("\n8. Cleaning up...")
        monitor.stop_monitoring()
        print("   ✓ Monitoring stopped")
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        print(f"Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()