@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM =====================================================================
REM  BrainSAIT-NPHIES-GIVC :: Push to Remote Automation Script
REM  Usage: push-to-remote.bat [optional custom commit message]
REM =====================================================================

set "REPO_DIR=C:\Users\rcmrejection3\nphies-rcm\GIVC"
set "COMMIT_MSG_FILE=%TEMP%\givc_commit_message.txt"
set "DEFAULT_VERSION=3.0.0"
set "CUSTOM_MESSAGE=%*"

echo.
echo ==================================================
echo   BrainSAIT-NPHIES-GIVC Remote Update Assistant
echo ==================================================
echo Repository : %REPO_DIR%
echo Timestamp  : %DATE% %TIME%
echo Version    : %DEFAULT_VERSION%
echo.

if not exist "%REPO_DIR%\.git" (
    echo [ERROR] Git repository not found at %REPO_DIR%
    echo         Please verify the path and try again.
    goto :cleanup
)

where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git CLI is not available in PATH.
    echo         Install Git for Windows and retry.
    goto :cleanup
)

cd /d "%REPO_DIR%"

echo [STEP 1] Repository status overview
git status --short
echo.

set "HAS_CHANGES="
for /f "usebackq delims=" %%I in (`git status --porcelain`) do (
    set HAS_CHANGES=1
    goto :afterStatus
)
:afterStatus

if defined HAS_CHANGES (
    echo [STEP 2] Staging new and modified files...
    git add -A
    if errorlevel 1 (
        echo [ERROR] Failed to stage files. Please review the output above.
        goto :cleanup
    )
    echo   [OK] Files staged successfully.
    echo.

    echo [STEP 3] Preparing commit message...
    if not "%CUSTOM_MESSAGE%"=="" (
        echo %CUSTOM_MESSAGE%>"%COMMIT_MSG_FILE%"
    ) else (
        call :CreateDefaultCommitMessage "%COMMIT_MSG_FILE%"
    )

    echo [STEP 4] Creating commit...
    git commit -F "%COMMIT_MSG_FILE%"
    set "COMMIT_EXIT=%ERRORLEVEL%"
    del "%COMMIT_MSG_FILE%" >nul 2>&1
    if not "%COMMIT_EXIT%"=="0" (
        echo [WARNING] Commit was not created. Continuing with pull/push.
    ) else (
        echo   [OK] Commit created successfully.
    )
    echo.
) else (
    echo [INFO] Working tree clean. Skipping commit step.
    echo.
)

echo [STEP 5] Reviewing remotes...
git remote -v
echo.

echo [STEP 6] Pulling latest changes from origin/main (rebase)...
git pull origin main --rebase
if errorlevel 1 (
    echo [WARNING] Pull encountered issues. Resolve conflicts before pushing.
    goto :cleanup
)
echo   [OK] Local branch synchronized with origin/main.
echo.

echo [STEP 7] Pushing updates to origin/main...
git push origin main
if errorlevel 1 (
    echo [ERROR] Push failed. Please resolve the issues above and retry.
    goto :cleanup
)

echo.
echo ==================================================
echo   SUCCESS! Remote repository updated.
echo ==================================================
echo Highlights:
echo   - Monorepo assets synchronized (apps, packages, services, infra)
echo   - NPHIES + GIVC AI integration artifacts included
echo   - Documentation set refreshed (Ultimate Guide, Quick Start, etc.)
echo   - Security assets protected via enhanced .gitignore
echo.
echo Reminder: Review PRE_PUSH_CHECKLIST.md after each deployment.
echo.

:cleanup
if exist "%COMMIT_MSG_FILE%" del "%COMMIT_MSG_FILE%" >nul 2>&1
echo Operation finished. Press any key to exit.
pause >nul
endlocal
exit /b 0

:CreateDefaultCommitMessage
setlocal EnableDelayedExpansion
set "MSG_FILE=%~1"
(
    echo Ultimate Integration v%DEFAULT_VERSION% - Unified Platform Update
    echo Date: %DATE% %TIME%
    echo.
    echo Key Highlights:
    echo - Synchronized NPHIES production backend with AI-driven services
    echo - Consolidated documentation ^(README, Ultimate Guide, Quick Start^)
    echo - Integrated monorepo assets from brainsait-rcm and new build
    echo - Updated security posture ^(.gitignore, certificates, env templates^)
    echo - Added deployment and infrastructure automation assets
    echo.
    echo Additional Notes:
    echo - Verify credential placeholders in .env.example before production push
    echo - See IMPLEMENTATION_SUMMARY.md for detailed change log
    echo - Run PRE_PUSH_CHECKLIST.md items prior to release
) >"!MSG_FILE!"
endlocal
exit /b 0
