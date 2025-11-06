# ClaimLinc-GIVC - Centralized Project Structure

**Created:** 2025-11-05 13:03:02
**Purpose:** Consolidated all ClaimLinc and related healthcare automation projects

## Directory Structure

### projects/
Main application projects including:
- ClaimLinc core application
- OAISES+ integration
- Related healthcare automation projects

### nphies-data/
NPHIES (Saudi Arabian National Platform for Health Information Exchange) related files:
- MOH April NPHIES submissions
- NPHIES RCM project
- Jazan August exports

### branches/
Branch-specific files organized by branch code:
- 484600-khamis/ - Khamis Mushait branch files
  - extractors/
  - models/
  - scripts/

### analysis/
Data analysis and reporting projects:
- Specific analysis tools
- Custom reports
- Performance analytics

### extractors/
Data extraction utilities for various sources

### models/
Data models and schemas

### scripts/
Automation scripts and utilities

### exports/
Exported data and reports

### config/
Configuration files and references:
- Price lists
- System configurations
- Credentials (encrypted)

### archives/
Historical data and backups

### docs/
Project documentation

## Quick Start

1. **Main Application:**
   - Navigate to projects/claimlinc/
   - Follow README instructions

2. **NPHIES Operations:**
   - Check nphies-data/ for submissions
   - Use nphies-rcm/ for RCM integration

3. **Branch-Specific Work:**
   - Branch files in branches/[branch-code]/

## Migration Statistics

- **Total Items Migrated:** 10
- **Items Skipped:** 1
- **Errors Encountered:** 0
- **Migration Date:** 2025-11-05

## Security Notes

- All credentials stored in encrypted format
- PHI data handled per PDPL compliance
- Audit logs maintained in logs/

## Maintenance

- Regular backups to archives/
- Update documentation in docs/
- Review access permissions quarterly

## Support

Contact: Dr. Fadil - BrainSAIT LTD
Email: support@brainsait.io

---
**BrainSAIT ClaimLinc - Healthcare Automation Excellence**
