# ICT live bot runner (Windows) — loads creds, ensures MT5 is up, runs the bot
# with restart-on-crash + logging. Launched by the ICTLiveBot scheduled task at
# logon (see scripts\install_startup_task.ps1), or manually:
#     powershell -ExecutionPolicy Bypass -File scripts\run_live.ps1
$ErrorActionPreference = "Stop"

# Repo root = parent of this script's folder.
Set-Location (Split-Path $PSScriptRoot -Parent)

# 1. Load live.env (KEY=VALUE, # comments) into this process's environment.
$envFile = "live.env"
if (-not (Test-Path $envFile)) {
    Write-Host "live.env not found. Copy live.env.example to live.env and fill it in." -ForegroundColor Red
    exit 1
}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=][^=]*?)\s*=\s*(.*?)\s*$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# 2. Ensure the MT5 terminal is running (needed for the Python API to attach).
$mt5 = [Environment]::GetEnvironmentVariable("MT5_TERMINAL_PATH", "Process")
if ($mt5 -and (Test-Path $mt5) -and -not (Get-Process terminal64 -ErrorAction SilentlyContinue)) {
    Write-Host "Launching MT5 terminal…"
    Start-Process $mt5
    Start-Sleep -Seconds 25   # give it time to log in before the bot connects
}

# 3. Run the bot in a restart loop. run_live's main() returns on a fatal error;
#    we log, back off, and relaunch so a transient failure self-heals.
New-Item -ItemType Directory -Force -Path "data" | Out-Null
$log  = "data\live.log"
$py   = ".\.venv\Scripts\python.exe"
$fails = 0
while ($true) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$ts] === starting live bot ===" | Tee-Object -FilePath $log -Append
    & $py -m live.run_live 2>&1 | Tee-Object -FilePath $log -Append
    $code = $LASTEXITCODE
    if ($code -eq 0) { $fails = 0 } else { $fails++ }
    # Back off on repeated fast crashes so we don't spin (e.g. bad creds / no net).
    $wait = if ($fails -ge 5) { 300 } else { 30 }
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$ts] bot exited (code $code, consecutive fails $fails) — restarting in ${wait}s" |
        Tee-Object -FilePath $log -Append
    Start-Sleep -Seconds $wait
}
