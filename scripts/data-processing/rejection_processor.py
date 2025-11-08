"""
ClaimLinc Rejection Sheet Processor
Handles extraction, normalization, and analysis of claim rejection reports
from payer portals (Bupa, GlobeMed, Tawuniya/Waseel)
"""

import json
import pandas as pd
import openpyxl
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import re
from enum import Enum


class RejectionReasonCode(str, Enum):
    """Standardized rejection reason codes"""
    INVALID_MEMBER_ID = "INVALID_MEMBER"
    MISSING_AUTH = "MISSING_AUTH"
    SERVICE_NOT_COVERED = "SERVICE_NOT_COVERED"
    EXCEEDS_LIMIT = "EXCEEDS_LIMIT"
    DUPLICATE_CLAIM = "DUPLICATE_CLAIM"
    INVALID_DATE = "INVALID_DATE"
    INCOMPLETE_DOCUMENTATION = "INCOMPLETE_DOCS"
    MISSING_DIAGNOSIS = "MISSING_DIAGNOSIS"
    INVALID_PROCEDURE_CODE = "INVALID_PROCEDURE"
    OUT_OF_NETWORK = "OUT_OF_NETWORK"
    AMOUNT_EXCEEDS_BENEFIT = "AMOUNT_EXCEEDS_BENEFIT"
    PRE_EXISTING_CONDITION = "PRE_EXISTING"
    MEDICAL_NECESSITY = "MEDICAL_NECESSITY"
    MISSING_REFERRAL = "MISSING_REFERRAL"
    INCORRECT_PROVIDER = "INCORRECT_PROVIDER"
    PATIENT_INELIGIBLE = "PATIENT_INELIGIBLE"
    CLAIM_TIMELINE_EXCEEDED = "CLAIM_TIMELINE"
    OTHER = "OTHER"


class RejectionSeverity(str, Enum):
    """Rejection severity levels"""
    CRITICAL = "critical"      # Claim cannot be resubmitted as-is
    HIGH = "high"              # Major issue, significant rework needed
    MEDIUM = "medium"          # Minor corrections needed
    LOW = "low"                # Informational or warning


@dataclass
class RejectionRecord:
    """Standardized rejection record"""
    claim_id: str
    payer_name: str
    rejection_date: str
    reason_code: str
    reason_description: str
    severity: str
    patient_member_id: str
    patient_name: Optional[str] = None
    provider_name: Optional[str] = None
    provider_code: Optional[str] = None
    branch: Optional[str] = None
    service_date: Optional[str] = None
    claim_amount: Optional[float] = None
    corrective_action: Optional[str] = None
    reference_number: Optional[str] = None
    appeal_deadline: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None
    source_file: Optional[str] = None
    processed_at: str = None

    def __post_init__(self):
        if self.processed_at is None:
            self.processed_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class RejectionProcessor:
    """Processes rejection sheets from various payer formats"""

    def __init__(self):
        self.branch_mapping = self._get_branch_mapping()
        self.rejection_mapping = self._get_rejection_mapping()

    def _get_branch_mapping(self) -> Dict[str, str]:
        """Get standardized branch name mapping"""
        return {
            "riyadh": "MainRiyadh",
            "main riyadh": "MainRiyadh",
            "unaizah": "Unaizah",
            "unizah": "Unaizah",
            "abha": "Abha",
            "madinah": "Madinah",
            "medina": "Madinah",
            "khamis": "Khamis",
            "khamis mushait": "Khamis",
            "mushait": "Khamis"
        }

    def _get_rejection_mapping(self) -> Dict[str, Tuple[str, str]]:
        """
        Get mapping of payer-specific rejection reasons to standardized codes.
        Returns tuple of (code, severity)
        """
        return {
            # Bupa Arabia mappings
            "invalid member id": (RejectionReasonCode.INVALID_MEMBER_ID, RejectionSeverity.HIGH),
            "member not found": (RejectionReasonCode.INVALID_MEMBER_ID, RejectionSeverity.HIGH),
            "no active membership": (RejectionReasonCode.PATIENT_INELIGIBLE, RejectionSeverity.HIGH),
            "membership expired": (RejectionReasonCode.PATIENT_INELIGIBLE, RejectionSeverity.MEDIUM),
            "service not covered": (RejectionReasonCode.SERVICE_NOT_COVERED, RejectionSeverity.MEDIUM),
            "authorization required": (RejectionReasonCode.MISSING_AUTH, RejectionSeverity.HIGH),
            "pre-auth required": (RejectionReasonCode.MISSING_AUTH, RejectionSeverity.HIGH),

            # GlobeMed mappings
            "duplicate claim": (RejectionReasonCode.DUPLICATE_CLAIM, RejectionSeverity.CRITICAL),
            "claim already submitted": (RejectionReasonCode.DUPLICATE_CLAIM, RejectionSeverity.CRITICAL),
            "invalid date": (RejectionReasonCode.INVALID_DATE, RejectionSeverity.MEDIUM),
            "service date outside policy": (RejectionReasonCode.INVALID_DATE, RejectionSeverity.MEDIUM),
            "incomplete documentation": (RejectionReasonCode.INCOMPLETE_DOCUMENTATION, RejectionSeverity.HIGH),
            "missing invoice": (RejectionReasonCode.INCOMPLETE_DOCUMENTATION, RejectionSeverity.HIGH),
            "missing diagnosis": (RejectionReasonCode.MISSING_DIAGNOSIS, RejectionSeverity.HIGH),
            "invalid procedure code": (RejectionReasonCode.INVALID_PROCEDURE_CODE, RejectionSeverity.MEDIUM),

            # Waseel/Tawuniya mappings
            "out of network": (RejectionReasonCode.OUT_OF_NETWORK, RejectionSeverity.HIGH),
            "non-network provider": (RejectionReasonCode.OUT_OF_NETWORK, RejectionSeverity.HIGH),
            "amount exceeds benefit limit": (RejectionReasonCode.EXCEEDS_LIMIT, RejectionSeverity.MEDIUM),
            "exceeds annual limit": (RejectionReasonCode.EXCEEDS_LIMIT, RejectionSeverity.MEDIUM),
            "pre-existing condition": (RejectionReasonCode.PRE_EXISTING_CONDITION, RejectionSeverity.CRITICAL),
            "medical necessity not documented": (RejectionReasonCode.MEDICAL_NECESSITY, RejectionSeverity.MEDIUM),
            "referral required": (RejectionReasonCode.MISSING_REFERRAL, RejectionSeverity.HIGH),
            "missing referral": (RejectionReasonCode.MISSING_REFERRAL, RejectionSeverity.HIGH),
            "incorrect provider": (RejectionReasonCode.INCORRECT_PROVIDER, RejectionSeverity.HIGH),
            "claim timeline exceeded": (RejectionReasonCode.CLAIM_TIMELINE_EXCEEDED, RejectionSeverity.CRITICAL),
        }

    def process_rejection_sheet(self, file_path: str, payer: str) -> List[RejectionRecord]:
        """
        Process a rejection sheet from a specific payer

        Args:
            file_path: Path to the rejection file (Excel or CSV)
            payer: Payer name (bupa, globemed, waseel)

        Returns:
            List of standardized RejectionRecord objects
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            if file_path.suffix.lower() in ['.xls', '.xlsx']:
                return self._process_excel_sheet(file_path, payer)
            elif file_path.suffix.lower() == '.csv':
                return self._process_csv_sheet(file_path, payer)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        except Exception as e:
            raise ValueError(f"Failed to process rejection sheet: {str(e)}")

    def _process_excel_sheet(self, file_path: Path, payer: str) -> List[RejectionRecord]:
        """Process Excel rejection sheet"""
        df = pd.read_excel(file_path, sheet_name=0)
        return self._normalize_rejection_dataframe(df, payer, file_path)

    def _process_csv_sheet(self, file_path: Path, payer: str) -> List[RejectionRecord]:
        """Process CSV rejection sheet"""
        df = pd.read_csv(file_path)
        return self._normalize_rejection_dataframe(df, payer, file_path)

    def _normalize_rejection_dataframe(
        self, df: pd.DataFrame, payer: str, file_path: Path
    ) -> List[RejectionRecord]:
        """
        Normalize rejection data from DataFrame based on payer format

        Args:
            df: DataFrame containing rejection data
            payer: Payer name
            file_path: Original file path

        Returns:
            List of RejectionRecord objects
        """
        records = []

        if payer.lower() == "bupa":
            records = self._normalize_bupa_rejections(df, file_path)
        elif payer.lower() == "globemed":
            records = self._normalize_globemed_rejections(df, file_path)
        elif payer.lower() in ["waseel", "tawuniya"]:
            records = self._normalize_waseel_rejections(df, file_path)
        else:
            records = self._normalize_generic_rejections(df, payer, file_path)

        return records

    def _normalize_bupa_rejections(self, df: pd.DataFrame, file_path: Path) -> List[RejectionRecord]:
        """
        Normalize Bupa Arabia rejection format
        Expected columns: Claim ID, Member ID, Service Date, Rejection Reason, etc.
        """
        records = []

        for idx, row in df.iterrows():
            try:
                claim_id = str(row.get("Claim ID", row.get("claim_id", f"BPA-{idx}")))
                member_id = str(row.get("Member ID", row.get("member_id", "")))
                reason = str(row.get("Rejection Reason", row.get("reason", "")))

                code, severity = self._classify_rejection(reason)
                branch = self._normalize_branch(row.get("Branch", "MainRiyadh"))

                record = RejectionRecord(
                    claim_id=claim_id,
                    payer_name="Bupa Arabia",
                    rejection_date=self._normalize_date(row.get("Rejection Date", row.get("date"))),
                    reason_code=code,
                    reason_description=reason,
                    severity=severity,
                    patient_member_id=member_id,
                    patient_name=row.get("Member Name", row.get("patient_name")),
                    provider_name="Al Hayat Hospital",
                    provider_code="AH001",
                    branch=branch,
                    service_date=self._normalize_date(row.get("Service Date")),
                    claim_amount=self._safe_float(row.get("Claim Amount")),
                    reference_number=row.get("Reference Number", row.get("ref_no")),
                    appeal_deadline=self._normalize_date(row.get("Appeal Deadline")),
                    source_file=str(file_path),
                    additional_info=self._extract_additional_info(row)
                )
                records.append(record)
            except Exception as e:
                print(f"Warning: Failed to process Bupa rejection row {idx}: {str(e)}")
                continue

        return records

    def _normalize_globemed_rejections(self, df: pd.DataFrame, file_path: Path) -> List[RejectionRecord]:
        """
        Normalize GlobeMed rejection format
        Expected columns: ClaimID, SubscriberID, RejectionReason, etc.
        """
        records = []

        for idx, row in df.iterrows():
            try:
                claim_id = str(row.get("ClaimID", row.get("Claim ID", f"GLB-{idx}")))
                member_id = str(row.get("SubscriberID", row.get("Member ID", "")))
                reason = str(row.get("RejectionReason", row.get("Reason", "")))

                code, severity = self._classify_rejection(reason)
                branch = self._normalize_branch(row.get("Branch"))

                record = RejectionRecord(
                    claim_id=claim_id,
                    payer_name="GlobeMed",
                    rejection_date=self._normalize_date(row.get("RejectionDate", row.get("Rejection Date"))),
                    reason_code=code,
                    reason_description=reason,
                    severity=severity,
                    patient_member_id=member_id,
                    patient_name=row.get("SubscriberName", row.get("Patient Name")),
                    provider_name="Al Hayat Hospital",
                    provider_code="AH001",
                    branch=branch,
                    service_date=self._normalize_date(row.get("ServiceDate", row.get("Service Date"))),
                    claim_amount=self._safe_float(row.get("ClaimAmount", row.get("Amount"))),
                    reference_number=row.get("ReferenceNumber", row.get("Reference")),
                    appeal_deadline=self._normalize_date(row.get("AppealDeadline")),
                    source_file=str(file_path),
                    additional_info=self._extract_additional_info(row)
                )
                records.append(record)
            except Exception as e:
                print(f"Warning: Failed to process GlobeMed rejection row {idx}: {str(e)}")
                continue

        return records

    def _normalize_waseel_rejections(self, df: pd.DataFrame, file_path: Path) -> List[RejectionRecord]:
        """
        Normalize Waseel/Tawuniya FHIR-based rejection format
        Expected columns: Claim Reference, Subscriber ID, Response Reason, etc.
        """
        records = []

        for idx, row in df.iterrows():
            try:
                claim_id = str(row.get("Claim Reference", row.get("ClaimID", f"WSE-{idx}")))
                member_id = str(row.get("Subscriber ID", row.get("SubscriberID", "")))
                reason = str(row.get("Response Reason", row.get("Reason", "")))

                code, severity = self._classify_rejection(reason)
                branch = self._normalize_branch(row.get("Branch", "MainRiyadh"))

                record = RejectionRecord(
                    claim_id=claim_id,
                    payer_name="Tawuniya/Waseel",
                    rejection_date=self._normalize_date(row.get("Response Date", row.get("Date"))),
                    reason_code=code,
                    reason_description=reason,
                    severity=severity,
                    patient_member_id=member_id,
                    patient_name=row.get("Subscriber Name", row.get("Patient Name")),
                    provider_name="Al Hayat Hospital",
                    provider_code="AH001",
                    branch=branch,
                    service_date=self._normalize_date(row.get("Service Date")),
                    claim_amount=self._safe_float(row.get("Claim Amount")),
                    reference_number=row.get("NPHIES Reference", row.get("Reference")),
                    appeal_deadline=self._normalize_date(row.get("Appeal Deadline")),
                    source_file=str(file_path),
                    additional_info=self._extract_additional_info(row)
                )
                records.append(record)
            except Exception as e:
                print(f"Warning: Failed to process Waseel rejection row {idx}: {str(e)}")
                continue

        return records

    def _normalize_generic_rejections(
        self, df: pd.DataFrame, payer: str, file_path: Path
    ) -> List[RejectionRecord]:
        """Normalize generic/unknown rejection format"""
        records = []

        # Attempt to identify key columns
        claim_col = self._find_column(df, ["claim_id", "claimid", "claim", "id"])
        member_col = self._find_column(df, ["member_id", "memberid", "subscriber_id", "patient_id"])
        reason_col = self._find_column(df, ["reason", "rejection_reason", "status"])
        date_col = self._find_column(df, ["date", "rejection_date", "response_date"])
        amount_col = self._find_column(df, ["amount", "claim_amount", "total"])

        for idx, row in df.iterrows():
            try:
                claim_id = str(row.get(claim_col, f"{payer.upper()}-{idx}")) if claim_col else f"{payer.upper()}-{idx}"
                member_id = str(row.get(member_col, "")) if member_col else ""
                reason = str(row.get(reason_col, "Unknown")) if reason_col else "Unknown"

                code, severity = self._classify_rejection(reason)

                record = RejectionRecord(
                    claim_id=claim_id,
                    payer_name=payer,
                    rejection_date=self._normalize_date(row.get(date_col)) if date_col else datetime.now().isoformat(),
                    reason_code=code,
                    reason_description=reason,
                    severity=severity,
                    patient_member_id=member_id,
                    claim_amount=self._safe_float(row.get(amount_col)) if amount_col else None,
                    branch="MainRiyadh",
                    source_file=str(file_path),
                    additional_info=self._extract_additional_info(row)
                )
                records.append(record)
            except Exception as e:
                print(f"Warning: Failed to process generic rejection row {idx}: {str(e)}")
                continue

        return records

    def _classify_rejection(self, reason_text: str) -> Tuple[str, str]:
        """
        Classify rejection reason to standardized code and severity

        Returns:
            Tuple of (reason_code, severity)
        """
        if not reason_text:
            return RejectionReasonCode.OTHER, RejectionSeverity.LOW

        reason_lower = reason_text.lower().strip()

        # Try exact matches first
        for key, (code, severity) in self.rejection_mapping.items():
            if reason_lower == key:
                return code, severity

        # Try substring matches
        for key, (code, severity) in self.rejection_mapping.items():
            if key in reason_lower:
                return code, severity

        # Default to OTHER
        return RejectionReasonCode.OTHER, RejectionSeverity.LOW

    def _normalize_branch(self, branch_value: Any) -> str:
        """Normalize branch name"""
        if not branch_value:
            return "MainRiyadh"

        branch_str = str(branch_value).lower().strip()
        return self.branch_mapping.get(branch_str, "MainRiyadh")

    def _normalize_date(self, date_value: Any) -> str:
        """Normalize date to ISO format"""
        if not date_value:
            return datetime.now().isoformat()

        try:
            if isinstance(date_value, datetime):
                return date_value.isoformat()
            elif isinstance(date_value, date):
                return date_value.isoformat()

            # Try parsing string dates
            date_str = str(date_value).strip()
            formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%Y-%m-%d %H:%M:%S",
                "%d-%m-%Y"
            ]

            for fmt in formats:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.isoformat()
                except ValueError:
                    continue

            return date_str
        except Exception:
            return datetime.now().isoformat()

    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column by checking multiple possible names"""
        for col in df.columns:
            col_lower = col.lower().replace("_", "").replace(" ", "")
            for name in possible_names:
                name_lower = name.lower().replace("_", "").replace(" ", "")
                if col_lower == name_lower or name_lower in col_lower:
                    return col
        return None

    def _extract_additional_info(self, row: pd.Series) -> Dict[str, Any]:
        """Extract additional information from row"""
        # Exclude common processed fields
        exclude_fields = {
            "claim_id", "claimid", "member_id", "memberid", "subscriber_id",
            "reason", "rejection_reason", "date", "rejection_date", "amount",
            "claim_amount", "branch", "name", "patient_name", "service_date"
        }

        additional = {}
        for col, value in row.items():
            col_lower = str(col).lower().replace("_", "").replace(" ", "")
            if col_lower not in exclude_fields and pd.notna(value):
                additional[str(col)] = str(value)

        return additional if additional else None

    def export_rejections_to_csv(self, records: List[RejectionRecord], output_path: str) -> str:
        """Export rejection records to CSV"""
        df = pd.DataFrame([r.to_dict() for r in records])
        df.to_csv(output_path, index=False)
        return f"Exported {len(records)} rejection records to {output_path}"

    def generate_branch_summary(self, records: List[RejectionRecord]) -> Dict[str, Any]:
        """Generate summary of rejections by branch"""
        summary = {
            "total_rejections": len(records),
            "rejection_date_range": {
                "from": min(r.rejection_date for r in records) if records else None,
                "to": max(r.rejection_date for r in records) if records else None
            },
            "by_branch": {},
            "by_payer": {},
            "by_severity": {},
            "by_reason_code": {},
            "critical_issues": []
        }

        # Group by branch
        for record in records:
            branch = record.branch or "Unknown"
            if branch not in summary["by_branch"]:
                summary["by_branch"][branch] = {
                    "count": 0,
                    "amount": 0.0,
                    "records": []
                }
            summary["by_branch"][branch]["count"] += 1
            if record.claim_amount:
                summary["by_branch"][branch]["amount"] += record.claim_amount
            summary["by_branch"][branch]["records"].append(record.to_dict())

        # Group by payer
        for record in records:
            payer = record.payer_name
            if payer not in summary["by_payer"]:
                summary["by_payer"][payer] = {"count": 0}
            summary["by_payer"][payer]["count"] += 1

        # Group by severity
        for record in records:
            severity = record.severity
            if severity not in summary["by_severity"]:
                summary["by_severity"][severity] = {"count": 0, "records": []}
            summary["by_severity"][severity]["count"] += 1
            if severity in [RejectionSeverity.CRITICAL, RejectionSeverity.HIGH]:
                summary["by_severity"][severity]["records"].append(record.to_dict())

        # Group by reason code
        for record in records:
            code = record.reason_code
            if code not in summary["by_reason_code"]:
                summary["by_reason_code"][code] = {"count": 0}
            summary["by_reason_code"][code]["count"] += 1

        # Extract critical issues
        summary["critical_issues"] = [
            r.to_dict() for r in records
            if r.severity in [RejectionSeverity.CRITICAL, RejectionSeverity.HIGH]
        ]

        return summary


# Utility functions
def process_rejection_file(file_path: str, payer: str) -> List[RejectionRecord]:
    """Utility function to process a rejection file"""
    processor = RejectionProcessor()
    return processor.process_rejection_sheet(file_path, payer)


def generate_rejection_summary(records: List[RejectionRecord]) -> Dict[str, Any]:
    """Utility function to generate rejection summary"""
    processor = RejectionProcessor()
    return processor.generate_branch_summary(records)


if __name__ == "__main__":
    # Example usage
    processor = RejectionProcessor()
    print("RejectionProcessor initialized")
    print(f"Available rejection codes: {[c.value for c in RejectionReasonCode]}")
    print(f"Severity levels: {[s.value for s in RejectionSeverity]}")
