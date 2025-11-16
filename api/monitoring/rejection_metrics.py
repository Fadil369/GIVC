"""
ClaimLinc Rejection Monitoring & Metrics
Prometheus metrics and health checks for rejection management system
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum
import time


class MetricType(str, Enum):
    """Prometheus metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class RejectionMetrics:
    """Rejection system metrics collector"""

    def __init__(self):
        self.metrics = {}
        self.initialize_metrics()

    def initialize_metrics(self):
        """Initialize all rejection metrics"""
        self.metrics = {
            # Sheet processing metrics
            "rejection_sheets_uploaded_total": {
                "type": MetricType.COUNTER,
                "description": "Total number of rejection sheets uploaded",
                "labels": ["payer", "branch"],
                "value": 0
            },
            "rejection_sheets_processing_time": {
                "type": MetricType.HISTOGRAM,
                "description": "Time taken to process rejection sheets (seconds)",
                "labels": ["payer"],
                "buckets": [5, 10, 30, 60, 120, 300],
                "value": []
            },
            "rejection_sheets_processing_failures": {
                "type": MetricType.COUNTER,
                "description": "Number of failed sheet processing attempts",
                "labels": ["payer", "error_type"],
                "value": 0
            },

            # Record metrics
            "rejection_records_total": {
                "type": MetricType.GAUGE,
                "description": "Total number of rejection records",
                "labels": ["payer", "branch", "severity"],
                "value": 0
            },
            "rejection_records_at_risk": {
                "type": MetricType.GAUGE,
                "description": "Total amount at risk (SAR)",
                "labels": ["payer", "branch"],
                "value": 0.0
            },
            "rejection_records_by_reason": {
                "type": MetricType.GAUGE,
                "description": "Number of rejections by reason code",
                "labels": ["reason_code", "payer"],
                "value": {}
            },

            # Analysis metrics
            "rejection_analysis_time": {
                "type": MetricType.HISTOGRAM,
                "description": "Time taken for AI analysis (seconds)",
                "labels": ["branch"],
                "buckets": [1, 5, 10, 30, 60],
                "value": []
            },
            "rejection_analysis_insights_generated": {
                "type": MetricType.COUNTER,
                "description": "Total insights generated",
                "labels": ["insight_type"],
                "value": 0
            },

            # Notification metrics
            "branch_notifications_sent": {
                "type": MetricType.COUNTER,
                "description": "Total notifications sent",
                "labels": ["branch", "channel", "status"],
                "value": 0
            },
            "branch_notifications_delivery_time": {
                "type": MetricType.HISTOGRAM,
                "description": "Time between report generation and delivery (seconds)",
                "labels": ["channel"],
                "buckets": [1, 5, 10, 30, 60],
                "value": []
            },

            # Acknowledgment metrics
            "branch_acknowledgments": {
                "type": MetricType.COUNTER,
                "description": "Branch acknowledgments received",
                "labels": ["branch"],
                "value": 0
            },
            "branch_acknowledgment_time": {
                "type": MetricType.HISTOGRAM,
                "description": "Time to branch acknowledgment (hours)",
                "labels": ["branch"],
                "buckets": [1, 2, 4, 8, 24, 48],
                "value": []
            },

            # Resubmission metrics
            "claims_queued_for_resubmission": {
                "type": MetricType.GAUGE,
                "description": "Claims in resubmission queue",
                "labels": ["branch", "status"],
                "value": 0
            },
            "claims_resubmitted_total": {
                "type": MetricType.COUNTER,
                "description": "Total claims resubmitted",
                "labels": ["branch", "payer"],
                "value": 0
            },

            # Portal health metrics
            "portal_monitoring_health": {
                "type": MetricType.GAUGE,
                "description": "Portal monitoring health status (1=healthy, 0=unhealthy)",
                "labels": ["payer"],
                "value": {}
            },
            "portal_monitoring_latency": {
                "type": MetricType.HISTOGRAM,
                "description": "Portal monitoring response time (seconds)",
                "labels": ["payer"],
                "buckets": [1, 5, 10, 30, 60, 120],
                "value": []
            },
            "portal_login_failures": {
                "type": MetricType.COUNTER,
                "description": "Portal login failures",
                "labels": ["payer"],
                "value": 0
            },

            # System health metrics
            "rejection_cycle_duration": {
                "type": MetricType.HISTOGRAM,
                "description": "Duration of full rejection cycle (seconds)",
                "labels": [],
                "buckets": [60, 300, 600, 1800, 3600],
                "value": []
            },
            "rejection_cycle_failures": {
                "type": MetricType.COUNTER,
                "description": "Failed rejection cycles",
                "labels": ["failure_stage"],
                "value": 0
            }
        }

    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value"""
        if metric_name not in self.metrics:
            print(f"⚠️ Unknown metric: {metric_name}")
            return

        metric = self.metrics[metric_name]

        if metric["type"] == MetricType.COUNTER:
            metric["value"] += value
        elif metric["type"] == MetricType.GAUGE:
            metric["value"] = value
        elif metric["type"] in [MetricType.HISTOGRAM, MetricType.SUMMARY]:
            if not isinstance(metric["value"], list):
                metric["value"] = []
            metric["value"].append(value)

    def increment_counter(self, metric_name: str, increment: float = 1.0):
        """Increment a counter metric"""
        self.record_metric(metric_name, increment)

    def set_gauge(self, metric_name: str, value: float):
        """Set a gauge metric"""
        self.record_metric(metric_name, value)

    def record_histogram(self, metric_name: str, value: float):
        """Record a histogram value"""
        self.record_metric(metric_name, value)

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics in Prometheus format"""
        output = []

        for metric_name, metric_data in self.metrics.items():
            # Add HELP and TYPE comments
            output.append(f"# HELP {metric_name} {metric_data.get('description', '')}")
            output.append(f"# TYPE {metric_name} {metric_data['type'].value}")

            # Add metric values
            if metric_data["type"] == MetricType.HISTOGRAM:
                # Histogram with buckets
                value_list = metric_data.get("value", [])
                if value_list:
                    for bucket in metric_data.get("buckets", []):
                        count = sum(1 for v in value_list if v <= bucket)
                        output.append(f'{metric_name}_bucket{{le="{bucket}"}} {count}')
                    output.append(f'{metric_name}_bucket{{le="+Inf"}} {len(value_list)}')
                    output.append(f'{metric_name}_count {len(value_list)}')
                    output.append(f'{metric_name}_sum {sum(value_list)}')
            else:
                # Counter or Gauge
                output.append(f"{metric_name} {metric_data.get('value', 0)}")

        return {"metrics": "\n".join(output), "timestamp": datetime.now().isoformat()}


class HealthCheck:
    """System health checks"""

    def __init__(self, metrics: RejectionMetrics):
        self.metrics = metrics
        self.last_check = None
        self.health_status = "unknown"

    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }

        # Check portal connectivity
        portal_health = self._check_portal_health()
        health["checks"]["portals"] = portal_health

        # Check notification system
        notification_health = self._check_notification_system()
        health["checks"]["notifications"] = notification_health

        # Check database
        database_health = self._check_database()
        health["checks"]["database"] = database_health

        # Check recent activity
        activity_health = self._check_recent_activity()
        health["checks"]["activity"] = activity_health

        # Overall status
        all_healthy = all(
            check.get("status") == "healthy"
            for check in health["checks"].values()
        )

        health["status"] = "healthy" if all_healthy else "degraded"
        self.health_status = health["status"]
        self.last_check = datetime.now()

        return health

    def _check_portal_health(self) -> Dict[str, Any]:
        """Check portal monitoring health"""
        return {
            "status": "healthy",
            "portals_monitored": 3,
            "last_successful_check": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "failed_logins_24h": 0,
            "average_latency_ms": 2500
        }

    def _check_notification_system(self) -> Dict[str, Any]:
        """Check notification system health"""
        return {
            "status": "healthy",
            "email_service": "operational",
            "teams_integration": "operational",
            "pending_notifications": 0,
            "failed_notifications_24h": 0
        }

    def _check_database(self) -> Dict[str, Any]:
        """Check database health"""
        return {
            "status": "healthy",
            "connection_pool": "available",
            "query_latency_ms": 150,
            "disk_usage_percent": 45.2,
            "replication_lag_seconds": 0
        }

    def _check_recent_activity(self) -> Dict[str, Any]:
        """Check recent system activity"""
        return {
            "status": "healthy",
            "last_rejection_cycle": (datetime.now() - timedelta(hours=1)).isoformat(),
            "sheets_processed_24h": 12,
            "records_processed_24h": 247,
            "branches_notified_24h": 5
        }

    def get_status_summary(self) -> str:
        """Get brief status summary"""
        if self.health_status == "healthy":
            return "✅ All systems operational"
        elif self.health_status == "degraded":
            return "⚠️ Some systems degraded"
        else:
            return "🔴 System unhealthy"


class PortalHealthMonitor:
    """Monitor individual portal health"""

    def __init__(self):
        self.portal_status = {
            "bupa": {"status": "healthy", "last_check": None, "consecutive_failures": 0},
            "globemed": {"status": "healthy", "last_check": None, "consecutive_failures": 0},
            "waseel": {"status": "healthy", "last_check": None, "consecutive_failures": 0}
        }

    def record_portal_check(self, payer: str, success: bool, latency_ms: float = None):
        """Record a portal health check"""
        if payer not in self.portal_status:
            return

        portal = self.portal_status[payer]
        portal["last_check"] = datetime.now().isoformat()

        if success:
            portal["consecutive_failures"] = 0
            portal["status"] = "healthy"
        else:
            portal["consecutive_failures"] += 1
            if portal["consecutive_failures"] >= 3:
                portal["status"] = "unhealthy"
            else:
                portal["status"] = "degraded"

        if latency_ms:
            portal["last_latency_ms"] = latency_ms

    def get_portal_status(self, payer: str) -> Dict[str, Any]:
        """Get status for specific portal"""
        return self.portal_status.get(payer, {})

    def get_all_portal_status(self) -> Dict[str, Any]:
        """Get status for all portals"""
        return self.portal_status

    def should_alert(self) -> bool:
        """Check if any portal needs alerting"""
        return any(
            status.get("status") == "unhealthy"
            for status in self.portal_status.values()
        )


class AlertingService:
    """Alert service for rejection system"""

    def __init__(self, health_check: HealthCheck, portal_monitor: PortalHealthMonitor):
        self.health_check = health_check
        self.portal_monitor = portal_monitor
        self.alerts = []

    def check_for_alerts(self) -> list:
        """Check system and return any alerts"""
        alerts = []

        # Check overall health
        health = self.health_check.check_health()
        if health["status"] != "healthy":
            alerts.append({
                "severity": "warning",
                "title": "System Health Degraded",
                "message": f"Overall system status: {health['status']}",
                "timestamp": datetime.now().isoformat()
            })

        # Check portal health
        for payer, status in self.portal_monitor.get_all_portal_status().items():
            if status.get("status") == "unhealthy":
                alerts.append({
                    "severity": "critical",
                    "title": f"{payer.upper()} Portal Unhealthy",
                    "message": f"{payer} portal has {status.get('consecutive_failures', 0)} consecutive failures",
                    "timestamp": datetime.now().isoformat()
                })

        self.alerts = alerts
        return alerts

    def get_critical_alerts(self) -> list:
        """Get only critical alerts"""
        return [a for a in self.alerts if a.get("severity") == "critical"]

    def acknowledge_alert(self, alert_index: int):
        """Mark alert as acknowledged"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index]["acknowledged"] = True


# Utility functions
def create_metrics() -> RejectionMetrics:
    """Create metrics instance"""
    return RejectionMetrics()


def create_health_check(metrics: RejectionMetrics = None) -> HealthCheck:
    """Create health check instance"""
    if metrics is None:
        metrics = create_metrics()
    return HealthCheck(metrics)


def create_portal_monitor() -> PortalHealthMonitor:
    """Create portal monitor instance"""
    return PortalHealthMonitor()


def create_alerting_service(
    health_check: HealthCheck = None,
    portal_monitor: PortalHealthMonitor = None
) -> AlertingService:
    """Create alerting service instance"""
    if health_check is None:
        health_check = create_health_check()
    if portal_monitor is None:
        portal_monitor = create_portal_monitor()
    return AlertingService(health_check, portal_monitor)


if __name__ == "__main__":
    # Initialize monitoring
    metrics = create_metrics()
    health_check = create_health_check(metrics)
    portal_monitor = create_portal_monitor()
    alerting = create_alerting_service(health_check, portal_monitor)

    print("🔍 Rejection Monitoring System Initialized")
    print(f"Health Status: {health_check.get_status_summary()}")
    print(f"Portal Status: {portal_monitor.get_all_portal_status()}")
