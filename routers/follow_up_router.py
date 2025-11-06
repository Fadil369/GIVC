"""API router exposing the follow-up worksheet snapshot."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from config.settings import settings
from integrations.teams.models import TeamsPriority
from services.follow_up import (
    FollowUpSnapshot,
    FollowUpWorksheetService,
)

router = APIRouter(prefix="/api/follow-ups", tags=["Follow Ups"])


def get_follow_up_service() -> FollowUpWorksheetService:
    follow_up_path = Path(settings.FOLLOW_UP_WORKBOOK_PATH)
    accounts_path = Path(settings.ACCOUNTS_WORKBOOK_PATH) if settings.ACCOUNTS_WORKBOOK_PATH else None
    return FollowUpWorksheetService(follow_up_path=follow_up_path, accounts_path=accounts_path)


@router.get("", response_model=FollowUpSnapshot)
async def list_follow_ups(
    include_non_alerts: bool = Query(
        True,
        description="Include non-alert worksheet rows in the response",
    ),
    priority: Optional[TeamsPriority] = Query(
        None,
        description="Filter records by Teams priority level",
    ),
    branch: Optional[str] = Query(
        None,
        description="Filter by branch name or branch key (case-insensitive)",
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by normalized status (e.g. ready_to_work)",
    ),
    should_alert: Optional[bool] = Query(
        None,
        description="Filter by actionable flag",
    ),
    service: FollowUpWorksheetService = Depends(get_follow_up_service),
) -> FollowUpSnapshot:
    try:
        snapshot = await run_in_threadpool(service.get_snapshot, include_non_alerts)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    def _matches(record) -> bool:
        if priority and record.priority != priority:
            return False
        if branch:
            branch_lower = branch.strip().lower()
            if record.branch_key.lower() != branch_lower and record.branch.lower() != branch_lower:
                return False
        if status:
            status_lower = status.strip().lower()
            if record.status.lower() != status_lower:
                return False
        if should_alert is not None and record.should_alert is not should_alert:
            return False
        return True

    filtered_records = [record for record in snapshot.records if _matches(record)]

    summary = FollowUpWorksheetService.build_summary(filtered_records)

    return FollowUpSnapshot(
        generated_at=snapshot.generated_at,
        workbook_path=snapshot.workbook_path,
        accounts_path=snapshot.accounts_path,
        summary=summary,
        overall_summary=snapshot.overall_summary,
        records=filtered_records,
    )
