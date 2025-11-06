"""
ClaimLinc Alert System
Handles alerting and notification management for critical events and thresholds
"""

import asyncio
import json
import smtplib
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from enum import Enum
import structlog


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    threshold: float
    comparison: str  # >, <, >=, <=, ==, !=
    severity: AlertSeverity
    channels: List[AlertChannel]
    enabled: bool = True
    cooldown_minutes: int = 5
    description: str = ""


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_name: str
    severity: AlertSeverity
    title: str
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path("./config/alert_config.json")
        self.config = self._load_config()
        self.active_alerts = {}
        self.alert_history = []
        self.alert_rules = self._load_alert_rules()
        self.logger = structlog.get_logger("alert_manager")
        
        # Alert tracking
        self.last_alert_time = {}
        self.alert_cooldowns = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load alert configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default alert configuration"""
        config = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "alerts@claimlinc.com",
                "to_addresses": ["admin@claimlinc.com", "ops@claimlinc.com"]
            },
            "webhook": {
                "slack_webhook": "",
                "teams_webhook": "",
                "custom_webhooks": []
            },
            "sms": {
                "provider": "twilio",
                "account_sid": "",
                "auth_token": "",
                "from_number": "",
                "to_numbers": ["+966501234567"]
            },
            "thresholds": {
                "cpu_usage_critical": 90,
                "memory_usage_critical": 90,
                "disk_usage_critical": 85,
                "error_rate_critical": 0.05,
                "success_rate_warning": 0.8
            },
            "notification_rules": {
                "critical_alerts": ["email", "slack", "sms"],
                "warning_alerts": ["email", "slack"],
                "info_alerts": ["email"]
            }
        }
        
        # Save default config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _save_config(self):
        """Save current configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules from configuration"""
        rules_config = self.config.get("alert_rules", [])
        rules = []
        
        for rule_config in rules_config:
            rule = AlertRule(
                name=rule_config["name"],
                metric_name=rule_config["metric_name"],
                threshold=rule_config["threshold"],
                comparison=rule_config["comparison"],
                severity=AlertSeverity(rule_config["severity"]),
                channels=[AlertChannel(channel) for channel in rule_config["channels"]],
                enabled=rule_config.get("enabled", True),
                cooldown_minutes=rule_config.get("cooldown_minutes", 5),
                description=rule_config.get("description", "")
            )
            rules.append(rule)
        
        # Add default rules if none exist
        if not rules:
            rules = self._create_default_rules()
        
        return rules
    
    def _create_default_rules(self) -> List[AlertRule]:
        """Create default alert rules"""
        default_rules = [
            AlertRule(
                name="High CPU Usage",
                metric_name="cpu_usage",
                threshold=90,
                comparison=">",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                description="CPU usage exceeds 90%"
            ),
            AlertRule(
                name="High Memory Usage",
                metric_name="memory_usage",
                threshold=90,
                comparison=">",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                description="Memory usage exceeds 90%"
            ),
            AlertRule(
                name="Low Success Rate",
                metric_name="automation_success_rate",
                threshold=0.8,
                comparison="<",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL],
                description="Automation success rate below 80%"
            ),
            AlertRule(
                name="High Validation Error Rate",
                metric_name="validation_error_rate",
                threshold=0.1,
                comparison=">",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL],
                description="Validation error rate exceeds 10%"
            ),
            AlertRule(
                name="Service Down",
                metric_name="service_health",
                threshold=1,
                comparison="<",
                severity=AlertSeverity.EMERGENCY,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.SMS],
                description="Critical service is down"
            )
        ]
        
        # Save rules to config
        self.config["alert_rules"] = [
            {
                "name": rule.name,
                "metric_name": rule.metric_name,
                "threshold": rule.threshold,
                "comparison": rule.comparison,
                "severity": rule.severity.value,
                "channels": [channel.value for channel in rule.channels],
                "enabled": rule.enabled,
                "cooldown_minutes": rule.cooldown_minutes,
                "description": rule.description
            }
            for rule in default_rules
        ]
        
        self._save_config()
        return default_rules
    
    async def start_alert_monitoring(self):
        """Start alert monitoring service"""
        try:
            self.logger.info("Starting alert monitoring service")
            
            # Start alert evaluation
            asyncio.create_task(self._evaluate_alerts())
            
            # Start alert cleanup
            asyncio.create_task(self._cleanup_old_alerts())
            
            self.logger.info("Alert monitoring service started")
            
        except Exception as e:
            self.logger.error(f"Failed to start alert monitoring: {e}")
            raise
    
    async def _evaluate_alerts(self):
        """Evaluate alerts against rules"""
        while True:
            try:
                # Get current metrics (would integrate with monitoring manager)
                metrics = await self._get_current_metrics()
                
                # Evaluate each rule
                for rule in self.alert_rules:
                    if not rule.enabled:
                        continue
                    
                    await self._evaluate_rule(rule, metrics)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error evaluating alerts: {e}")
                await asyncio.sleep(30)
    
    async def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Evaluate a specific rule against current metrics"""
        try:
            metric_value = metrics.get(rule.metric_name)
            if metric_value is None:
                return
            
            # Check if alert should be triggered
            should_alert = self._compare_values(metric_value, rule.threshold, rule.comparison)
            
            # Check cooldown period
            if self._is_in_cooldown(rule.name):
                return
            
            if should_alert:
                await self._trigger_alert(rule, metric_value)
            else:
                # Check if we should resolve existing alert
                await self._resolve_alert_if_needed(rule.name)
                
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule.name}: {e}")
    
    def _compare_values(self, value: float, threshold: float, comparison: str) -> bool:
        """Compare value against threshold based on comparison operator"""
        if comparison == ">":
            return value > threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == ">=":
            return value >= threshold
        elif comparison == "<=":
            return value <= threshold
        elif comparison == "==":
            return value == threshold
        elif comparison == "!=":
            return value != threshold
        else:
            self.logger.error(f"Unknown comparison operator: {comparison}")
            return False
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if rule is in cooldown period"""
        rule = next((r for r in self.alert_rules if r.name == rule_name), None)
        if not rule:
            return False
        
        last_alert = self.last_alert_time.get(rule_name)
        if not last_alert:
            return False
        
        cooldown_end = last_alert + timedelta(minutes=rule.cooldown_minutes)
        return datetime.now() < cooldown_end
    
    async def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """Trigger an alert"""
        alert_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            severity=rule.severity,
            title=f"Alert: {rule.name}",
            message=rule.description,
            metric_value=metric_value,
            threshold=rule.threshold,
            timestamp=datetime.now()
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.last_alert_time[rule.name] = datetime.now()
        
        # Log alert
        self.logger.warning(
            f"Alert triggered: {rule.name}",
            alert_id=alert_id,
            metric_value=metric_value,
            threshold=rule.threshold,
            severity=rule.severity.value
        )
        
        # Send notifications
        await self._send_notifications(alert, rule)
    
    async def _resolve_alert_if_needed(self, rule_name: str):
        """Resolve alert if conditions have improved"""
        # Find active alert for this rule
        active_alerts = [alert for alert in self.active_alerts.values() 
                        if alert.rule_name == rule_name and not alert.resolved]
        
        if not active_alerts:
            return
        
        # Resolve all active alerts for this rule
        for alert in active_alerts:
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            self.logger.info(
                f"Alert resolved: {rule_name}",
                alert_id=alert.id,
                duration=str(alert.resolved_at - alert.timestamp)
            )
        
        # Remove from active alerts (keep in history)
        self.active_alerts = {k: v for k, v in self.active_alerts.items() 
                            if v.rule_name != rule_name or not v.resolved}
    
    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send alert notifications through configured channels"""
        for channel in rule.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert, rule)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_alert(alert, rule)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert, rule)
                elif channel == AlertChannel.TEAMS:
                    await self._send_teams_alert(alert, rule)
                elif channel == AlertChannel.SMS:
                    await self._send_sms_alert(alert, rule)
                    
            except Exception as e:
                self.logger.error(f"Failed to send {channel.value} alert: {e}")
    
    async def _send_email_alert(self, alert: Alert, rule: AlertRule):
        """Send email alert"""
        email_config = self.config.get("email", {})
        if not email_config.get("username") or not email_config.get("password"):
            self.logger.warning("Email configuration incomplete, skipping email alert")
            return
        
        try:
            # Create email content
            subject = f"[{alert.severity.value.upper()}] ClaimLinc Alert - {rule.name}"
            
            body = f"""
            Alert Details:
            - Alert: {rule.name}
            - Severity: {alert.severity.value.upper()}
            - Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            - Metric: {rule.metric_name}
            - Current Value: {alert.metric_value}
            - Threshold: {alert.threshold}
            - Description: {alert.message}
            
            Please investigate this issue immediately.
            
            ClaimLinc Monitoring System
            """
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = email_config["from_address"]
            msg['To'] = ", ".join(email_config["to_addresses"])
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            text = msg.as_string()
            server.sendmail(email_config["from_address"], email_config["to_addresses"], text)
            server.quit()
            
            self.logger.info(f"Email alert sent for {rule.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    async def _send_slack_alert(self, alert: Alert, rule: AlertRule):
        """Send Slack alert"""
        webhook_url = self.config.get("webhook", {}).get("slack_webhook")
        if not webhook_url:
            self.logger.warning("Slack webhook not configured, skipping Slack alert")
            return
        
        try:
            color = {
                AlertSeverity.INFO: "good",
                AlertSeverity.WARNING: "warning", 
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.EMERGENCY: "danger"
            }.get(alert.severity, "warning")
            
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"🚨 ClaimLinc Alert: {rule.name}",
                        "fields": [
                            {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                            {"title": "Metric", "value": rule.metric_name, "short": True},
                            {"title": "Current Value", "value": str(alert.metric_value), "short": True},
                            {"title": "Threshold", "value": str(alert.threshold), "short": True},
                            {"title": "Time", "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "short": False}
                        ],
                        "text": alert.message
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"Slack alert sent for {rule.name}")
                    else:
                        self.logger.error(f"Slack API returned status {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert, rule: AlertRule):
        """Send generic webhook alert"""
        webhook_urls = self.config.get("webhook", {}).get("custom_webhooks", [])
        if not webhook_urls:
            return
        
        payload = {
            "alert": asdict(alert),
            "rule": {
                "name": rule.name,
                "metric_name": rule.metric_name,
                "threshold": rule.threshold,
                "severity": rule.severity.value
            },
            "timestamp": datetime.now().isoformat()
        }
        
        for webhook_url in webhook_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=payload) as response:
                        if response.status < 400:
                            self.logger.info(f"Webhook alert sent to {webhook_url}")
                        else:
                            self.logger.error(f"Webhook returned status {response.status}")
                            
            except Exception as e:
                self.logger.error(f"Failed to send webhook alert: {e}")
    
    async def _send_teams_alert(self, alert: Alert, rule: AlertRule):
        """Send Microsoft Teams alert"""
        webhook_url = self.config.get("webhook", {}).get("teams_webhook")
        if not webhook_url:
            return
        
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "FF0000" if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] else "FFA500",
                "summary": f"ClaimLinc Alert: {rule.name}",
                "sections": [
                    {
                        "activityTitle": f"🚨 ClaimLinc Alert: {rule.name}",
                        "activitySubtitle": alert.message,
                        "facts": [
                            {"name": "Severity", "value": alert.severity.value.upper()},
                            {"name": "Metric", "value": rule.metric_name},
                            {"name": "Current Value", "value": str(alert.metric_value)},
                            {"name": "Threshold", "value": str(rule.threshold)},
                            {"name": "Time", "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"Teams alert sent for {rule.name}")
                    else:
                        self.logger.error(f"Teams API returned status {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Failed to send Teams alert: {e}")
    
    async def _send_sms_alert(self, alert: Alert, rule: AlertRule):
        """Send SMS alert (mock implementation)"""
        # Mock SMS implementation - would integrate with Twilio or other SMS provider
        sms_config = self.config.get("sms", {})
        if not sms_config.get("account_sid"):
            return
        
        message = f"ClaimLinc Alert: {rule.name} - {alert.message} (Value: {alert.metric_value}, Threshold: {rule.threshold})"
        
        # In real implementation, would use Twilio API
        self.logger.info(f"SMS alert would be sent: {message}")
    
    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics (mock implementation)"""
        # In real implementation, would integrate with monitoring manager
        return {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 34.1,
            "automation_success_rate": 0.94,
            "validation_error_rate": 0.03,
            "service_health": 1
        }
    
    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts from history"""
        while True:
            try:
                cutoff_date = datetime.now() - timedelta(days=30)
                
                # Remove old alerts from history
                self.alert_history = [
                    alert for alert in self.alert_history 
                    if alert.resolved_at is None or alert.resolved_at > cutoff_date
                ]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up old alerts: {e}")
                await asyncio.sleep(3600)
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            
            self.logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        
        return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return [asdict(alert) for alert in self.active_alerts.values()]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        now = datetime.now()
        last_24h = now - timedelta(days=1)
        last_7d = now - timedelta(days=7)
        
        recent_alerts = [alert for alert in self.alert_history if alert.timestamp > last_24h]
        weekly_alerts = [alert for alert in self.alert_history if alert.timestamp > last_7d]
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([
                alert for alert in recent_alerts if alert.severity == severity
            ])
        
        return {
            "total_active": len(self.active_alerts),
            "total_resolved": len([alert for alert in self.alert_history if alert.resolved]),
            "last_24h_total": len(recent_alerts),
            "last_7d_total": len(weekly_alerts),
            "severity_breakdown_24h": severity_counts,
            "most_frequent_rules": self._get_most_frequent_rules(weekly_alerts)
        }
    
    def _get_most_frequent_rules(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        """Get most frequent alert rules"""
        rule_counts = {}
        for alert in alerts:
            rule_counts[alert.rule_name] = rule_counts.get(alert.rule_name, 0) + 1
        
        return [
            {"rule": rule, "count": count}
            for rule, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]


# Utility functions
def get_alert_manager() -> AlertManager:
    """Get global alert manager instance"""
    if not hasattr(get_alert_manager, "_instance"):
        get_alert_manager._instance = AlertManager()
    return get_alert_manager._instance


if __name__ == "__main__":
    # Example usage
    async def main():
        alert_manager = AlertManager()
        await alert_manager.start_alert_monitoring()
        
        # Simulate some alert conditions
        import random
        
        for i in range(20):
            # Randomly trigger some alerts
            if random.random() > 0.7:
                # Simulate high CPU
                await alert_manager._evaluate_rule(
                    AlertRule(
                        name="High CPU Usage",
                        metric_name="cpu_usage",
                        threshold=90,
                        comparison=">",
                        severity=AlertSeverity.CRITICAL,
                        channels=[AlertChannel.EMAIL]
                    ),
                    {"cpu_usage": random.uniform(85, 95)}
                )
            
            if random.random() > 0.8:
                # Simulate low success rate
                await alert_manager._evaluate_rule(
                    AlertRule(
                        name="Low Success Rate",
                        metric_name="automation_success_rate",
                        threshold=0.8,
                        comparison="<",
                        severity=AlertSeverity.WARNING,
                        channels=[AlertChannel.EMAIL]
                    ),
                    {"automation_success_rate": random.uniform(0.7, 0.85)}
                )
            
            await asyncio.sleep(10)
        
        # Get statistics
        stats = alert_manager.get_alert_statistics()
        print(json.dumps(stats, indent=2, default=str))
        
        # Get active alerts
        active = alert_manager.get_active_alerts()
        print(f"Active alerts: {len(active)}")
    
    asyncio.run(main())
