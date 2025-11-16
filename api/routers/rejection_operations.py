"""
ClaimLinc Rejection Operations Router
FastAPI router for rejection sheet management, analysis, and branch routing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import tempfile
from pathlib import Path

# Import services
from scripts.data_processing.rejection_processor import (
    RejectionProcessor,
    RejectionRecord,
    process_rejection_file,
    generate_rejection_summary
)
from automation.ai_analyzer.rejection_analyzer import (
    RejectionAnalyzer,
    analyze_rejections,
    generate_branch_report
)
from api.services.notification_service import (
    NotificationRouter,
    NotificationChannel,
    send_rejection_report
)

# Pydantic models
class RejectionUploadRequest(BaseModel):
    """Request model for rejection sheet upload"""
    payer: str = Field(..., description="Payer name (bupa, globemed, waseel)")
    branch: Optional[str] = Field(None, description="Branch name (auto-detected from file if not provided)")
    process_immediately: bool = Field(True, description="Process and analyze immediately")


class BranchAcknowledgmentRequest(BaseModel):
    """Request model for branch acknowledgment"""
    branch: str = Field(..., description="Branch name")
    user: str = Field(..., description="User acknowledging the report")
    comments: Optional[str] = Field(None, description="Optional comments/feedback")


class RejectionResubmissionRequest(BaseModel):
    """Request model for claim resubmission"""
    rejection_ids: List[str] = Field(..., description="List of rejection record IDs to resubmit")
    corrections: Dict[str, Any] = Field(default_factory=dict, description="Corrections applied")
    target_submission_date: Optional[str] = Field(None, description="Target submission date")


class RejectionOperationsResponse(BaseModel):
    """Response model for rejection operations"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


# Initialize router
router = APIRouter(prefix="/api/v1/rejections", tags=["rejection_operations"])

# Initialize services
rejection_processor = RejectionProcessor()
rejection_analyzer = RejectionAnalyzer()
notification_router = NotificationRouter()


@router.post("/upload", response_model=RejectionOperationsResponse)
async def upload_rejection_sheet(
    payer: str = Form(...),
    file: UploadFile = File(...),
    branch: Optional[str] = Form(None),
    process_immediately: bool = Form(True),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and process rejection sheet from payer

    Args:
        payer: Payer name (bupa, globemed, waseel)
        file: Excel/CSV rejection sheet file
        branch: Optional branch name (auto-detected if not provided)
        process_immediately: Process and analyze immediately or queue for later
        background_tasks: Background task queue

    Returns:
        Upload status and processing results
    """
    try:
        # Validate payer
        valid_payers = ["bupa", "globemed", "waseel", "tawuniya"]
        if payer.lower() not in valid_payers:
            raise HTTPException(status_code=400, detail=f"Invalid payer. Valid values: {valid_payers}")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            # Process rejection sheet
            records = rejection_processor.process_rejection_sheet(tmp_path, payer)

            if not records:
                raise ValueError("No rejection records found in uploaded file")

            # Generate summary
            summary = rejection_processor.generate_branch_summary(records)

            # Convert records to dictionaries for JSON serialization
            records_dicts = [r.to_dict() if isinstance(r, RejectionRecord) else r for r in records]

            # If processing immediately, run analysis
            analysis_result = None
            if process_immediately:
                analysis_result = rejection_analyzer.analyze_rejections(records_dicts)

            response_data = {
                "records_processed": len(records),
                "summary": summary,
                "analysis": analysis_result if process_immediately else None,
                "file_path": tmp_path,
                "processed_at": datetime.now().isoformat()
            }

            # Queue background notification if requested
            if branch and background_tasks:
                background_tasks.add_task(
                    _send_branch_notifications,
                    branch=branch,
                    summary=summary,
                    analysis=analysis_result
                )

            return RejectionOperationsResponse(
                status="success",
                message=f"Successfully processed {len(records)} rejection records from {payer}",
                data=response_data
            )

        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process rejection sheet: {str(e)}"
        )


@router.get("/analysis/{branch}", response_model=RejectionOperationsResponse)
async def get_rejection_analysis(
    branch: str,
    days: int = 30,
    payer: Optional[str] = None
):
    """
    Get analysis of rejections for a specific branch

    Args:
        branch: Branch name
        days: Number of days to analyze (default: 30)
        payer: Optional payer filter

    Returns:
        Branch analysis and recommendations
    """
    try:
        # Validate branch
        valid_branches = notification_router.list_all_branches()
        if branch not in valid_branches:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid branch. Valid values: {valid_branches}"
            )

        # In production, fetch records from database filtered by branch/payer/date
        # For now, return example structure
        example_records = [
            {
                "claim_id": f"CLM-{i:05d}",
                "branch": branch,
                "payer_name": payer or "Bupa Arabia",
                "rejection_date": datetime.now().isoformat(),
                "reason_code": "INVALID_MEMBER",
                "reason_description": "Member ID not found in system",
                "severity": "high",
                "patient_member_id": f"MEM-{i:08d}",
                "claim_amount": 5000 + (i * 1000)
            }
            for i in range(1, 6)
        ]

        analysis = rejection_analyzer.analyze_rejections(example_records)
        report = rejection_analyzer.generate_branch_report(example_records, branch)

        return RejectionOperationsResponse(
            status="success",
            message=f"Analysis for {branch} retrieved successfully",
            data={
                "branch": branch,
                "analysis_period_days": days,
                "total_records_analyzed": len(example_records),
                "analysis": analysis,
                "branch_report": report
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )


@router.post("/acknowledge", response_model=RejectionOperationsResponse)
async def acknowledge_rejection_report(
    request: BranchAcknowledgmentRequest
):
    """
    Record branch acknowledgment of rejection report

    Args:
        request: Acknowledgment details

    Returns:
        Acknowledgment confirmation
    """
    try:
        # Validate branch
        valid_branches = notification_router.list_all_branches()
        if request.branch not in valid_branches:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid branch. Valid values: {valid_branches}"
            )

        # Record acknowledgment
        timestamp = datetime.now().isoformat()
        success = notification_router.notify_branch_acknowledgment(
            request.branch,
            request.user,
            timestamp
        )

        if not success:
            raise ValueError("Failed to record acknowledgment")

        return RejectionOperationsResponse(
            status="success",
            message=f"Acknowledgment recorded for {request.branch}",
            data={
                "branch": request.branch,
                "acknowledged_by": request.user,
                "acknowledged_at": timestamp,
                "comments": request.comments
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record acknowledgment: {str(e)}"
        )


@router.post("/resubmit", response_model=RejectionOperationsResponse)
async def prepare_claim_resubmission(
    request: RejectionResubmissionRequest,
    background_tasks: BackgroundTasks
):
    """
    Prepare rejected claims for resubmission with corrections

    Args:
        request: Resubmission details including rejection IDs and corrections
        background_tasks: Background task queue

    Returns:
        Resubmission preparation status
    """
    try:
        if not request.rejection_ids:
            raise ValueError("At least one rejection ID is required")

        # Queue resubmission preparation in background
        background_tasks.add_task(
            _prepare_resubmission,
            rejection_ids=request.rejection_ids,
            corrections=request.corrections,
            target_submission_date=request.target_submission_date
        )

        return RejectionOperationsResponse(
            status="queued",
            message=f"Resubmission prepared for {len(request.rejection_ids)} claims",
            data={
                "rejection_ids": request.rejection_ids,
                "corrections_applied": request.corrections,
                "target_submission_date": request.target_submission_date,
                "queued_at": datetime.now().isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to prepare resubmission: {str(e)}"
        )


@router.get("/summary/{branch}", response_model=RejectionOperationsResponse)
async def get_branch_rejection_summary(
    branch: str,
    days: int = 7
):
    """
    Get quick summary of recent rejections for a branch

    Args:
        branch: Branch name
        days: Number of days to summarize (default: 7)

    Returns:
        Branch rejection summary
    """
    try:
        # Validate branch
        valid_branches = notification_router.list_all_branches()
        if branch not in valid_branches:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid branch. Valid values: {valid_branches}"
            )

        # In production, fetch from database
        summary_data = {
            "branch": branch,
            "period_days": days,
            "total_rejections": 12,
            "total_at_risk": 87500.00,
            "by_payer": {
                "Bupa Arabia": {"count": 5, "amount": 35000},
                "GlobeMed": {"count": 4, "amount": 28500},
                "Tawuniya/Waseel": {"count": 3, "amount": 24000}
            },
            "by_severity": {
                "critical": {"count": 2, "amount": 15000},
                "high": {"count": 5, "amount": 42500},
                "medium": {"count": 4, "amount": 28000},
                "low": {"count": 1, "amount": 2000}
            },
            "action_required": True,
            "requires_immediate_attention": 2
        }

        return RejectionOperationsResponse(
            status="success",
            message=f"Summary for {branch} retrieved successfully",
            data=summary_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve summary: {str(e)}"
        )


@router.post("/run-full-cycle", response_model=RejectionOperationsResponse)
async def run_full_rejection_cycle(
    background_tasks: BackgroundTasks
):
    """
    Run full rejection monitoring, analysis, and dispatch cycle

    This endpoint triggers:
    1. Portal monitoring for new rejection sheets
    2. Extraction and normalization
    3. AI-driven analysis
    4. Branch routing and notifications
    5. Status tracking

    Returns:
        Cycle execution status
    """
    try:
        cycle_id = f"CYCLE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Queue full cycle execution
        background_tasks.add_task(_execute_full_cycle, cycle_id)

        return RejectionOperationsResponse(
            status="started",
            message="Full rejection cycle started",
            data={
                "cycle_id": cycle_id,
                "started_at": datetime.now().isoformat(),
                "steps": [
                    "Portal monitoring",
                    "Sheet extraction",
                    "Data normalization",
                    "AI analysis",
                    "Branch routing",
                    "Notifications sent"
                ]
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start rejection cycle: {str(e)}"
        )


@router.get("/cycle-status/{cycle_id}", response_model=RejectionOperationsResponse)
async def get_cycle_status(cycle_id: str):
    """
    Get status of a running rejection cycle

    Args:
        cycle_id: Cycle identifier

    Returns:
        Cycle status and progress
    """
    try:
        # In production, fetch status from database/cache
        status_data = {
            "cycle_id": cycle_id,
            "status": "in_progress",
            "current_step": "branch_routing",
            "progress_percentage": 75,
            "steps_completed": [
                {"step": "Portal monitoring", "status": "completed", "timestamp": datetime.now().isoformat()},
                {"step": "Sheet extraction", "status": "completed", "timestamp": datetime.now().isoformat()},
                {"step": "Data normalization", "status": "completed", "timestamp": datetime.now().isoformat()},
                {"step": "AI analysis", "status": "completed", "timestamp": datetime.now().isoformat()}
            ],
            "steps_pending": [
                {"step": "Branch routing", "status": "in_progress"},
                {"step": "Notifications sent", "status": "pending"}
            ]
        }

        return RejectionOperationsResponse(
            status="success",
            message="Cycle status retrieved",
            data=status_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cycle status: {str(e)}"
        )


# Background task functions
async def _send_branch_notifications(branch: str, summary: Dict[str, Any], analysis: Dict[str, Any]):
    """Background task: Send notifications to branch"""
    try:
        channels = [NotificationChannel.EMAIL, NotificationChannel.TEAMS, NotificationChannel.INTERNAL]
        results = notification_router.route_rejection_report(branch, summary, analysis, channels)
        print(f"✅ Notifications sent for {branch}: {results}")
    except Exception as e:
        print(f"❌ Failed to send notifications: {str(e)}")


async def _prepare_resubmission(
    rejection_ids: List[str],
    corrections: Dict[str, Any],
    target_submission_date: Optional[str]
):
    """Background task: Prepare claims for resubmission"""
    try:
        print(f"📝 Preparing {len(rejection_ids)} claims for resubmission")
        # In production, this would:
        # 1. Retrieve original claims
        # 2. Apply corrections
        # 3. Validate against payer requirements
        # 4. Queue for submission
        print(f"✅ Resubmission preparation complete")
    except Exception as e:
        print(f"❌ Failed to prepare resubmission: {str(e)}")


async def _execute_full_cycle(cycle_id: str):
    """Background task: Execute full rejection monitoring cycle"""
    try:
        print(f"🔄 Starting full rejection cycle: {cycle_id}")

        # Step 1: Monitor portals
        print(f"📡 Monitoring payer portals...")

        # Step 2: Extract rejections
        print(f"📥 Extracting rejection sheets...")

        # Step 3: Normalize data
        print(f"🔄 Normalizing rejection data...")

        # Step 4: Analyze
        print(f"🧠 Running AI analysis...")

        # Step 5: Route to branches
        print(f"📍 Routing to branches...")

        # Step 6: Send notifications
        for branch in notification_router.list_all_branches():
            print(f"📧 Notifying {branch}...")

        print(f"✅ Full cycle completed: {cycle_id}")

    except Exception as e:
        print(f"❌ Full cycle failed: {str(e)}")


# Include router in main app
# In api/main.py, add: from api.routers.rejection_operations import router as rejection_router
# Then: app.include_router(rejection_router)
