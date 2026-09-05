# One-shot pipeline: fetch HistData (if missing) -> prepare -> backtest -> pair/bias/
# entry/session analysis. Run from the repo root (C:\ICT):
#     powershell -ExecutionPolicy Bypass -File scripts\run_full_pipeline.ps1
#
# Stops immediately on the first real failure (does not cascade silently like running
# each step by hand in the wrong directory did).

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
Write-Host "=== repo root: $root ===" -ForegroundColor Cyan

$raw  = "data\histdata_raw"
$dest = "data\histdata"

# Only fetch if data\histdata has no CSVs yet (idempotent — safe to re-run).
$haveData = (Test-Path $dest) -and ((Get-ChildItem $dest -Filter "*.csv" -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0)

if (-not $haveData) {
    Write-Host "`n=== no data\histdata CSVs found - fetching HistData (2022-2025) ===" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $raw | Out-Null
    python scripts\fetch_histdata.py --years 2022 2023 2024 2025 --dest $raw
    if ($LASTEXITCODE -ne 0) { Write-Host "FETCH FAILED (exit $LASTEXITCODE) - stopping." -ForegroundColor Red; exit 1 }

    Write-Host "`n=== normalising into $dest ===" -ForegroundColor Yellow
    python scripts\prepare_histdata.py $raw --dest $dest
    if ($LASTEXITCODE -ne 0) { Write-Host "PREPARE FAILED (exit $LASTEXITCODE) - stopping." -ForegroundColor Red; exit 1 }
} else {
    Write-Host "`n=== data\histdata already has CSVs - skipping fetch/prepare ===" -ForegroundColor Green
}

Write-Host "`n=== running backtest 2022-2025 ===" -ForegroundColor Yellow
python run_backtest_histdata.py --years 2022 2023 2024 2025
if ($LASTEXITCODE -ne 0) { Write-Host "BACKTEST FAILED (exit $LASTEXITCODE) - stopping." -ForegroundColor Red; exit 1 }

Write-Host "`n=== running pair x bias x entry x session analysis ===" -ForegroundColor Yellow
python scripts\pair_bias_analysis.py
if ($LASTEXITCODE -ne 0) { Write-Host "ANALYSIS FAILED (exit $LASTEXITCODE) - stopping." -ForegroundColor Red; exit 1 }

Write-Host "`n=== running AMD range & sweep analysis ===" -ForegroundColor Yellow
python scripts\amd_range_analysis.py
if ($LASTEXITCODE -ne 0) { Write-Host "AMD ANALYSIS FAILED (exit $LASTEXITCODE) - stopping." -ForegroundColor Red; exit 1 }

Write-Host "`n=== DONE - check the RESULTS PUSHED lines above for all reports ===" -ForegroundColor Cyan
