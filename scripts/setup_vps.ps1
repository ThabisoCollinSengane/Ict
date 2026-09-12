# ICT live-trading VPS setup (Windows / PowerShell)
# Run from the repo root in PowerShell:
#     powershell -ExecutionPolicy Bypass -File scripts\setup_vps.ps1
#
# It creates a virtual environment and installs the live dependencies. It does NOT
# install Python or MT5 - see LIVE_SETUP.md for those (one-time manual downloads).

$ErrorActionPreference = "Stop"
Write-Host "=== ICT VPS setup ===" -ForegroundColor Cyan

# 1. Python present?
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python not found on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.11+ from https://www.python.org/downloads/windows/"
    Write-Host "Tick 'Add python.exe to PATH' during install, then re-run this script."
    exit 1
}
$ver = (python --version) 2>&1
Write-Host "Found $ver"

# 2. Virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
} else {
    Write-Host ".venv already exists - reusing."
}

# 3. Install deps
Write-Host "Installing live dependencies..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements_live.txt

# 4. Done
Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  1. Install + launch the MetaTrader 5 terminal, log into your Exness DEMO account."
Write-Host "  2. Set credentials (this PowerShell session):"
Write-Host '       $env:MT5_LOGIN="12345678"; $env:MT5_PASSWORD="pwd"; $env:MT5_SERVER="Exness-MT5Trial14"'
Write-Host "  3. Run the connectivity smoke test (places NO trades):"
Write-Host "       .\.venv\Scripts\python.exe -m live.smoke_test"
Write-Host ""
Write-Host "See LIVE_SETUP.md for the full walkthrough and the go-live checklist."
