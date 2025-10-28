@echo off
echo ========================================================
echo GIVC INTEGRATION AND GIT PUSH SCRIPT
echo ========================================================
echo.

REM Step 1: Run the integration script
echo [STEP 1] Running integration script...
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\rcmrejection3\nphies-rcm\integrate.ps1"
if %errorlevel% neq 0 (
    echo ERROR: Integration script failed!
    pause
    exit /b 1
)
echo Integration completed successfully!
echo.

REM Step 2: Change to GIVC directory
echo [STEP 2] Changing to GIVC directory...
cd /d "C:\Users\rcmrejection3\nphies-rcm\GIVC"
echo.

REM Step 3: Check git status
echo [STEP 3] Checking git status...
git status
echo.

REM Step 4: Check if remote exists and update it
echo [STEP 4] Configuring remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/fadil369/GIVC.git
git remote -v
echo.

REM Step 5: Stage all changes
echo [STEP 5] Staging all changes...
git add -A
echo.

REM Step 6: Show what will be committed
echo [STEP 6] Changes to be committed:
git status --short
echo.

REM Step 7: Commit changes
echo [STEP 7] Committing changes...
git commit -m "Integrated best features from nphies-rcm, brainsait-nphies-givc, and brainsait-rcm directories" -m "- Enhanced Python backend with NPHIES integration" -m "- Added AI features from brainsait-rcm" -m "- Integrated monorepo structure (apps/packages)" -m "- Added OASIS templates" -m "- Merged certificates and configuration" -m "- Consolidated infrastructure" -m "- Merged documentation and test suites"
if %errorlevel% neq 0 (
    echo No changes to commit or commit failed
    echo.
)
echo.

REM Step 8: Pull with rebase to sync with remote
echo [STEP 8] Syncing with remote (pull with rebase)...
git pull origin main --rebase
if %errorlevel% neq 0 (
    echo WARNING: Pull failed. Trying with master branch...
    git pull origin master --rebase
    if %errorlevel% neq 0 (
        echo WARNING: Pull with rebase failed. Will try force push.
    )
)
echo.

REM Step 9: Push to remote
echo [STEP 9] Pushing to remote repository...
git push -u origin main
if %errorlevel% neq 0 (
    echo WARNING: Push to main failed. Trying master branch...
    git push -u origin master
    if %errorlevel% neq 0 (
        echo WARNING: Push failed. You may need to force push or resolve conflicts.
        echo To force push, run: git push -u origin main --force
        pause
        exit /b 1
    )
)
echo.

echo ========================================================
echo SUCCESS! Integration completed and pushed to GitHub
echo Repository: https://github.com/fadil369/GIVC
echo ========================================================
echo.
pause
