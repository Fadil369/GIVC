"""
ClaimLinc Monitoring Manager
Handles system monitoring, metrics collection, and performance tracking
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from collections import deque
import psutil
import structlog
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import aiohttp
import websockets


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    name: str
    value: float
    labels: Dict[str, str]
    metric_type: str


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    uptime_seconds: float
    timestamp: datetime


class PerformanceMonitor:
    """Monitor system and application performance"""
    
    def __init__(self, monitoring_dir: Path = None):
        self.monitoring_dir = monitoring_dir or Path("./monitoring")
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_buffer = deque(maxlen=10000)
        self.active_monitors = {}
        self.logger = structlog.get_logger("performance_monitor")
        
        # Prometheus metrics
        self.http_requests_total = Counter(
            'claimlinc_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration = Histogram(
            'claimlinc_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        self.active_connections = Gauge(
            'claimlinc_active_connections',
            'Number of active connections'
        )
        
        self.processing_queue_size = Gauge(
            'claimlinc_processing_queue_size',
            'Size of claim processing queue'
        )
        
        self.claims_processed_total = Counter(
            'claimlinc_claims_processed_total',
            'Total claims processed',
            ['payer', 'status']
        )
        
        self.validation_errors_total = Counter(
            'claimlinc_validation_errors_total',
            'Total validation errors',
            ['error_type']
        )
        
        self.automation_success_rate = Gauge(
            'claimlinc_automation_success_rate',
            'Automation success rate',
            ['payer']
        )
    
    async def start_monitoring(self):
        """Start all monitoring processes"""
        try:
            # Start Prometheus metrics server
            start_http_server(8001)
            self.logger.info("Prometheus metrics server started on port 8001")
            
            # Start system metrics collection
            asyncio.create_task(self._collect_system_metrics())
            
            # Start application metrics collection
            asyncio.create_task(self._collect_application_metrics())
            
            # Start health checks
            asyncio.create_task(self._run_health_checks())
            
            # Start metrics export
            asyncio.create_task(self._export_metrics())
            
            self.logger.info("Performance monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            raise
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        while True:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                metrics = SystemMetrics(
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    disk_usage=disk.percent,
                    network_io={
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv,
                        'packets_sent': network.packets_sent,
                        'packets_recv': network.packets_recv
                    },
                    process_count=len(psutil.pids()),
                    uptime_seconds=time.time() - psutil.boot_time(),
                    timestamp=datetime.now()
                )
                
                # Store metrics
                metric_point = MetricPoint(
                    timestamp=metrics.timestamp,
                    name="system_metrics",
                    value=metrics.cpu_usage,  # Store CPU as primary value
                    labels={
                        "memory_usage": str(metrics.memory_usage),
                        "disk_usage": str(metrics.disk_usage),
                        "process_count": str(metrics.process_count)
                    },
                    metric_type="system"
                )
                
                self.metrics_buffer.append(metric_point)
                
                # Update Prometheus gauges
                self.active_connections.set(metrics.process_count)
                
                # Log if critical thresholds exceeded
                if metrics.cpu_usage > 90:
                    self.logger.warning(f"High CPU usage: {metrics.cpu_usage}%")
                
                if metrics.memory_usage > 90:
                    self.logger.warning(f"High memory usage: {metrics.memory_usage}%")
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(30)
    
    async def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        while True:
            try:
                # Check processing queue sizes
                queue_sizes = self._get_queue_sizes()
                for queue_name, size in queue_sizes.items():
                    self.processing_queue_size.set(size)
                    
                    # Log warnings for large queues
                    if size > 100:
                        self.logger.warning(f"Large queue detected: {queue_name} has {size} items")
                
                # Check automation success rates
                success_rates = self._get_automation_success_rates()
                for payer, rate in success_rates.items():
                    self.automation_success_rate.labels(payer=payer).set(rate)
                    
                    # Log warnings for low success rates
                    if rate < 0.8:  # Less than 80% success rate
                        self.logger.warning(f"Low success rate for {payer}: {rate:.2%}")
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                self.logger.error(f"Error collecting application metrics: {e}")
                await asyncio.sleep(60)
    
    async def _run_health_checks(self):
        """Run periodic health checks"""
        while True:
            try:
                health_status = await self._perform_health_checks()
                
                # Log health status
                overall_status = health_status.get("overall_status", "unknown")
                if overall_status == "critical":
                    self.logger.error(f"Critical health issue detected: {health_status}")
                elif overall_status == "warning":
                    self.logger.warning(f"Health warning: {health_status}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error running health checks: {e}")
                await asyncio.sleep(300)
    
    async def _perform_health_checks(self) -> Dict[str, Any]:
        """Perform comprehensive health checks"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        try:
            # Check API endpoints
            api_health = await self._check_api_health()
            health_status["checks"]["api"] = api_health
            
            # Check database connectivity
            db_health = await self._check_database_health()
            health_status["checks"]["database"] = db_health
            
            # Check external services
            services_health = await self._check_external_services_health()
            health_status["checks"]["external_services"] = services_health
            
            # Check n8n workflows
            workflow_health = await self._check_workflow_health()
            health_status["checks"]["workflows"] = workflow_health
            
            # Determine overall status
            statuses = [check.get("status", "unknown") for check in health_status["checks"].values()]
            if "critical" in statuses:
                health_status["overall_status"] = "critical"
            elif "warning" in statuses:
                health_status["overall_status"] = "warning"
            elif all(status == "healthy" for status in statuses):
                health_status["overall_status"] = "healthy"
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API endpoint health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": response.headers.get("X-Response-Time"),
                            "details": data
                        }
                    else:
                        return {
                            "status": "warning",
                            "http_status": response.status,
                            "message": "API health endpoint returned non-200 status"
                        }
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "message": "Cannot connect to API health endpoint"
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity"""
        # Mock implementation - in real scenario, check actual database
        try:
            # Simulate database check
            await asyncio.sleep(0.1)
            return {
                "status": "healthy",
                "connection_pool_size": 10,
                "active_connections": 3,
                "max_connections": 100
            }
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "message": "Database connectivity failed"
            }
    
    async def _check_external_services_health(self) -> Dict[str, Any]:
        """Check external services health"""
        services = {
            "bupa_portal": {"url": "https://portal.bupa.com.sa", "critical": True},
            "globemed_portal": {"url": "https://portal.globemed.sa", "critical": True},
            "waseel_api": {"url": "https://api.waseel.com", "critical": False}
        }
        
        results = {}
        for service_name, config in services.items():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(config["url"], timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status < 400:
                            results[service_name] = {
                                "status": "healthy",
                                "response_time": response.headers.get("X-Response-Time"),
                                "http_status": response.status
                            }
                        else:
                            status = "critical" if config["critical"] else "warning"
                            results[service_name] = {
                                "status": status,
                                "http_status": response.status,
                                "message": f"Service returned status {response.status}"
                            }
            except Exception as e:
                status = "critical" if config["critical"] else "warning"
                results[service_name] = {
                    "status": status,
                    "error": str(e),
                    "message": f"Cannot connect to {service_name}"
                }
        
        overall_status = "healthy"
        if any(result["status"] == "critical" for result in results.values()):
            overall_status = "critical"
        elif any(result["status"] == "warning" for result in results.values()):
            overall_status = "warning"
        
        return {
            "status": overall_status,
            "services": results
        }
    
    async def _check_workflow_health(self) -> Dict[str, Any]:
        """Check n8n workflow health"""
        try:
            # Mock implementation - in real scenario, check n8n API
            workflows = {
                "bupa_workflow": {"status": "active", "last_execution": "2 minutes ago"},
                "globemed_workflow": {"status": "active", "last_execution": "5 minutes ago"},
                "waseel_workflow": {"status": "active", "last_execution": "1 minute ago"}
            }
            
            inactive_workflows = [name for name, status in workflows.items() 
                                if status["status"] != "active"]
            
            if inactive_workflows:
                return {
                    "status": "warning",
                    "inactive_workflows": inactive_workflows,
                    "workflows": workflows
                }
            else:
                return {
                    "status": "healthy",
                    "workflows": workflows
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "message": "Cannot check workflow health"
            }
    
    async def _export_metrics(self):
        """Export metrics to various formats"""
        while True:
            try:
                # Export to JSON
                await self._export_metrics_json()
                
                # Export to CSV for analysis
                await self._export_metrics_csv()
                
                # Clean old metrics
                await self._cleanup_old_metrics()
                
                await asyncio.sleep(300)  # Export every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error exporting metrics: {e}")
                await asyncio.sleep(300)
    
    async def _export_metrics_json(self):
        """Export metrics to JSON format"""
        try:
            metrics_data = {
                "export_timestamp": datetime.now().isoformat(),
                "metrics": [asdict(metric) for metric in self.metrics_buffer]
            }
            
            export_path = self.monitoring_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_path, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            
            self.logger.info(f"Metrics exported to {export_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics JSON: {e}")
    
    async def _export_metrics_csv(self):
        """Export metrics to CSV format"""
        try:
            import pandas as pd
            
            if not self.metrics_buffer:
                return
            
            data = []
            for metric in self.metrics_buffer:
                row = {
                    'timestamp': metric.timestamp.isoformat(),
                    'name': metric.name,
                    'value': metric.value,
                    'metric_type': metric.metric_type,
                    **{f"label_{k}": v for k, v in metric.labels.items()}
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            export_path = self.monitoring_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(export_path, index=False)
            
            self.logger.info(f"Metrics exported to CSV: {export_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics CSV: {e}")
    
    async def _cleanup_old_metrics(self):
        """Clean up old metric files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for metric_file in self.monitoring_dir.glob("metrics_*.json"):
                if metric_file.stat().st_mtime < cutoff_date.timestamp():
                    metric_file.unlink()
                    self.logger.info(f"Cleaned up old metrics file: {metric_file}")
            
            for csv_file in self.monitoring_dir.glob("metrics_*.csv"):
                if csv_file.stat().st_mtime < cutoff_date.timestamp():
                    csv_file.unlink()
                    self.logger.info(f"Cleaned up old CSV file: {csv_file}")
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {e}")
    
    def _get_queue_sizes(self) -> Dict[str, int]:
        """Get current processing queue sizes"""
        # Mock implementation - in real scenario, check actual queues
        return {
            "claim_normalization": 5,
            "claim_validation": 2,
            "automation_submission": 8,
            "report_generation": 1
        }
    
    def _get_automation_success_rates(self) -> Dict[str, float]:
        """Get automation success rates by payer"""
        # Mock implementation - in real scenario, calculate from actual data
        return {
            "bupa": 0.95,
            "globemed": 0.89,
            "waseel": 0.92
        }
    
    def record_http_request(self, method: str, endpoint: str, duration: float, status: int):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_claim_processed(self, payer: str, status: str):
        """Record claim processing metrics"""
        self.claims_processed_total.labels(payer=payer, status=status).inc()
    
    def record_validation_error(self, error_type: str):
        """Record validation error metrics"""
        self.validation_errors_total.labels(error_type=error_type).inc()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        if not self.metrics_buffer:
            return {"status": "no_data"}
        
        latest_metrics = list(self.metrics_buffer)[-1]
        
        return {
            "timestamp": latest_metrics.timestamp.isoformat(),
            "system_metrics": {
                "cpu_usage": latest_metrics.value,
                "memory_usage": float(latest_metrics.labels.get("memory_usage", "0")),
                "disk_usage": float(latest_metrics.labels.get("disk_usage", "0")),
                "process_count": int(latest_metrics.labels.get("process_count", "0"))
            },
            "queue_sizes": self._get_queue_sizes(),
            "success_rates": self._get_automation_success_rates(),
            "prometheus_endpoint": "http://localhost:8001/metrics"
        }


class MonitoringManager:
    """Main monitoring manager coordinating all monitoring activities"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.logger = structlog.get_logger("monitoring_manager")
        self.monitoring_active = False
    
    async def start_monitoring(self):
        """Start all monitoring services"""
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring already active")
                return
            
            await self.performance_monitor.start_monitoring()
            self.monitoring_active = True
            
            self.logger.info("Monitoring manager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring manager: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop all monitoring services"""
        try:
            self.monitoring_active = False
            self.logger.info("Monitoring manager stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring manager: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "performance_metrics": self.performance_monitor.get_current_metrics(),
            "timestamp": datetime.now().isoformat()
        }


# Utility functions
def get_monitoring_manager() -> MonitoringManager:
    """Get global monitoring manager instance"""
    if not hasattr(get_monitoring_manager, "_instance"):
        get_monitoring_manager._instance = MonitoringManager()
    return get_monitoring_manager._instance


if __name__ == "__main__":
    # Example usage
    async def main():
        manager = MonitoringManager()
        await manager.start_monitoring()
        
        # Simulate some activity
        import random
        
        for i in range(10):
            # Record some metrics
            manager.performance_monitor.record_http_request(
                "POST", "/api/v1/normalize", 
                random.uniform(0.1, 0.5), 
                200 if random.random() > 0.1 else 400
            )
            
            manager.performance_monitor.record_claim_processed(
                random.choice(["bupa", "globemed", "waseel"]),
                "success" if random.random() > 0.05 else "failed"
            )
            
            if random.random() > 0.8:
                manager.performance_monitor.record_validation_error(
                    random.choice(["missing_field", "invalid_format", "data_consistency"])
                )
            
            await asyncio.sleep(5)
        
        # Get current status
        status = manager.get_monitoring_status()
        print(json.dumps(status, indent=2))
        
        await asyncio.sleep(10)
        await manager.stop_monitoring()
    
    # Run the example
    asyncio.run(main())
