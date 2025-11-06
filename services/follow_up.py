"""Follow-up worksheet domain service and API models."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from integrations.teams.models import StakeholderGroup, TeamsPriority
from pipeline.follow_up_processor import (
    DUE_SOON_THRESHOLD_DAYS,
    FollowUpWorksheetProcessor,
)


def _format_priority_label(priority: TeamsPriority) -> str:
    mapping = {
        TeamsPriority.CRITICAL: "🔴 Critical",
        TeamsPriority.HIGH: "🟠 High",
        TeamsPriority.MEDIUM: "🟡 Medium",
        TeamsPriority.LOW: "🟢 Low",
        TeamsPriority.INFO: "🔵 Info",
    }
    return mapping.get(priority, priority.value.title())


def _priority_color(priority: TeamsPriority) -> str:
    mapping = {
        TeamsPriority.CRITICAL: "attention",
        TeamsPriority.HIGH: "warning",
        TeamsPriority.MEDIUM: "accent",
        TeamsPriority.LOW: "good",
        TeamsPriority.INFO: "default",
    }
    return mapping.get(priority, "default")


def _priority_icon(priority: TeamsPriority) -> str:
    mapping = {
        TeamsPriority.CRITICAL: "🚨",
        TeamsPriority.HIGH: "⚠️",
        TeamsPriority.MEDIUM: "ℹ️",
        TeamsPriority.LOW: "📝",
        TeamsPriority.INFO: "📢",
    }
    return mapping.get(priority, "📢")


class FollowUpRecord(BaseModel):
    """Normalized worksheet record exposed through the API."""

    correlation_id: str
    branch: str
    branch_key: str
    insurance_company: str
    batch_no: Optional[str] = None
    processor: Optional[str] = None
    status: str
    status_display: str
    status_raw: Optional[str] = None
    should_alert: bool = False
    priority: TeamsPriority
    priority_label: str = Field(..., description="Human readable priority")
    priority_color: str = Field(..., description="Adaptive Card color token")
    priority_icon: str = Field(..., description="Emoji icon representing priority")
    stakeholders: List[StakeholderGroup]
    alerts: List[str] = []
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    resubmission_date: Optional[date] = None
    days_until_due: Optional[int] = None
    billing_amount: Optional[float] = None
    approved_to_pay: Optional[float] = None
    final_rejection_amount: Optional[float] = None
    final_rejection_percent: Optional[float] = None
    recovery_amount: Optional[float] = None
    billing_month: Optional[str] = None
    billing_year: Optional[int] = None
    rework_type: Optional[str] = None
    batch_type: Optional[str] = None
    formatted: Dict[str, Any] = Field(default_factory=dict)
    portal_resources: List[Dict[str, Any]] = Field(default_factory=list)


class FollowUpSummary(BaseModel):
    """Aggregated worksheet metrics for dashboards."""

    total_rows: int
    actionable_rows: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    overdue: int
    due_soon: int
    ready_to_work: int
    not_submitted: int
    recovery_total: float
    billing_total: float
    rejection_total: float


class FollowUpSnapshot(BaseModel):
    """Top-level API payload containing worksheet snapshot."""

    generated_at: datetime
    workbook_path: str
    accounts_path: Optional[str]
    summary: FollowUpSummary
    overall_summary: FollowUpSummary
    records: List[FollowUpRecord]


class FollowUpWorksheetService:
    """Facade that turns worksheet contexts into API-friendly models."""

    def __init__(
        self,
        follow_up_path: Path,
        accounts_path: Optional[Path] = None,
    ) -> None:
        self.follow_up_path = Path(follow_up_path)
        self.accounts_path = Path(accounts_path) if accounts_path else None
        self._processor = FollowUpWorksheetProcessor(
            follow_up_path=self.follow_up_path,
            accounts_path=self.accounts_path,
        )

    def _build_record(self, context: Dict[str, Any]) -> FollowUpRecord:
        normalized = context.get("normalized", {})
        formatted = context.get("data", {})

        priority: TeamsPriority = context["priority"]
        stakeholders: List[StakeholderGroup] = context.get("stakeholders", [])
        alerts: List[str] = formatted.get("alerts", [])

        return FollowUpRecord(
            correlation_id=context["correlation_id"],
            branch=formatted.get("branch") or normalized.get("branch", "Unknown"),
            branch_key=normalized.get("branch_key", "unknown"),
            insurance_company=formatted.get("insurance_company") or normalized.get("insurance_company", "Unknown"),
            batch_no=formatted.get("batch_no") or normalized.get("batch_no"),
            processor=formatted.get("processor") or normalized.get("processor"),
            status=normalized.get("status", "unknown"),
            status_display=formatted.get("status_display", normalized.get("status_display", "Needs Review")),
            status_raw=normalized.get("status_raw"),
            should_alert=context.get("should_alert", False),
            priority=priority,
            priority_label=_format_priority_label(priority),
            priority_color=_priority_color(priority),
            priority_icon=_priority_icon(priority),
            stakeholders=stakeholders,
            alerts=alerts,
            due_date=normalized.get("due_date"),
            received_date=normalized.get("received_date"),
            resubmission_date=normalized.get("resubmission_date"),
            days_until_due=normalized.get("days_to_due"),
            billing_amount=normalized.get("billing_amount"),
            approved_to_pay=normalized.get("approved_to_pay"),
            final_rejection_amount=normalized.get("final_rejection_amount"),
            final_rejection_percent=normalized.get("final_rejection_percent"),
            recovery_amount=normalized.get("recovery_amount"),
            billing_month=normalized.get("billing_month"),
            billing_year=normalized.get("year"),
            rework_type=normalized.get("rework_type"),
            batch_type=normalized.get("batch_type"),
            formatted=formatted,
            portal_resources=formatted.get("portal_resources", []),
        )

    @staticmethod
    def build_summary(records: List[FollowUpRecord]) -> FollowUpSummary:
        total_rows = len(records)
        actionable_rows = sum(1 for record in records if record.should_alert)
        critical = sum(1 for record in records if record.priority == TeamsPriority.CRITICAL)
        high = sum(1 for record in records if record.priority == TeamsPriority.HIGH)
        medium = sum(1 for record in records if record.priority == TeamsPriority.MEDIUM)
        low = sum(1 for record in records if record.priority == TeamsPriority.LOW)
        info = sum(1 for record in records if record.priority == TeamsPriority.INFO)
        overdue = sum(
            1
            for record in records
            if record.days_until_due is not None and record.days_until_due < 0
        )
        due_soon = sum(
            1
            for record in records
            if record.days_until_due is not None and 0 <= record.days_until_due <= DUE_SOON_THRESHOLD_DAYS
        )
        ready_to_work = sum(1 for record in records if record.status == "ready_to_work")
        not_submitted = sum(1 for record in records if record.status == "not_submitted")

        recovery_total = sum(record.recovery_amount or 0.0 for record in records)
        billing_total = sum(record.billing_amount or 0.0 for record in records)
        rejection_total = sum(record.final_rejection_amount or 0.0 for record in records)

        return FollowUpSummary(
            total_rows=total_rows,
            actionable_rows=actionable_rows,
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            info=info,
            overdue=overdue,
            due_soon=due_soon,
            ready_to_work=ready_to_work,
            not_submitted=not_submitted,
            recovery_total=recovery_total,
            billing_total=billing_total,
            rejection_total=rejection_total,
        )

    def get_snapshot(self, include_non_alerts: bool = True) -> FollowUpSnapshot:
        contexts = self._processor.collect_contexts(include_non_alerts=include_non_alerts)
        records = [self._build_record(context) for context in contexts]
        summary = self.build_summary(records)

        generated_at = datetime.utcnow()

        return FollowUpSnapshot(
            generated_at=generated_at,
            workbook_path=str(self.follow_up_path),
            accounts_path=str(self.accounts_path) if self.accounts_path else None,
            summary=summary,
            overall_summary=summary,
            records=records,
        )
