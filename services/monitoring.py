"""
Monitoring and Metrics for Ultrathink AI
=========================================
Comprehensive monitoring, metrics collection, and health checking.

Features:
- Prometheus metrics collection
- Health checks for all components
- Performance monitoring
- Error tracking and alerting
- Database connection monitoring

Author: GIVC Platform Team
License: GPL-3.0
"""

import time
import logging
import asyncio
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import asynccontextmanager

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    
    # Mock classes if prometheus not available
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass

logger = logging.getLogger(__name__)

# =========================================================================
# Metrics Definitions
# =========================================================================

# API Metrics
api_requests_total = Counter(
    'ultrathink_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'ultrathink_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# AI Model Metrics
ai_validations_total = Counter(
    'ultrathink_validations_total',
    'Total AI validations performed',
    ['result']
)

ai_validation_duration = Histogram(
    'ultrathink_validation_duration_seconds',
    'AI validation processing time'
)

ai_completions_total = Counter(
    'ultrathink_completions_total',
    'Total smart completions generated'
)

ai_completion_duration = Histogram(
    'ultrathink_completion_duration_seconds',
    'Smart completion processing time'
)

ai_predictions_total = Counter(
    'ultrathink_predictions_total',
    'Total error predictions made',
    ['prediction_result']
)

ai_prediction_duration = Histogram(
    'ultrathink_prediction_duration_seconds',
    'Error prediction processing time'
)

ai_anomalies_total = Counter(
    'ultrathink_anomalies_total',
    'Total anomaly detections',
    ['risk_level', 'anomaly_type']
)

ai_anomaly_duration = Histogram(
    'ultrathink_anomaly_duration_seconds',
    'Anomaly detection processing time'
)

# Security Metrics
security_blocks_total = Counter(
    'ultrathink_security_blocks_total',
    'Total security blocks',
    ['block_type', 'severity']
)

rate_limit_hits_total = Counter(
    'ultrathink_rate_limit_hits_total',
    'Rate limit violations',
    ['limit_type']
)

# System Metrics
active_connections = Gauge(
    'ultrathink_active_connections',
    'Number of active connections'
)

memory_usage_bytes = Gauge(
    'ultrathink_memory_usage_bytes',
    'Memory usage in bytes'
)

cpu_usage_percent = Gauge(
    'ultrathink_cpu_usage_percent',
    'CPU usage percentage'
)

ml_model_accuracy = Gauge(
    'ultrathink_ml_model_accuracy',
    'ML model accuracy',
    ['model_name']
)

# =========================================================================
# Health Check Components
# =========================================================================

@dataclass
class HealthStatus:
    """Health status for a component"""
    name: str
    healthy: bool
    message: str
    response_time_ms: float
    last_check: datetime
    details: Optional[Dict] = None

class HealthChecker:
    """Comprehensive health checking for all components"""
    
    def __init__(self):
        self.checks = {}
        self.last_full_check = None
        
    async def check_all_components(self) -> Dict[str, HealthStatus]:
        """Run health checks for all components"""
        results = {}
        
        # Check database connectivity
        results['database'] = await self._check_database()
        
        # Check Redis connectivity
        results['redis'] = await self._check_redis()
        
        # Check ML models
        results['ml_models'] = await self._check_ml_models()
        
        # Check NPHIES connectivity
        results['nphies'] = await self._check_nphies()
        
        # Check system resources
        results['system'] = await self._check_system_resources()
        
        # Check security middleware
        results['security'] = await self._check_security_middleware()
        
        self.last_full_check = datetime.now()
        self.checks = results
        
        return results
    
    async def _check_database(self) -> HealthStatus:
        """Check database connectivity"""
        start_time = time.time()
        
        try:
            # Import here to avoid circular imports
            from .database_models import SessionLocal
            
            db = SessionLocal()
            try:
                # Simple query to test connectivity
                db.execute("SELECT 1")
                db.commit()
                
                response_time = (time.time() - start_time) * 1000
                return HealthStatus(
                    name="database",
                    healthy=True,
                    message="Database connection successful",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
                
            finally:
                db.close()
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="database",
                healthy=False,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
    
    async def _check_redis(self) -> HealthStatus:
        """Check Redis connectivity"""
        start_time = time.time()
        
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            
            # Test Redis connection
            r.ping()
            
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="redis",
                healthy=True,
                message="Redis connection successful",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="redis",
                healthy=False,
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
    
    async def _check_ml_models(self) -> HealthStatus:
        """Check ML models status"""
        start_time = time.time()
        
        try:
            from .ml_models import diagnosis_model, amount_model, error_model, anomaly_model
            
            models_status = {
                'diagnosis': diagnosis_model.trained,
                'amount': amount_model.trained,
                'error': error_model.trained,
                'anomaly': anomaly_model.trained
            }
            
            healthy_models = sum(models_status.values())
            total_models = len(models_status)
            
            response_time = (time.time() - start_time) * 1000
            
            if healthy_models == total_models:
                message = "All ML models loaded and ready"
                healthy = True
            elif healthy_models > 0:
                message = f"{healthy_models}/{total_models} ML models loaded (using fallbacks)"
                healthy = True
            else:
                message = "No ML models loaded (using rule-based fallbacks)"
                healthy = True  # Still functional with fallbacks
            
            return HealthStatus(
                name="ml_models",
                healthy=healthy,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                details=models_status
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="ml_models",
                healthy=False,
                message=f"ML models check failed: {str(e)}",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
    
    async def _check_nphies(self) -> HealthStatus:
        """Check NPHIES API connectivity"""
        start_time = time.time()
        
        try:
            import httpx
            
            # Test NPHIES endpoint (timeout quickly)
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://HSB.nphies.sa/api/fs/fhir/metadata")
                
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return HealthStatus(
                    name="nphies",
                    healthy=True,
                    message="NPHIES API accessible",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
            else:
                return HealthStatus(
                    name="nphies",
                    healthy=False,
                    message=f"NPHIES API returned status {response.status_code}",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="nphies",
                healthy=False,
                message=f"NPHIES API check failed: {str(e)}",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
    
    async def _check_system_resources(self) -> HealthStatus:
        """Check system resources"""
        start_time = time.time()
        
        try:
            # Get system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            disk = psutil.disk_usage('/')
            
            # Update Prometheus metrics
            memory_usage_bytes.set(memory.used)
            cpu_usage_percent.set(cpu_percent)
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine health based on thresholds
            memory_warning = memory.percent > 80
            cpu_warning = cpu_percent > 80
            disk_warning = disk.percent > 90
            
            warnings = []
            if memory_warning:
                warnings.append(f"High memory usage: {memory.percent:.1f}%")
            if cpu_warning:
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            if disk_warning:
                warnings.append(f"High disk usage: {disk.percent:.1f}%")
            
            healthy = len(warnings) == 0
            message = "System resources normal" if healthy else "; ".join(warnings)
            
            return HealthStatus(
                name="system",
                healthy=healthy,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                details={
                    'memory_percent': memory.percent,
                    'cpu_percent': cpu_percent,
                    'disk_percent': disk.percent
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="system",
                healthy=False,
                message=f"System check failed: {str(e)}",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
    
    async def _check_security_middleware(self) -> HealthStatus:
        """Check security middleware status"""
        start_time = time.time()
        
        try:
            from middleware.security_middleware import rate_limiter, input_validator
            
            # Test rate limiter
            test_identifier = "health_check_test"
            allowed, info = await rate_limiter.check_rate_limit(test_identifier)
            
            # Test input validator
            test_data = {"test": "clean_data"}
            is_valid, errors = await input_validator.validate_request_data(test_data)
            
            response_time = (time.time() - start_time) * 1000
            
            if allowed and is_valid:
                return HealthStatus(
                    name="security",
                    healthy=True,
                    message="Security middleware operational",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
            else:
                return HealthStatus(
                    name="security",
                    healthy=False,
                    message="Security middleware issues detected",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="security",
                healthy=False,
                message=f"Security middleware check failed: {str(e)}",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        if not self.checks:
            return {
                "status": "unknown",
                "message": "No health checks performed yet"
            }
        
        healthy_components = sum(1 for check in self.checks.values() if check.healthy)
        total_components = len(self.checks)
        
        if healthy_components == total_components:
            status = "healthy"
            message = "All components operational"
        elif healthy_components > total_components * 0.5:
            status = "degraded"
            message = f"{healthy_components}/{total_components} components healthy"
        else:
            status = "unhealthy"
            message = f"Only {healthy_components}/{total_components} components healthy"
        
        return {
            "status": status,
            "message": message,
            "components_healthy": healthy_components,
            "components_total": total_components,
            "last_check": self.last_full_check.isoformat() if self.last_full_check else None,
            "components": {name: {
                "healthy": check.healthy,
                "message": check.message,
                "response_time_ms": check.response_time_ms
            } for name, check in self.checks.items()}
        }

# =========================================================================
# Performance Monitoring
# =========================================================================

class PerformanceMonitor:
    """Monitor performance of various operations"""
    
    def __init__(self):
        self.operation_times = {}
        self.error_counts = {}
    
    @asynccontextmanager
    async def measure_operation(self, operation_name: str, labels: Optional[Dict] = None):
        """Context manager to measure operation duration"""
        start_time = time.time()
        
        try:
            yield
            
            # Record successful operation
            duration = time.time() - start_time
            
            if operation_name not in self.operation_times:
                self.operation_times[operation_name] = []
            
            self.operation_times[operation_name].append(duration)
            
            # Update Prometheus metrics based on operation type
            if 'validation' in operation_name:
                ai_validation_duration.observe(duration)
                ai_validations_total.inc(['success'])
            elif 'completion' in operation_name:
                ai_completion_duration.observe(duration)
                ai_completions_total.inc()
            elif 'prediction' in operation_name:
                ai_prediction_duration.observe(duration)
                ai_predictions_total.inc(['success'])
            elif 'anomaly' in operation_name:
                ai_anomaly_duration.observe(duration)
                
        except Exception as e:
            # Record failed operation
            duration = time.time() - start_time
            
            if operation_name not in self.error_counts:
                self.error_counts[operation_name] = 0
            self.error_counts[operation_name] += 1
            
            # Update error metrics
            if 'validation' in operation_name:
                ai_validations_total.inc(['error'])
            elif 'prediction' in operation_name:
                ai_predictions_total.inc(['error'])
            
            logger.error(f"Operation {operation_name} failed after {duration:.3f}s: {e}")
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        
        for operation, times in self.operation_times.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "avg_duration": sum(times) / len(times),
                    "min_duration": min(times),
                    "max_duration": max(times),
                    "error_count": self.error_counts.get(operation, 0)
                }
        
        return stats

# =========================================================================
# Metrics Collection and Export
# =========================================================================

class MetricsCollector:
    """Collect and export metrics"""
    
    def __init__(self):
        self.custom_metrics = {}
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        api_requests_total.inc([method, endpoint, str(status_code)])
        api_request_duration.observe(duration, [method, endpoint])
    
    def record_security_event(self, event_type: str, severity: str):
        """Record security event"""
        security_blocks_total.inc([event_type, severity])
    
    def record_rate_limit_hit(self, limit_type: str):
        """Record rate limit violation"""
        rate_limit_hits_total.inc([limit_type])
    
    def record_anomaly_detection(self, risk_level: str, anomaly_type: str, duration: float):
        """Record anomaly detection"""
        ai_anomalies_total.inc([risk_level, anomaly_type])
        ai_anomaly_duration.observe(duration)
    
    def update_ml_model_accuracy(self, model_name: str, accuracy: float):
        """Update ML model accuracy metric"""
        ml_model_accuracy.set(accuracy, [model_name])
    
    def set_active_connections(self, count: int):
        """Set active connections count"""
        active_connections.set(count)
    
    def get_metrics_export(self) -> str:
        """Export metrics in Prometheus format"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest()
        else:
            return "# Prometheus not available\n"

# =========================================================================
# Alert Manager
# =========================================================================

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5% error rate
            'response_time': 5.0,  # 5 seconds
            'memory_usage': 0.9,  # 90% memory usage
            'anomaly_rate': 0.1,  # 10% anomaly rate
        }
        self.active_alerts = {}
    
    def check_thresholds(self, metrics: Dict[str, float]):
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        for metric, value in metrics.items():
            threshold = self.alert_thresholds.get(metric)
            if threshold and value > threshold:
                alert = {
                    'metric': metric,
                    'value': value,
                    'threshold': threshold,
                    'severity': self._get_severity(metric, value, threshold),
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)
        
        return alerts
    
    def _get_severity(self, metric: str, value: float, threshold: float) -> str:
        """Determine alert severity"""
        ratio = value / threshold
        
        if ratio > 2.0:
            return 'critical'
        elif ratio > 1.5:
            return 'high'
        elif ratio > 1.2:
            return 'medium'
        else:
            return 'low'
    
    async def send_alert(self, alert: Dict):
        """Send alert notification (implement based on your notification system)"""
        logger.warning(f"ALERT: {alert['metric']} = {alert['value']} (threshold: {alert['threshold']})")
        
        # Here you would integrate with:
        # - Email notifications
        # - Slack/Teams webhooks
        # - PagerDuty
        # - SMS alerts
        # etc.

# =========================================================================
# Global Instances
# =========================================================================

health_checker = HealthChecker()
performance_monitor = PerformanceMonitor()
metrics_collector = MetricsCollector()
alert_manager = AlertManager()

# =========================================================================
# Monitoring API Endpoints
# =========================================================================

async def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    await health_checker.check_all_components()
    return health_checker.get_overall_health()

async def get_metrics() -> str:
    """Get metrics in Prometheus format"""
    return metrics_collector.get_metrics_export()

async def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics"""
    return performance_monitor.get_performance_stats()

# Auto-start system monitoring
async def start_background_monitoring():
    """Start background monitoring tasks"""
    while True:
        try:
            # Update system metrics every 30 seconds
            await health_checker._check_system_resources()
            
            # Sleep before next check
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Background monitoring error: {e}")
            await asyncio.sleep(60)  # Wait longer on error

# Initialize background monitoring
try:
    asyncio.create_task(start_background_monitoring())
except RuntimeError:
    # No event loop running, will start when app starts
    pass