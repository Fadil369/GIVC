# Run integration with better error handling
$ErrorActionPreference = "Continue"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "GIVC INTEGRATION AND GIT PUSH SCRIPT" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run the integration script
Write-Host "[STEP 1] Running integration script..." -ForegroundColor Yellow
try {
    & "C:\Users\rcmrejection3\nphies-rcm\integrate.ps1"
    Write-Host "Integration completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Integration script failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Change to GIVC directory
Write-Host "[STEP 2] Changing to GIVC directory..." -ForegroundColor Yellow
Set-Location "C:\Users\rcmrejection3\nphies-rcm\GIVC"
Write-Host ""

# Step 3: Check git status
Write-Host "[STEP 3] Checking git status..." -ForegroundColor Yellow
git status
Write-Host ""

# Step 4: Configure remote repository
Write-Host "[STEP 4] Configuring remote repository..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/fadil369/GIVC.git
git remote -v
Write-Host ""

# Step 5: Stage all changes
Write-Host "[STEP 5] Staging all changes..." -ForegroundColor Yellow
git add -A
Write-Host ""

# Step 6: Show what will be committed
Write-Host "[STEP 6] Changes to be committed:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Step 7: Commit changes
Write-Host "[STEP 7] Committing changes..." -ForegroundColor Yellow
$commitMessage = @"
Integrated best features from nphies-rcm, brainsait-nphies-givc, and brainsait-rcm directories

- Enhanced Python backend with NPHIES integration
- Added AI features from brainsait-rcm
- Integrated monorepo structure (apps/packages)
- Added OASIS templates
- Merged certificates and configuration
- Consolidated infrastructure
- Merged documentation and test suites
"@

git commit -m $commitMessage
Write-Host ""

# Step 8: Pull with rebase to sync with remote
Write-Host "[STEP 8] Syncing with remote (pull with rebase)..." -ForegroundColor Yellow
$pullSuccess = $false
try {
    git pull origin main --rebase 2>&1 | Out-Null
    $pullSuccess = $LASTEXITCODE -eq 0
} catch {
    Write-Host "WARNING: Pull from main failed, trying master..." -ForegroundColor Yellow
}

if (-not $pullSuccess) {
    try {
        git pull origin master --rebase 2>&1 | Out-Null
        $pullSuccess = $LASTEXITCODE -eq 0
    } catch {
        Write-Host "WARNING: Pull with rebase failed. Will try push anyway." -ForegroundColor Yellow
    }
}
Write-Host ""

# Step 9: Push to remote
Write-Host "[STEP 9] Pushing to remote repository..." -ForegroundColor Yellow
$pushSuccess = $false
try {
    git push -u origin main 2>&1
    $pushSuccess = $LASTEXITCODE -eq 0
} catch {
    Write-Host "WARNING: Push to main failed, trying master..." -ForegroundColor Yellow
}

if (-not $pushSuccess) {
    try {
        git push -u origin master 2>&1
        $pushSuccess = $LASTEXITCODE -eq 0
    } catch {
        Write-Host "WARNING: Push failed. You may need to force push." -ForegroundColor Red
        Write-Host "To force push, run: git push -u origin main --force" -ForegroundColor Yellow
        exit 1
    }
}

if ($pushSuccess) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host "SUCCESS! Integration completed and pushed to GitHub" -ForegroundColor Green
    Write-Host "Repository: https://github.com/fadil369/GIVC" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Integration completed but push may have issues." -ForegroundColor Yellow
    Write-Host "Check git status and resolve any conflicts manually." -ForegroundColor Yellow
}
