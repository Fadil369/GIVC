@echo off
echo ========================================
echo NPHIES Data Analyzer - Quick Launcher
echo ========================================
echo.

:menu
echo Please select an option:
echo.
echo 1. Run Basic Console Analysis
echo 2. Run Advanced Analysis with Visualizations
echo 3. Install Required Packages
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto basic
if "%choice%"=="2" goto advanced
if "%choice%"=="3" goto install
if "%choice%"=="4" goto exit

echo Invalid choice. Please try again.
echo.
goto menu

:basic
echo.
echo Running Basic Console Analysis...
echo.
python nphies_analyzer.py
echo.
echo Analysis complete! Check the analysis_output folder.
pause
goto menu

:advanced
echo.
echo Running Advanced Analysis with Visualizations...
echo.
python advanced_nphies_analyzer.py
echo.
echo Analysis complete! Check the analysis_output folder.
pause
goto menu

:install
echo.
echo Installing required packages...
echo.
pip install -r requirements.txt
echo.
echo Installation complete!
pause
goto menu

:exit
echo.
echo Thank you for using NPHIES Data Analyzer!
echo.
exit
