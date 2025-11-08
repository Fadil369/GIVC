"""
ClaimLinc Notification & Branch Routing Service
Handles email, Teams, and internal notification routing
"""

import json
import smtplib
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
import os
from pathlib import Path


class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    TEAMS = "teams"
    INTERNAL = "internal"
    SMS = "sms"


class BranchConfig:
    """Branch configuration for routing"""

    BRANCH_ROUTING_MAP = {
        "MainRiyadh": {
            "email": os.getenv("EMAIL_OPS_RIYADH", "ops.riyadh@alhayat.example"),
            "teams": os.getenv("TEAMS_RIYADH", "teams://AlHayat/MainRiyadh/Claims"),
            "manager": "Riyadh Operations Manager",
            "phone": os.getenv("PHONE_RIYADH", "+966-11-XXXXXX")
        },
        "Unaizah": {
            "email": os.getenv("EMAIL_OPS_UNAIZAH", "ops.unaizah@alhayat.example"),
            "teams": os.getenv("TEAMS_UNAIZAH", "teams://AlHayat/Unaizah/Claims"),
            "manager": "Unaizah Operations Manager",
            "phone": os.getenv("PHONE_UNAIZAH", "+966-16-XXXXXX")
        },
        "Abha": {
            "email": os.getenv("EMAIL_OPS_ABHA", "ops.abha@alhayat.example"),
            "teams": os.getenv("TEAMS_ABHA", "teams://AlHayat/Abha/Claims"),
            "manager": "Abha Operations Manager",
            "phone": os.getenv("PHONE_ABHA", "+966-17-XXXXXX")
        },
        "Madinah": {
            "email": os.getenv("EMAIL_OPS_MADINAH", "ops.madinah@alhayat.example"),
            "teams": os.getenv("TEAMS_MADINAH", "teams://AlHayat/Madinah/Claims"),
            "manager": "Madinah Operations Manager",
            "phone": os.getenv("PHONE_MADINAH", "+966-14-XXXXXX")
        },
        "Khamis": {
            "email": os.getenv("EMAIL_OPS_KHAMIS", "ops.khamis@alhayat.example"),
            "teams": os.getenv("TEAMS_KHAMIS", "teams://AlHayat/Khamis/Claims"),
            "manager": "Khamis Operations Manager",
            "phone": os.getenv("PHONE_KHAMIS", "+966-17-XXXXXX")
        }
    }


class EmailService:
    """Email notification service"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@claimlinc.brainsait.io")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        cc_emails: List[str] = None,
        bcc_emails: List[str] = None,
        attachments: List[Dict[str, Any]] = None
    ) -> bool:
        """
        Send email notification

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            cc_emails: CC email addresses
            bcc_emails: BCC email addresses
            attachments: List of attachment dictionaries with 'filename' and 'content'

        Returns:
            Success status
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email

            if cc_emails:
                message["Cc"] = ", ".join(cc_emails)

            # Add HTML part
            message.attach(MIMEText(html_content, "html"))

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    try:
                        part = MIMEText(attachment.get("content", ""))
                        part.add_header("Content-Disposition", "attachment", filename=attachment.get("filename", "file.txt"))
                        message.attach(part)
                    except Exception as e:
                        print(f"Warning: Failed to attach {attachment.get('filename')}: {str(e)}")

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()

            server.login(self.sender_email, self.sender_password)

            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            if bcc_emails:
                recipients.extend(bcc_emails)

            server.sendmail(self.sender_email, recipients, message.as_string())
            server.quit()

            print(f"✅ Email sent to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            return False

    def send_rejection_report(
        self,
        to_email: str,
        branch: str,
        summary: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> bool:
        """Send formatted rejection report via email"""
        try:
            html_content = self._generate_rejection_report_html(branch, summary, analysis)
            subject = f"ClaimLinc: Rejection Report for {branch} - {datetime.now().strftime('%Y-%m-%d')}"

            return self.send_email(to_email, subject, html_content)

        except Exception as e:
            print(f"❌ Failed to send rejection report: {str(e)}")
            return False

    def _generate_rejection_report_html(
        self,
        branch: str,
        summary: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Generate HTML rejection report"""
        total_rejections = summary.get("total_rejections", 0)
        total_at_risk = summary.get("total_at_risk", 0)
        critical_count = summary.get("by_severity", {}).get("critical", 0)

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
                h2 {{ color: #0066cc; margin-top: 20px; }}
                .critical {{ color: #d32f2f; font-weight: bold; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .metric {{ display: inline-block; margin-right: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #0066cc; color: white; }}
                .alert {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
                .action {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>ClaimLinc Rejection Report - {branch}</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="metric"><strong>Total Rejections:</strong> {total_rejections}</div>
                <div class="metric"><strong>Total at Risk:</strong> SAR {total_at_risk:,.2f}</div>
                <div class="metric"><strong>Critical Issues:</strong> <span class="critical">{critical_count}</span></div>
            </div>

            <h2>Rejection Breakdown by Severity</h2>
            <table>
                <tr>
                    <th>Severity Level</th>
                    <th>Count</th>
                    <th>Action Required</th>
                </tr>
                <tr>
                    <td class="critical">Critical</td>
                    <td>{summary.get("by_severity", {}).get("critical", 0)}</td>
                    <td>Immediate action required - cannot resubmit as-is</td>
                </tr>
                <tr>
                    <td style="color: #ff9800;">High</td>
                    <td>{summary.get("by_severity", {}).get("high", 0)}</td>
                    <td>Major corrections needed before resubmission</td>
                </tr>
                <tr>
                    <td style="color: #2196f3;">Medium</td>
                    <td>{summary.get("by_severity", {}).get("medium", 0)}</td>
                    <td>Minor corrections required</td>
                </tr>
                <tr>
                    <td style="color: #4caf50;">Low</td>
                    <td>{summary.get("by_severity", {}).get("low", 0)}</td>
                    <td>Informational - monitor for patterns</td>
                </tr>
            </table>

            <h2>Analysis & Insights</h2>
        """

        # Add insights
        for insight in analysis.get("insights", [])[:5]:
            html += f"""
            <div class="alert">
                <strong>{insight.get('reason_code', 'Unknown')}:</strong>
                {insight.get('count', 0)} cases affecting SAR {insight.get('total_at_risk', 0):,.2f}
                <br/>
                <em>{', '.join(insight.get('recommended_actions', [])[:2])}</em>
            </div>
            """

        # Add recommendations
        html += "<h2>Recommended Actions</h2>"
        for i, rec in enumerate(analysis.get("recommendations", []), 1):
            html += f'<div class="action">{i}. {rec}</div>'

        html += """
            <h2>Next Steps</h2>
            <ol>
                <li>Review critical rejections immediately</li>
                <li>Gather necessary documentation for high-severity items</li>
                <li>Submit corrections according to payer requirements</li>
                <li>Acknowledge receipt of this report via system</li>
            </ol>

            <p style="margin-top: 30px; color: #999; font-size: 12px;">
                This is an automated report from ClaimLinc. Please do not reply to this email.
                <br/>
                For questions, contact the ClaimLinc Operations team.
            </p>
        </body>
        </html>
        """

        return html


class TeamsNotificationService:
    """Teams notification service (webhook-based)"""

    def __init__(self):
        self.webhook_base = os.getenv("TEAMS_WEBHOOK_BASE", "https://outlook.webhook.office.com/webhookb2/")

    def send_notification(
        self,
        title: str,
        message: str,
        channel: str,
        severity: str = "info",
        actions: List[Dict[str, str]] = None
    ) -> bool:
        """
        Send Teams notification via webhook

        Args:
            title: Notification title
            message: Notification message
            channel: Teams channel identifier
            severity: Severity level (info, warning, critical)
            actions: List of action buttons

        Returns:
            Success status
        """
        try:
            # Color coding by severity
            color_map = {
                "info": "0078D4",
                "warning": "FFB900",
                "critical": "DA3B01"
            }

            color = color_map.get(severity, "0078D4")

            # This is a simplified implementation
            # In production, you would construct proper Teams Adaptive Cards
            print(f"📢 Teams notification: {title} - {message}")
            return True

        except Exception as e:
            print(f"❌ Teams notification failed: {str(e)}")
            return False

    def send_rejection_alert(
        self,
        branch: str,
        critical_count: int,
        total_amount: float,
        top_issue: str
    ) -> bool:
        """Send rejection alert to Teams"""
        try:
            title = f"🚨 Rejection Alert: {branch}"
            message = f"""
            Critical Issues: {critical_count}
            Total at Risk: SAR {total_amount:,.2f}
            Top Issue: {top_issue}
            Action Required: Review and respond immediately
            """

            channel_config = BranchConfig.BRANCH_ROUTING_MAP.get(branch, {})
            teams_channel = channel_config.get("teams", "")

            return self.send_notification(title, message, teams_channel, severity="critical")

        except Exception as e:
            print(f"❌ Failed to send rejection alert: {str(e)}")
            return False


class NotificationRouter:
    """Routes notifications to appropriate channels and branches"""

    def __init__(self):
        self.email_service = EmailService()
        self.teams_service = TeamsNotificationService()

    def route_rejection_report(
        self,
        branch: str,
        summary: Dict[str, Any],
        analysis: Dict[str, Any],
        channels: List[NotificationChannel] = None
    ) -> Dict[str, bool]:
        """
        Route rejection report to appropriate channels

        Args:
            branch: Branch name
            summary: Rejection summary statistics
            analysis: AI analysis results
            channels: Notification channels to use

        Returns:
            Dictionary of channel results
        """
        if channels is None:
            channels = [NotificationChannel.EMAIL, NotificationChannel.TEAMS, NotificationChannel.INTERNAL]

        results = {}
        branch_config = BranchConfig.BRANCH_ROUTING_MAP.get(branch, {})

        # Route to email
        if NotificationChannel.EMAIL in channels:
            email = branch_config.get("email")
            if email:
                results["email"] = self.email_service.send_rejection_report(
                    email, branch, summary, analysis
                )

        # Route to Teams
        if NotificationChannel.TEAMS in channels:
            teams_channel = branch_config.get("teams")
            if teams_channel:
                critical_count = summary.get("by_severity", {}).get("critical", 0)
                total_amount = summary.get("total_at_risk", 0)
                top_issue = analysis.get("insights", [{}])[0].get("reason_code", "Unknown")

                results["teams"] = self.teams_service.send_rejection_alert(
                    branch, critical_count, total_amount, top_issue
                )

        # Route to internal system
        if NotificationChannel.INTERNAL in channels:
            results["internal"] = self._record_internal_notification(branch, summary)

        return results

    def notify_branch_acknowledgment(self, branch: str, user: str, timestamp: str) -> bool:
        """Record branch acknowledgment of rejection report"""
        try:
            log_entry = {
                "branch": branch,
                "user": user,
                "timestamp": timestamp,
                "action": "acknowledged_rejection_report"
            }
            print(f"✅ Branch acknowledgment recorded: {log_entry}")
            return True
        except Exception as e:
            print(f"❌ Failed to record acknowledgment: {str(e)}")
            return False

    def _record_internal_notification(self, branch: str, summary: Dict[str, Any]) -> bool:
        """Record notification in internal system"""
        try:
            notification = {
                "type": "rejection_report",
                "branch": branch,
                "timestamp": datetime.now().isoformat(),
                "summary": summary
            }
            print(f"✅ Internal notification recorded: {notification}")
            return True
        except Exception as e:
            print(f"❌ Failed to record internal notification: {str(e)}")
            return False

    def get_branch_contacts(self, branch: str) -> Dict[str, str]:
        """Get contact information for a branch"""
        return BranchConfig.BRANCH_ROUTING_MAP.get(branch, {})

    def list_all_branches(self) -> List[str]:
        """List all configured branches"""
        return list(BranchConfig.BRANCH_ROUTING_MAP.keys())


# Utility functions
def send_rejection_report(
    branch: str,
    summary: Dict[str, Any],
    analysis: Dict[str, Any],
    channels: List[str] = None
) -> Dict[str, bool]:
    """Utility function to send rejection report"""
    router = NotificationRouter()
    channel_enums = [NotificationChannel(c) for c in (channels or ["email", "teams", "internal"])]
    return router.route_rejection_report(branch, summary, analysis, channel_enums)


if __name__ == "__main__":
    router = NotificationRouter()
    print("NotificationRouter initialized")
    print(f"Configured branches: {router.list_all_branches()}")
