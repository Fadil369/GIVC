$host.UI.RawUI.WindowTitle = "GIVC Integration"
$ErrorActionPreference = "Continue"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "GIVC INTEGRATION AND GIT PUSH" -ForegroundColor Cyan  
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Execute integration
Write-Host "[RUNNING] Integration script..." -ForegroundColor Yellow
& "$PSScriptRoot\integrate.ps1"

Write-Host ""
Write-Host "[COMPLETE] Integration finished. Now processing git operations..." -ForegroundColor Green
Write-Host ""

# Change to GIVC
Set-Location "$PSScriptRoot\GIVC"

# Configure git
Write-Host "[GIT] Configuring remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/fadil369/GIVC.git
git remote -v

# Stage changes
Write-Host ""
Write-Host "[GIT] Staging changes..." -ForegroundColor Yellow
git add -A

# Show status
Write-Host ""
Write-Host "[GIT] Status:" -ForegroundColor Yellow
git status --short | Select-Object -First 20
Write-Host "... (showing first 20 files)" -ForegroundColor Gray

# Commit
Write-Host ""
Write-Host "[GIT] Committing..." -ForegroundColor Yellow
git commit -m "Unified GIVC platform with integrated features" -m "Merged nphies-rcm, brainsait-nphies-givc, and brainsait-rcm" -m "- Python backend with NPHIES integration" -m "- AI fraud detection features" -m "- Monorepo structure" -m "- OASIS templates" -m "- Certificates and configs" -m "- Infrastructure and docs"

# Sync and push
Write-Host ""
Write-Host "[GIT] Syncing with remote..." -ForegroundColor Yellow
git pull origin main --rebase --quiet 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    git pull origin master --rebase --quiet 2>&1 | Out-Null
}

Write-Host ""
Write-Host "[GIT] Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Trying master branch..." -ForegroundColor Yellow
    git push -u origin master 2>&1
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "COMPLETE!" -ForegroundColor Green
Write-Host "Repository: https://github.com/fadil369/GIVC" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green
