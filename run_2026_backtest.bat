@echo off
REM ============================================================================
REM  ICT 2026 Backtest — one-click runner for Windows
REM
REM  Double-click this file (from the repo root), or run it from PowerShell:
REM      .\run_2026_backtest.bat
REM
REM  What it does:
REM    1. Prepares your HistData 2026 downloads (unzip + convert + rename)
REM    2. Runs the backtest on 2026
REM
REM  One-time setup first (see the chat walkthrough):
REM    - Install Python 3.12 with "Add python.exe to PATH" ticked
REM    - python -m pip install -r requirements.txt
REM    - Download + extract your Drive "2026" folder of HistData .zip files
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM --- pick the python launcher that exists on this machine -------------------
set "PY=python"
where python >nul 2>nul || set "PY=py"

echo.
echo ============================================================
echo  ICT 2026 Backtest
echo ============================================================
echo.

REM --- 1. locate the folder of HistData zips ---------------------------------
REM  Pass it as an argument (drag a folder onto this .bat), else you'll be asked.
set "DATA_DIR=%~1"
if "%DATA_DIR%"=="" (
    set /p "DATA_DIR=Path to your extracted 2026 HistData folder (e.g. C:\ict-data\2026): "
)

REM strip surrounding quotes if the user pasted a quoted path
set "DATA_DIR=%DATA_DIR:"=%"

if not exist "%DATA_DIR%" (
    echo.
    echo  ERROR: folder not found: "%DATA_DIR%"
    echo  Extract your Drive "2026" download first, then re-run.
    echo.
    pause
    exit /b 1
)

REM --- 2. prepare the data ----------------------------------------------------
echo.
echo [1/2] Preparing HistData files from "%DATA_DIR%" ...
echo.
%PY% scripts\prepare_histdata.py "%DATA_DIR%"
if errorlevel 1 (
    echo.
    echo  Data preparation failed - see the messages above.
    pause
    exit /b 1
)

REM --- 3. run the backtest ----------------------------------------------------
echo.
echo [2/2] Running the 2026 backtest ...
echo.
%PY% run_backtest_histdata.py --years 2026
if errorlevel 1 (
    echo.
    echo  Backtest failed - see the messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done. Scroll up for the full report, then copy it into
echo  the chat and I'll interpret the results.
echo.
echo  Tip: for the meaningful continuous path, add your
echo  2022-2025 CSVs to data\histdata\ and run:
echo    %PY% run_backtest_histdata.py --years 2022 2023 2024 2025 2026
echo ============================================================
echo.
pause
