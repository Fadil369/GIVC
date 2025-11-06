# Ultimate GIVC Integration Script
# Merges best files from GIVC, brainsait-rcm, and brainsait-nphies-givc

$ErrorActionPreference = "Stop"

$baseDir = "C:\Users\rcmrejection3\nphies-rcm"
$givcDir = Join-Path $baseDir "GIVC"
$rcmDir = Join-Path $baseDir "brainsait-rcm"
$nphiesDir = Join-Path $baseDir "brainsait-nphies-givc"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "ULTIMATE GIVC INTEGRATION" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Change to base directory
Set-Location $baseDir

# Phase 1: Python Backend Enhancement
Write-Host "[PHASE 1] Enhancing Python Backend..." -ForegroundColor Yellow

# Create backend structure in GIVC
$backendDir = Join-Path $givcDir "backend"
if (-not (Test-Path $backendDir)) {
    New-Item -ItemType Directory -Path $backendDir -Force | Out-Null
}

# Copy app structure from brainsait-nphies-givc
Write-Host "  → Copying NPHIES app structure..." -ForegroundColor Gray
$nphiesAppSource = Join-Path $nphiesDir "app"
$nphiesAppDest = Join-Path $backendDir "app"
if (Test-Path $nphiesAppSource) {
    Copy-Item -Path $nphiesAppSource -Destination $nphiesAppDest -Recurse -Force
    Write-Host "    ✓ NPHIES app structure copied" -ForegroundColor Green
}

# Copy main.py from brainsait-nphies-givc
Write-Host "  → Copying NPHIES main.py..." -ForegroundColor Gray
$nphiesMainSource = Join-Path $nphiesDir "main.py"
$nphiesMainDest = Join-Path $backendDir "main_nphies.py"
if (Test-Path $nphiesMainSource) {
    Copy-Item -Path $nphiesMainSource -Destination $nphiesMainDest -Force
    Write-Host "    ✓ NPHIES main.py copied as main_nphies.py" -ForegroundColor Green
}

# Copy requirements.txt from brainsait-nphies-givc
Write-Host "  → Merging requirements..." -ForegroundColor Gray
$nphiesReqSource = Join-Path $nphiesDir "requirements.txt"
$nphiesReqDest = Join-Path $backendDir "requirements_nphies.txt"
if (Test-Path $nphiesReqSource) {
    Copy-Item -Path $nphiesReqSource -Destination $nphiesReqDest -Force
    Write-Host "    ✓ NPHIES requirements copied" -ForegroundColor Green
}

# Phase 2: Certificates
Write-Host "[PHASE 2] Setting up Certificates..." -ForegroundColor Yellow

$certSource = Join-Path $nphiesDir "certificates"
$certDest = Join-Path $givcDir "certificates"
if (Test-Path $certSource) {
    if (-not (Test-Path $certDest)) {
        New-Item -ItemType Directory -Path $certDest -Force | Out-Null
    }
    Copy-Item -Path "$certSource\*" -Destination $certDest -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Certificates directory synced" -ForegroundColor Green
}

# Phase 3: Configuration Files
Write-Host "[PHASE 3] Merging Configuration..." -ForegroundColor Yellow

# Copy config.yaml from brainsait-nphies-givc
$nphiesConfigSource = Join-Path $nphiesDir "config\config.yaml"
$nphiesConfigDest = Join-Path $givcDir "config\nphies-portals.yaml"
if (Test-Path $nphiesConfigSource) {
    if (-not (Test-Path (Join-Path $givcDir "config"))) {
        New-Item -ItemType Directory -Path (Join-Path $givcDir "config") -Force | Out-Null
    }
    Copy-Item -Path $nphiesConfigSource -Destination $nphiesConfigDest -Force
    Write-Host "  ✓ NPHIES portal config copied" -ForegroundColor Green
}

# Phase 4: Monorepo Structure (from brainsait-rcm)
Write-Host "[PHASE 4] Integrating Monorepo Structure..." -ForegroundColor Yellow

# Copy apps directory
$rcmAppsSource = Join-Path $rcmDir "apps"
$rcmAppsDest = Join-Path $givcDir "apps"
if (Test-Path $rcmAppsSource) {
    Copy-Item -Path $rcmAppsSource -Destination $rcmAppsDest -Recurse -Force
    Write-Host "  ✓ Apps directory copied from brainsait-rcm" -ForegroundColor Green
}

# Copy packages directory
$rcmPackagesSource = Join-Path $rcmDir "packages"
$rcmPackagesDest = Join-Path $givcDir "packages"
if (Test-Path $rcmPackagesSource) {
    Copy-Item -Path $rcmPackagesSource -Destination $rcmPackagesDest -Recurse -Force
    Write-Host "  ✓ Packages directory copied from brainsait-rcm" -ForegroundColor Green
}

# Copy turbo.json
$rcmTurboSource = Join-Path $rcmDir "turbo.json"
$rcmTurboDest = Join-Path $givcDir "turbo_rcm.json"
if (Test-Path $rcmTurboSource) {
    Copy-Item -Path $rcmTurboSource -Destination $rcmTurboDest -Force
    Write-Host "  ✓ Turbo.json copied" -ForegroundColor Green
}

# Phase 5: OASIS Templates
Write-Host "[PHASE 5] Extracting OASIS Templates..." -ForegroundColor Yellow

$oasisTemplatesDir = Join-Path $givcDir "oasis-templates"
if (-not (Test-Path $oasisTemplatesDir)) {
    New-Item -ItemType Directory -Path $oasisTemplatesDir -Force | Out-Null
}

Get-ChildItem -Path $rcmDir -Filter "claim-o*.html" | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $oasisTemplatesDir -Force
    Write-Host "  ✓ Copied $($_.Name)" -ForegroundColor Green
}

# Phase 6: Infrastructure
Write-Host "[PHASE 6] Integrating Infrastructure..." -ForegroundColor Yellow

$rcmInfraSource = Join-Path $rcmDir "infrastructure"
$rcmInfraDest = Join-Path $givcDir "infrastructure"
if (Test-Path $rcmInfraSource) {
    Copy-Item -Path $rcmInfraSource -Destination $rcmInfraDest -Recurse -Force
    Write-Host "  ✓ Infrastructure directory copied" -ForegroundColor Green
}

# Phase 7: Enhanced Services
Write-Host "[PHASE 7] Merging Services..." -ForegroundColor Yellow

$rcmServicesSource = Join-Path $rcmDir "services"
$rcmServicesDest = Join-Path $givcDir "backend\services_rcm"
if (Test-Path $rcmServicesSource) {
    Copy-Item -Path $rcmServicesSource -Destination $rcmServicesDest -Recurse -Force
    Write-Host "  ✓ RCM services copied" -ForegroundColor Green
}

# Phase 8: Documentation
Write-Host "[PHASE 8] Consolidating Documentation..." -ForegroundColor Yellow

$docsDir = Join-Path $givcDir "docs"
if (-not (Test-Path $docsDir)) {
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
}

# Copy NPHIES README as integration guide
$nphiesReadmeSource = Join-Path $nphiesDir "README.md"
$nphiesReadmeDest = Join-Path $docsDir "NPHIES_INTEGRATION_GUIDE.md"
if (Test-Path $nphiesReadmeSource) {
    Copy-Item -Path $nphiesReadmeSource -Destination $nphiesReadmeDest -Force
    Write-Host "  ✓ NPHIES integration guide created" -ForegroundColor Green
}

# Copy RCM README as AI features guide
$rcmReadmeSource = Join-Path $rcmDir "README.md"
$rcmReadmeDest = Join-Path $docsDir "AI_FEATURES_GUIDE.md"
if (Test-Path $rcmReadmeSource) {
    Copy-Item -Path $rcmReadmeSource -Destination $rcmReadmeDest -Force
    Write-Host "  ✓ AI features guide created" -ForegroundColor Green
}

# Copy brainsait-nphies-givc docs
$nphiesDocsSource = Join-Path $nphiesDir "docs"
if (Test-Path $nphiesDocsSource) {
    Copy-Item -Path "$nphiesDocsSource\*" -Destination $docsDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ NPHIES docs merged" -ForegroundColor Green
}

# Copy key markdown files from brainsait-rcm
$keyDocs = @(
    "DEPLOYMENT_GUIDE.md",
    "AUTH_BACKEND_PROGRESS.md",
    "OASIS_AUTOMATION_READY.md",
    "SECURITY_AUDIT_REPORT.md",
    "CODE_QUALITY_REPORT.md"
)

foreach ($doc in $keyDocs) {
    $source = Join-Path $rcmDir $doc
    $dest = Join-Path $docsDir "RCM_$doc"
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "  ✓ Copied $doc" -ForegroundColor Green
    }
}

# Phase 9: Tests
Write-Host "[PHASE 9] Merging Test Suites..." -ForegroundColor Yellow

$testsDir = Join-Path $givcDir "tests"
if (-not (Test-Path $testsDir)) {
    New-Item -ItemType Directory -Path $testsDir -Force | Out-Null
}

# Copy NPHIES tests
$nphiesTestsSource = Join-Path $nphiesDir "tests"
$nphiesTestsDest = Join-Path $testsDir "nphies"
if (Test-Path $nphiesTestsSource) {
    Copy-Item -Path $nphiesTestsSource -Destination $nphiesTestsDest -Recurse -Force
    Write-Host "  ✓ NPHIES tests copied" -ForegroundColor Green
}

# Phase 10: Environment Templates
Write-Host "[PHASE 10] Merging Environment Templates..." -ForegroundColor Yellow

# Copy .env.example from brainsait-nphies-givc if better
$nphiesEnvSource = Join-Path $nphiesDir ".env.example"
$nphiesEnvDest = Join-Path $givcDir ".env.nphies.example"
if (Test-Path $nphiesEnvSource) {
    Copy-Item -Path $nphiesEnvSource -Destination $nphiesEnvDest -Force
    Write-Host "  ✓ NPHIES env template copied" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "INTEGRATION COMPLETE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  ✓ Python backend enhanced with NPHIES integration" -ForegroundColor Green
Write-Host "  ✓ AI features from brainsait-rcm integrated" -ForegroundColor Green
Write-Host "  ✓ Monorepo structure (apps/packages) added" -ForegroundColor Green
Write-Host "  ✓ OASIS templates extracted" -ForegroundColor Green
Write-Host "  ✓ Certificates configured" -ForegroundColor Green
Write-Host "  ✓ Infrastructure merged" -ForegroundColor Green
Write-Host "  ✓ Documentation consolidated" -ForegroundColor Green
Write-Host "  ✓ Test suites merged" -ForegroundColor Green
Write-Host ""
Write-Host "Main Directory: $givcDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review merged files in GIVC directory" -ForegroundColor White
Write-Host "  2. Update main requirements.txt" -ForegroundColor White
Write-Host "  3. Merge .env templates" -ForegroundColor White
Write-Host "  4. Test NPHIES integration" -ForegroundColor White
Write-Host "  5. Run full test suite" -ForegroundColor White
Write-Host "  6. Build Docker containers" -ForegroundColor White
Write-Host ""
