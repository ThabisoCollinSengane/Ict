# Register the ICT OPS bot to auto-start at logon (Windows Scheduled Task).
# Mirrors install_startup_task.ps1 (which does the live trading bot). Runs in the
# interactive session at logon so it survives disconnect; combined with Windows
# auto-logon it also recovers after a reboot.
#     powershell -ExecutionPolicy Bypass -File scripts\install_ops_task.ps1
$ErrorActionPreference = "Stop"

$repo = Split-Path $PSScriptRoot -Parent
$ps1  = Join-Path $repo "scripts\ops_bot.ps1"
$user = "$env:USERDOMAIN\$env:USERNAME"

$action  = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps1`"" `
    -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "ICTOpsBot" -Action $action -Trigger $trigger `
    -Settings $settings -RunLevel Highest -Force | Out-Null

Write-Host "Registered scheduled task 'ICTOpsBot' (runs at logon)." -ForegroundColor Green
Write-Host "Start it now:   Start-ScheduledTask -TaskName ICTOpsBot"
Write-Host "Stop it:        Stop-ScheduledTask  -TaskName ICTOpsBot"
Write-Host "Remove it:      Unregister-ScheduledTask -TaskName ICTOpsBot -Confirm:`$false"
Write-Host ""
Write-Host "IMPORTANT: run only ONE instance of each bot. Before Start-ScheduledTask,"
Write-Host "close any manual terminal still running ops_bot.ps1 (else Telegram 409)."
