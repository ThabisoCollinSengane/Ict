@echo off
REM ============================================================================
REM  P39 — Volume-as-confidence analysis — one-click runner for Windows
REM
REM  Runs the full handover pipeline end-to-end:
REM    1. backtest 2022 (IS) + 2024 (OOS)  -> produces the trade dump
REM    2. aggregate the HistData TICK zips  -> per-month M5 tick/delta counts
REM    3. analyse                            -> data\p39_volume_report.md
REM
REM  Prerequisites (one-time):
REM    - Python 3.12 on PATH  +  python -m pip install -r requirements.txt
REM    - 2022 and 2024 M1 data already in data\histdata\ (the same files that
REM      produce your normal backtest). If missing, run prepare_histdata.py first.
REM    - Your extracted TICK folder ("Tick data, fx eurusd and gbpusd 2022 and
REM      2024") of HISTDATA_COM_ASCII_<PAIR>_T<YYYYMM>.zip files.
REM
REM  Usage: double-click, or drag the tick folder onto this .bat, or:
REM    .\run_p39_analysis.bat "C:\path\to\tick folder"
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PY=python"
where python >nul 2>nul || set "PY=py"

echo.
echo ============================================================
echo  P39 - Volume-as-confidence analysis
echo ============================================================
echo.

REM --- locate the tick zip folder --------------------------------------------
set "TICK_DIR=%~1"
if "%TICK_DIR%"=="" (
    set /p "TICK_DIR=Path to your extracted TICK folder (HistData T-zips): "
)
set "TICK_DIR=%TICK_DIR:"=%"
if not exist "%TICK_DIR%" (
    echo.
    echo  ERROR: folder not found: "%TICK_DIR%"
    echo  Extract your "Tick data ... 2022 and 2024" Drive download first.
    echo.
    pause
    exit /b 1
)

REM Years to backtest for the trade dump. Match the tick coverage (2022 IS,
REM 2024 OOS). Override by passing a 2nd argument, e.g. "2022 2023 2024 2025".
set "YEARS=%~2"
if "%YEARS%"=="" set "YEARS=2022 2024"

REM --- 1. backtest -> trade dump ---------------------------------------------
echo [1/3] Backtesting %YEARS% to produce the trade dump ...
echo.
%PY% run_backtest_histdata.py --years %YEARS%
if errorlevel 1 (
    echo.
    echo  Backtest failed - is the 2022/2024 M1 data in data\histdata\ ?
    echo  If not, run: %PY% scripts\prepare_histdata.py ^<your M1 zip folder^>
    pause
    exit /b 1
)

REM --- 2. aggregate ticks -----------------------------------------------------
echo.
echo [2/3] Aggregating tick data from "%TICK_DIR%" (this is the slow step) ...
echo.
%PY% scripts\p39_volume_analysis.py aggregate "%TICK_DIR%"
if errorlevel 1 (
    echo.
    echo  Tick aggregation failed - see the messages above.
    pause
    exit /b 1
)

REM --- 3. analyse -------------------------------------------------------------
echo.
echo [3/3] Joining ticks to trades and writing the report ...
echo.
%PY% scripts\p39_volume_analysis.py analyse
if errorlevel 1 (
    echo.
    echo  Analysis failed - see the messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done. The report is at:
echo    data\p39_volume_report.md
echo.
echo  Open it, or copy its contents into the chat and I'll read
echo  the verdict (GREEN/YELLOW/RED) with you.
echo ============================================================
echo.
pause
