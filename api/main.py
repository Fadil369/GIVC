"""
ClaimLinc FastAPI Main Application
Main API server for claim normalization, validation, and automation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.normalize_data import ClaimDataNormalizer, normalize_claim_data, batch_normalize_claims
from scripts.validate_data import ClaimDataValidator, validate_claim_data, batch_validate_claims
from scripts.generate_test_data import TestDataGenerator, ReportGenerator, generate_test_claims

# Pydantic models for API requests/responses
class ClaimRequest(BaseModel):
    """Request model for single claim processing"""
    claim_data: Dict[str, Any] = Field(..., description="Raw claim data to process")
    source_format: str = Field(..., description="Source format: bupa, globemed, waseel, or generic")
    validation_required: bool = Field(True, description="Whether to validate after normalization")

class BatchClaimRequest(BaseModel):
    """Request model for batch claim processing"""
    claims_data: List[Dict[str, Any]] = Field(..., description="List of claim data to process")
    source_format: str = Field(..., description="Source format: bupa, globemed, waseel, or generic")
    validation_required: bool = Field(True, description="Whether to validate after normalization")

class TestDataRequest(BaseModel):
    """Request model for test data generation"""
    count: int = Field(10, ge=1, le=1000, description="Number of test claims to generate")
    payer_format: str = Field("bupa", description="Payer format for test data: bupa, globemed, waseel")
    include_rejection_cases: bool = Field(False, description="Include rejection test scenarios")

class ValidationResponse(BaseModel):
    """Response model for validation results"""
    claim_id: str
    validation_status: str
    validation_score: float
    compliance_status: str
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]
    data_quality_metrics: Dict[str, Any]

class NormalizationResponse(BaseModel):
    """Response model for normalization results"""
    claim_id: str
    normalized_data: Dict[str, Any]
    validation_result: Optional[ValidationResponse]
    processing_time: float
    source_format: str
    metadata: Dict[str, Any]

class BatchProcessingResponse(BaseModel):
    """Response model for batch processing"""
    total_claims: int
    successfully_processed: int
    failed: int
    processing_time: float
    results: List[Dict[str, Any]]
    summary_report: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title="ClaimLinc API",
    description="Healthcare Claims Normalization and Automation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Force HTTPS in production
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions Policy
    response.headers["Permissions-Policy"] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "payment=(), "
        "usb=()"
    )

    return response

# Initialize service components
normalizer = ClaimDataNormalizer()
validator = ClaimDataValidator()
test_generator = TestDataGenerator()
report_generator = ReportGenerator()

# Create output directories
output_dirs = {
    "normalized": Path("./data/normalized"),
    "validated": Path("./data/validated"),
    "reports": Path("./reports"),
    "exports": Path("./exports")
}

for dir_path in output_dirs.values():
    dir_path.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 ClaimLinc API Server Starting...")
    print(f"📁 Output directories created: {list(output_dirs.values())}")
    print("✅ System ready for claim processing")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 ClaimLinc API Server Shutting Down...")

@app.get("/", tags=["System"])
async def root():
    """Root endpoint with system information"""
    return {
        "service": "ClaimLinc API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "normalize": "/api/v1/normalize",
            "validate": "/api/v1/validate", 
            "batch_process": "/api/v1/batch",
            "test_data": "/api/v1/test-data",
            "reports": "/api/v1/reports",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    try:
        # Test basic functionality
        test_claim = {"claim_id": "TEST-001", "provider": {"name": "Test"}, "patient": {"member_id": "TEST"}, "claim_details": {"total_amount": 100}}
        normalized = normalizer.normalize_claim(test_claim, "generic")
        validated = validator.validate_claim(normalized)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "normalizer": "operational",
                "validator": "operational",
                "test_generator": "operational"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/api/v1/normalize", response_model=NormalizationResponse, tags=["Processing"])
async def normalize_claim_endpoint(request: ClaimRequest):
    """Normalize a single claim to standard format"""
    try:
        start_time = datetime.now()
        
        # Normalize the claim
        normalized_data = normalizer.normalize_claim(request.claim_data, request.source_format)
        
        # Validate if requested
        validation_result = None
        if request.validation_required and "error" not in normalized_data:
            validation_result = validator.validate_claim(normalized_data)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = NormalizationResponse(
            claim_id=normalized_data.get("claim_id", "UNKNOWN"),
            normalized_data=normalized_data,
            validation_result=ValidationResponse(**validation_result) if validation_result else None,
            processing_time=processing_time,
            source_format=request.source_format,
            metadata={
                "processed_at": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")

@app.post("/api/v1/validate", response_model=ValidationResponse, tags=["Processing"])
async def validate_claim_endpoint(claim_data: Dict[str, Any]):
    """Validate claim data for quality and compliance"""
    try:
        validation_result = validator.validate_claim(claim_data)
        return ValidationResponse(**validation_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.post("/api/v1/batch", response_model=BatchProcessingResponse, tags=["Processing"])
async def batch_process_claims(request: BatchClaimRequest):
    """Process multiple claims in batch"""
    try:
        start_time = datetime.now()
        
        # Normalize all claims
        normalized_claims = batch_normalize_claims(request.claims_data, request.source_format)
        
        # Validate if requested
        validation_results = []
        if request.validation_required:
            for claim in normalized_claims:
                if "error" not in claim:
                    validation_result = validator.validate_claim(claim)
                    claim["validation_result"] = validation_result
                validation_results.append(validation_result)
        
        # Calculate statistics
        total_claims = len(normalized_claims)
        successfully_processed = sum(1 for claim in normalized_claims if "error" not in claim)
        failed = total_claims - successfully_processed
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Generate summary report
        summary_report = {
            "total_claims": total_claims,
            "successfully_processed": successfully_processed,
            "failed": failed,
            "success_rate": round((successfully_processed / total_claims) * 100, 2) if total_claims > 0 else 0,
            "average_processing_time": round(processing_time / total_claims, 3) if total_claims > 0 else 0
        }
        
        response = BatchProcessingResponse(
            total_claims=total_claims,
            successfully_processed=successfully_processed,
            failed=failed,
            processing_time=processing_time,
            results=normalized_claims,
            summary_report=summary_report
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.post("/api/v1/test-data/generate", tags=["Test Data"])
async def generate_test_data_endpoint(request: TestDataRequest):
    """Generate synthetic test data"""
    try:
        # Generate claims
        claims = test_generator.generate_batch_claims(request.count, request.payer_format)
        
        # Add rejection cases if requested
        if request.include_rejection_cases:
            rejection_cases = test_generator.generate_rejection_scenarios(request.payer_format)
            claims.extend(rejection_cases)
        
        # Generate summary report
        report_path = report_generator.generate_summary_report(
            claims, 
            f"test_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        return {
            "generated_claims": len(claims),
            "claims": claims,
            "report": report_path,
            "payer_format": request.payer_format,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test data generation failed: {str(e)}")

@app.get("/api/v1/reports/summary", tags=["Reports"])
async def get_summary_report(claims_data: List[Dict[str, Any]]):
    """Generate and return summary report"""
    try:
        report_path = report_generator.generate_summary_report(claims_data)
        
        # Read and return the report
        if isinstance(report_path, str):
            # Extract file path from the string
            json_path = report_path.split(" and ")[0]  # Get first file (JSON)
            if json_path.endswith(".json"):
                with open(json_path, 'r') as f:
                    report_data = json.load(f)
                return {
                    "report": report_data,
                    "report_file": json_path,
                    "generated_at": datetime.now().isoformat()
                }
        
        return {"message": "Report generated", "details": report_path}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.post("/api/v1/automation/submit/{payer}", tags=["Automation"])
async def submit_claim_to_payer(payer: str, claim_data: Dict[str, Any]):
    """Submit claim to specific payer automation workflow"""
    try:
        payer = payer.lower()
        
        # This would integrate with the n8n workflows
        if payer == "bupa":
            webhook_url = "http://localhost:5678/webhook/claimlinc-bupa"
        elif payer == "globemed":
            webhook_url = "http://localhost:5678/webhook/claimlinc-globemed"
        elif payer == "waseel":
            webhook_url = "http://localhost:5678/webhook/claimlinc-waseel"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported payer: {payer}")
        
        # Normalize and validate before submission
        normalized = normalizer.normalize_claim(claim_data, "generic")
        if "error" not in normalized:
            validation = validator.validate_claim(normalized)
            
            # Submit to workflow (this would make actual HTTP request to n8n)
            # For now, return success with mock data
            return {
                "status": "submitted",
                "payer": payer,
                "submission_id": f"{payer.upper()}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
                "normalized_claim": normalized,
                "validation_result": validation,
                "next_steps": [
                    "Monitor submission status",
                    "Check for rejections",
                    "Review payment processing"
                ]
            }
        else:
            raise HTTPException(status_code=400, detail=f"Normalization failed: {normalized.get('error')}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

@app.get("/api/v1/workflow/status/{submission_id}", tags=["Automation"])
async def get_workflow_status(submission_id: str):
    """Check status of submitted workflow"""
    try:
        # This would query n8n workflow status
        # Mock implementation for now
        return {
            "submission_id": submission_id,
            "status": "processing",
            "current_step": "claim_submission",
            "estimated_completion": "2-5 minutes",
            "next_steps": ["portal_login", "claim_upload", "confirmation"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/api/v1/export/csv", tags=["Export"])
async def export_to_csv(claims_data: List[Dict[str, Any]], filename: Optional[str] = None):
    """Export claims to CSV format"""
    try:
        if not filename:
            filename = f"claims_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        csv_path = output_dirs["exports"] / filename
        
        # Use normalizer's export functionality
        export_result = normalizer.export_to_csv(claims_data, str(csv_path))
        
        return {
            "export_result": export_result,
            "file_path": str(csv_path),
            "download_url": f"/api/v1/download/{filename}",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/api/v1/download/{filename}", tags=["Export"])
async def download_file(filename: str):
    """Download exported file"""
    try:
        file_path = output_dirs["exports"] / filename
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                filename=filename,
                media_type="text/csv"
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/api/v1/system/stats", tags=["System"])
async def get_system_stats():
    """Get system statistics and health metrics"""
    try:
        return {
            "uptime": "Running",
            "memory_usage": "Normal",
            "processing_capacity": "Available",
            "supported_payers": ["bupa", "globemed", "waseel"],
            "api_version": "1.0.0",
            "endpoints_available": [
                "/api/v1/normalize",
                "/api/v1/validate",
                "/api/v1/batch",
                "/api/v1/test-data/generate",
                "/api/v1/automation/submit/{payer}",
                "/api/v1/export/csv"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting ClaimLinc FastAPI Server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
