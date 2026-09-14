# Add (or remove) a Telegram chat id to the bot's access list in live.env.
#
#   powershell -ExecutionPolicy Bypass -File scripts\add_access.ps1 -Id 6582495477 -Role admin
#   powershell -ExecutionPolicy Bypass -File scripts\add_access.ps1 -Id 6582495477 -Role viewer
#   powershell -ExecutionPolicy Bypass -File scripts\add_access.ps1 -Id 6582495477 -Remove
#
#   -Role admin  : full control (read AND trade) -> TELEGRAM_ADMIN_IDS
#   -Role viewer : read-only + alerts           -> TELEGRAM_VIEWER_IDS
#   -Remove      : take the id out of BOTH lists
#
# Idempotent (no duplicates). live.env is gitignored, so this only ever touches
# the copy on this machine. Restart the bot afterwards so it re-reads live.env
# (scripts\run_live.ps1, or scripts\sync_and_restart.ps1).
param(
    [Parameter(Mandatory = $true)][string]$Id,
    [ValidateSet("admin", "viewer")][string]$Role = "admin",
    [switch]$Remove
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$envFile = "live.env"
if (-not (Test-Path $envFile)) {
    Write-Host "live.env not found in $(Get-Location). Copy live.env.example first." -ForegroundColor Red
    exit 1
}

$targetKey = if ($Role -eq "viewer") { "TELEGRAM_VIEWER_IDS" } else { "TELEGRAM_ADMIN_IDS" }
$keys = @("TELEGRAM_ADMIN_IDS", "TELEGRAM_VIEWER_IDS")

$lines = @(Get-Content $envFile)
$seen = @{}
$out = foreach ($line in $lines) {
    $matched = $false
    foreach ($k in $keys) {
        if ($line -match ("^\s*" + $k + "\s*=\s*(.*)$")) {
            $matched = $true
            $seen[$k] = $true
            $list = @($matches[1] -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
            $list = @($list | Where-Object { $_ -ne $Id })          # drop any existing copy
            if (-not $Remove -and $k -eq $targetKey) { $list += $Id }  # add to the target list
            "$k=" + ($list -join ',')
            break
        }
    }
    if (-not $matched) { $line }
}
# If the target key wasn't present at all, append it (only when adding).
if (-not $Remove -and -not $seen[$targetKey]) { $out += "$targetKey=$Id" }

Set-Content -Path $envFile -Value $out -Encoding ascii

$action = if ($Remove) { "removed from all lists" } else { "added to $targetKey" }
Write-Host "OK - $Id $action." -ForegroundColor Green
Write-Host "Current access lines in live.env:" -ForegroundColor Cyan
Get-Content $envFile | Select-String "TELEGRAM_ADMIN_IDS|TELEGRAM_VIEWER_IDS|TELEGRAM_OPEN_VIEW"
Write-Host "`nRestart the bot so it re-reads live.env:" -ForegroundColor Yellow
Write-Host "    powershell -ExecutionPolicy Bypass -File scripts\run_live.ps1"
