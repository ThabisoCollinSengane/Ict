# ICT bot - pull the latest code from GitHub and restart the live bot.
#
# Run this on the VM whenever you've pushed new bot changes:
#     powershell -ExecutionPolicy Bypass -File scripts\sync_and_restart.ps1
#
# Options:
#     -Branch <name>   which branch to deploy (default: the algorithm branch)
#     -NoRestart       sync only; don't relaunch (you start run_live.ps1 yourself)
#
# What it does, in order:
#   1. stops the running bot (python + its run_live.ps1 restart-loop windows)
#   2. hard-resets the working tree to origin/<branch> - an EXACT match, no merge
#      conflicts. Your live.env and data\ are gitignored, so they are NOT touched.
#   3. refreshes the venv deps from requirements_live.txt
#   4. runs the offline self-test - a bad pull is caught BEFORE the bot relaunches
#   5. relaunches the bot in a fresh window (unless -NoRestart)
param(
    [string]$Branch = "claude/algorithm-ict-2022-alignment-9kkLi",
    [switch]$NoRestart
)
$ErrorActionPreference = "Stop"

# Repo root = parent of this script's folder.
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "== ICT bot sync ==" -ForegroundColor Cyan
Write-Host ("repo   : {0}" -f (Get-Location))
Write-Host ("branch : {0}" -f $Branch)

# 1. Stop the running bot so files aren't locked and the new code is picked up.
Write-Host "`n[1/5] stopping the running bot..." -ForegroundColor Yellow
# 1a. the launcher loop(s) first, so they don't relaunch stale code mid-sync.
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "run_live\.ps1" -and $_.ProcessId -ne $PID } |
    ForEach-Object {
        Write-Host ("  stopping launcher pid {0}" -f $_.ProcessId)
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
# 1b. the python bot process itself (leave MT5 terminal64 running).
Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "live\.run_live" } |
    ForEach-Object {
        Write-Host ("  stopping bot pid {0}" -f $_.ProcessId)
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 2

# 2. Fetch + hard-reset to the remote branch (exact match; no conflicts).
Write-Host "`n[2/5] syncing to origin/$Branch ..." -ForegroundColor Yellow
git fetch origin $Branch
git checkout -B $Branch "origin/$Branch"
git reset --hard "origin/$Branch"
Write-Host ("  now at: {0}" -f (git log --oneline -1))

# 3. Refresh Python deps (safe no-op when already installed).
Write-Host "`n[3/5] updating venv deps ..." -ForegroundColor Yellow
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "  .venv not found at $py - create it first (see requirements_live.txt)." -ForegroundColor Red
    exit 1
}
& $py -m pip install -q -r requirements_live.txt

# 4. Offline self-test (no MT5, no network) - catch a bad pull before relaunch.
Write-Host "`n[4/5] offline self-test ..." -ForegroundColor Yellow
& $py -m live.test_semi_auto
if ($LASTEXITCODE -ne 0) {
    Write-Host "SELF-TEST FAILED - NOT restarting. Fix the pull before relaunching." -ForegroundColor Red
    exit 1
}

# 5. Relaunch.
if ($NoRestart) {
    Write-Host "`nSync done (-NoRestart). Start it with: scripts\run_live.ps1" -ForegroundColor Green
    exit 0
}
Write-Host "`n[5/5] relaunching the bot in a new window ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-ExecutionPolicy","Bypass","-NoExit","-File","scripts\run_live.ps1"
Write-Host "Bot relaunched. Watch data\runner.log (or the new window)." -ForegroundColor Green
Write-Host "In Telegram, send /brief then /mm EURUSD buy to see the new IFVG beat tags." -ForegroundColor Green
