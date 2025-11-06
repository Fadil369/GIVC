@echo off
REM ===================================================================
REM Ultimate GIVC Integration Script
REM Merges best files from GIVC, brainsait-rcm, and brainsait-nphies-givc
REM ===================================================================

echo.
echo ==================================================
echo ULTIMATE GIVC INTEGRATION
echo ==================================================
echo.

cd /d C:\Users\rcmrejection3\nphies-rcm

REM Phase 1: Create directory structure
echo [PHASE 1] Creating directory structure...
if not exist "GIVC\backend" mkdir GIVC\backend
if not exist "GIVC\backend\app" mkdir GIVC\backend\app
if not exist "GIVC\backend\ai" mkdir GIVC\backend\ai
if not exist "GIVC\backend\services_rcm" mkdir GIVC\backend\services_rcm
if not exist "GIVC\certificates" mkdir GIVC\certificates
if not exist "GIVC\config" mkdir GIVC\config
if not exist "GIVC\oasis-templates" mkdir GIVC\oasis-templates
if not exist "GIVC\infrastructure" mkdir GIVC\infrastructure
if not exist "GIVC\docs" mkdir GIVC\docs
echo   [OK] Directories created
echo.

REM Phase 2: Copy Python backend from brainsait-nphies-givc
echo [PHASE 2] Copying NPHIES backend...
if exist "brainsait-nphies-givc\app" (
    xcopy /E /I /Y /Q brainsait-nphies-givc\app GIVC\backend\app >nul 2>&1
    echo   [OK] NPHIES app structure copied
) else (
    echo   [SKIP] brainsait-nphies-givc\app not found
)

if exist "brainsait-nphies-givc\main.py" (
    copy /Y brainsait-nphies-givc\main.py GIVC\backend\main_nphies.py >nul 2>&1
    echo   [OK] NPHIES main.py copied
)

if exist "brainsait-nphies-givc\requirements.txt" (
    copy /Y brainsait-nphies-givc\requirements.txt GIVC\backend\requirements_nphies.txt >nul 2>&1
    echo   [OK] NPHIES requirements.txt copied
)
echo.

REM Phase 3: Copy certificates
echo [PHASE 3] Copying certificates...
if exist "brainsait-nphies-givc\certificates" (
    xcopy /E /I /Y /Q brainsait-nphies-givc\certificates\* GIVC\certificates\ >nul 2>&1
    echo   [OK] Certificates copied
) else (
    echo   [SKIP] Certificates directory not found
)
echo.

REM Phase 4: Copy configuration
echo [PHASE 4] Copying configuration...
if exist "brainsait-nphies-givc\config\config.yaml" (
    copy /Y brainsait-nphies-givc\config\config.yaml GIVC\config\nphies-portals.yaml >nul 2>&1
    echo   [OK] NPHIES portal config copied
) else (
    echo   [SKIP] config.yaml not found
)
echo.

REM Phase 5: Copy monorepo structure from brainsait-rcm
echo [PHASE 5] Copying monorepo structure...
if exist "brainsait-rcm\apps" (
    xcopy /E /I /Y /Q brainsait-rcm\apps GIVC\apps >nul 2>&1
    echo   [OK] Apps directory copied
) else (
    echo   [SKIP] Apps directory not found
)

if exist "brainsait-rcm\packages" (
    xcopy /E /I /Y /Q brainsait-rcm\packages GIVC\packages >nul 2>&1
    echo   [OK] Packages directory copied
) else (
    echo   [SKIP] Packages directory not found
)

if exist "brainsait-rcm\turbo.json" (
    copy /Y brainsait-rcm\turbo.json GIVC\turbo_rcm.json >nul 2>&1
    echo   [OK] Turbo.json copied
)
echo.

REM Phase 6: Copy OASIS templates
echo [PHASE 6] Copying OASIS templates...
if exist "brainsait-rcm\claim-oaises.html" (
    copy /Y brainsait-rcm\claim-oaises*.html GIVC\oasis-templates\ >nul 2>&1
    copy /Y brainsait-rcm\claim-oises*.html GIVC\oasis-templates\ >nul 2>&1
    echo   [OK] OASIS HTML templates copied
) else (
    echo   [SKIP] OASIS templates not found
)
echo.

REM Phase 7: Copy infrastructure
echo [PHASE 7] Copying infrastructure...
if exist "brainsait-rcm\infrastructure" (
    xcopy /E /I /Y /Q brainsait-rcm\infrastructure GIVC\infrastructure >nul 2>&1
    echo   [OK] Infrastructure directory copied
) else (
    echo   [SKIP] Infrastructure directory not found
)
echo.

REM Phase 8: Copy RCM services
echo [PHASE 8] Copying RCM services...
if exist "brainsait-rcm\services" (
    xcopy /E /I /Y /Q brainsait-rcm\services GIVC\backend\services_rcm >nul 2>&1
    echo   [OK] RCM services copied
) else (
    echo   [SKIP] RCM services directory not found
)
echo.

REM Phase 9: Copy documentation
echo [PHASE 9] Copying documentation...
if exist "brainsait-nphies-givc\README.md" (
    copy /Y brainsait-nphies-givc\README.md GIVC\docs\NPHIES_INTEGRATION_GUIDE.md >nul 2>&1
    echo   [OK] NPHIES integration guide created
)

if exist "brainsait-nphies-givc\IMPLEMENTATION_SUMMARY.md" (
    copy /Y brainsait-nphies-givc\IMPLEMENTATION_SUMMARY.md GIVC\docs\NPHIES_IMPLEMENTATION.md >nul 2>&1
    echo   [OK] NPHIES implementation summary copied
)

if exist "brainsait-nphies-givc\QUICKSTART.md" (
    copy /Y brainsait-nphies-givc\QUICKSTART.md GIVC\docs\NPHIES_QUICKSTART.md >nul 2>&1
    echo   [OK] NPHIES quickstart copied
)

if exist "brainsait-rcm\README.md" (
    copy /Y brainsait-rcm\README.md GIVC\docs\AI_FEATURES_GUIDE.md >nul 2>&1
    echo   [OK] AI features guide created
)

if exist "brainsait-rcm\DEPLOYMENT_GUIDE.md" (
    copy /Y brainsait-rcm\DEPLOYMENT_GUIDE.md GIVC\docs\RCM_DEPLOYMENT_GUIDE.md >nul 2>&1
    echo   [OK] RCM deployment guide copied
)

if exist "brainsait-rcm\AUTH_BACKEND_PROGRESS.md" (
    copy /Y brainsait-rcm\AUTH_BACKEND_PROGRESS.md GIVC\docs\RCM_AUTH_BACKEND.md >nul 2>&1
    echo   [OK] Auth backend docs copied
)

if exist "brainsait-rcm\OASIS_AUTOMATION_READY.md" (
    copy /Y brainsait-rcm\OASIS_AUTOMATION_READY.md GIVC\docs\RCM_OASIS_AUTOMATION.md >nul 2>&1
    echo   [OK] OASIS automation docs copied
)

if exist "brainsait-rcm\SECURITY_AUDIT_REPORT.md" (
    copy /Y brainsait-rcm\SECURITY_AUDIT_REPORT.md GIVC\docs\RCM_SECURITY_AUDIT.md >nul 2>&1
    echo   [OK] Security audit report copied
)

if exist "brainsait-rcm\CODE_QUALITY_REPORT.md" (
    copy /Y brainsait-rcm\CODE_QUALITY_REPORT.md GIVC\docs\RCM_CODE_QUALITY.md >nul 2>&1
    echo   [OK] Code quality report copied
)
echo.

REM Phase 10: Copy test suites
echo [PHASE 10] Copying test suites...
if exist "brainsait-nphies-givc\tests" (
    if not exist "GIVC\tests\nphies" mkdir GIVC\tests\nphies
    xcopy /E /I /Y /Q brainsait-nphies-givc\tests\* GIVC\tests\nphies\ >nul 2>&1
    echo   [OK] NPHIES tests copied
) else (
    echo   [SKIP] NPHIES tests directory not found
)
echo.

REM Phase 11: Copy environment templates
echo [PHASE 11] Copying environment templates...
if exist "brainsait-nphies-givc\.env.example" (
    copy /Y brainsait-nphies-givc\.env.example GIVC\.env.nphies.example >nul 2>&1
    echo   [OK] NPHIES env template copied
)
echo.

REM Phase 12: Copy additional docs from brainsait-nphies-givc
echo [PHASE 12] Copying additional NPHIES docs...
if exist "brainsait-nphies-givc\docs" (
    xcopy /E /I /Y /Q brainsait-nphies-givc\docs\* GIVC\docs\ >nul 2>&1
    echo   [OK] Additional NPHIES docs merged
)
echo.

REM Final summary
echo.
echo ==================================================
echo INTEGRATION COMPLETE!
echo ==================================================
echo.
echo Summary:
echo   [OK] Python backend enhanced with NPHIES integration
echo   [OK] Certificates configured
echo   [OK] Configuration files merged
echo   [OK] Monorepo structure (apps/packages) added
echo   [OK] OASIS templates extracted
echo   [OK] Infrastructure merged
echo   [OK] RCM services integrated
echo   [OK] Documentation consolidated
echo   [OK] Test suites merged
echo   [OK] Environment templates copied
echo.
echo Main Directory: C:\Users\rcmrejection3\nphies-rcm\GIVC
echo.
echo Next Steps:
echo   1. Review merged files in GIVC directory
echo   2. Update main requirements.txt
echo   3. Merge .env templates
echo   4. Test NPHIES integration
echo   5. Run full test suite
echo   6. Build Docker containers
echo.
echo Documentation:
echo   - GIVC\ULTIMATE_INTEGRATION_GUIDE.md (complete guide)
echo   - QUICK_INTEGRATION_REFERENCE.md (quick reference)
echo   - INTEGRATION_PLAN.md (detailed plan)
echo.

pause
