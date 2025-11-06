# MIGRATION VERIFICATION REPORT
Generated: 2025-11-05 13:09:36

## STATUS SUMMARY

**Total Items Requested:** 11 items
**Successfully Moved:** 10 items
**Not Found (Skipped):** 1 item
**Partial Moves:** 1 item (needs cleanup)

---

## DETAILED VERIFICATION

###  SUCCESSFULLY MOVED (10 items)

#### 1. OAISES+ Project
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\oaises+
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\projects\oaises+
- **Status:**  Fully moved
- **Contains:** apps/, services/ subdirectories

#### 2. MOH April NPHIES Data
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\MOHAPRILNPHIES
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\nphies-data\MOHAPRILNPHIES
- **Status:**  Fully moved
- **Contains:** analysis_output/, comprehensive_analysis/, globmed_analysis/

#### 3. Files Archive (ZIP)
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\files.zip
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\archives\files.zip
- **Status:**  Fully moved

#### 4. Price List Reference
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\new updated price list.lnk
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\config\new updated price list.lnk
- **Status:**  Fully moved

#### 5. NPHIES RCM Project
- **Original:** C:\Users\rcmrejection3\nphies-rcm
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\nphies-data\nphies-rcm
- **Status:**  Partially moved (main content moved, cleanup folders remain)
- **Contains:** brainsait-nphies-givc/, cleanup_audit_logs/, cleanup_backup_20251028135440/
- **Note:** Some files had path length issues during move (Windows MAX_PATH limitation)

#### 6. Specific Analysis Project
- **Original:** C:\Users\rcmrejection3\projects_linc\specific_analysis
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\analysis\specific_analysis
- **Status:**  Fully moved
- **Contains:** output/ subdirectory

#### 7. Khamis Branch - Extractors
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\484600-khamis\extractors
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\branches\484600-khamis\extractors
- **Status:**  Fully moved

#### 8. Khamis Branch - Models
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\484600-khamis\models
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\branches\484600-khamis\models
- **Status:**  Fully moved

#### 9. Khamis Branch - Scripts
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\484600-khamis\scripts
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\branches\484600-khamis\scripts
- **Status:**  Fully moved

#### 10. NPHIES Jazan August Export
- **Original:** C:\Users\rcmrejection3\OneDrive\Desktop\nphies-export-jazan-aug-extracted
- **New Location:** C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\nphies-data\nphies-export-jazan-aug-extracted
- **Status:**  Fully moved
- **Contains:** nphies-export-jazan-aug/, __MACOSX/

---

###  NOT FOUND (1 item)

#### ClaimLinc Main Project
- **Expected Path:** C:\Users\rcmrejection3\OneDrive\Desktop\claimlinc
- **Status:**  Does not exist at specified location
- **Action:** Skipped (may already be in a different location or renamed)

---

###  CLEANUP REQUIRED

#### Remaining at Original nphies-rcm Location
**Path:** C:\Users\rcmrejection3\nphies-rcm

**Leftover folders:**
- cleanup_backup_20251028154720/
- GIVC/

**Recommendation:** 
- Review these folders for any needed content
- If not needed, delete to complete cleanup
- Main project content successfully moved to ClaimLinc-GIVC\nphies-data\nphies-rcm

---

## FINAL DIRECTORY STRUCTURE

\\\
C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\
 projects/
    oaises+/                    [MOVED FROM Desktop]
 nphies-data/
    MOHAPRILNPHIES/            [MOVED FROM Desktop]
    nphies-rcm/                [MOVED FROM C:\Users\rcmrejection3\]
    nphies-export-jazan-aug-extracted/ [MOVED FROM Desktop]
 branches/
    484600-khamis/
        extractors/            [MOVED FROM Desktop\484600-khamis\]
        models/                [MOVED FROM Desktop\484600-khamis\]
        scripts/               [MOVED FROM Desktop\484600-khamis\]
 analysis/
    specific_analysis/         [MOVED FROM projects_linc\]
 archives/
    files.zip                  [MOVED FROM Desktop]
 config/
    new updated price list.lnk [MOVED FROM Desktop]
 docs/
    README.md                  [AUTO-GENERATED]
    DIRECTORY_INDEX.md         [AUTO-GENERATED]
 [Empty directories ready for future use]
\\\

---

## NEXT STEPS

1.  Review this verification report
2.  Manually check C:\Users\rcmrejection3\nphies-rcm for needed content
3.  Clean up remaining folders if not needed
4.  Update any application config files with new paths
5.  Update environment variables if needed
6.  Test applications with new directory structure

---

## VERIFICATION COMMANDS

To verify contents:
\\\powershell
# List all moved projects
Get-ChildItem "C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC" -Directory

# Count total files
(Get-ChildItem "C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC" -Recurse -File).Count

# Check specific project
Get-ChildItem "C:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC\projects\oaises+"
\\\

---

**Migration Date:** 2025-11-05 13:09:36
**Script:** move-to-claimlinc-givc.ps1
**Status:** SUCCESS (with minor cleanup needed)
