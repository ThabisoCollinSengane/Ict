# Register the ICT live bot to auto-start at logon (Windows Scheduled Task).
# Runs in the INTERACTIVE session on purpose — MT5 is a GUI app and needs a real
# session, so this triggers at logon (not "session 0"). Combined with Windows
# auto-logon (see GCP_WINDOWS_SETUP.md) the bot recovers after a reboot too.
#     powershell -ExecutionPolicy Bypass -File scripts\install_startup_task.ps1
$ErrorActionPreference = "Stop"

$repo = Split-Path $PSScriptRoot -Parent
$ps1  = Join-Path $repo "scripts\run_live.ps1"
$user = "$env:USERDOMAIN\$env:USERNAME"

$action  = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps1`"" `
    -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
# Never time out; if the task process dies, Task Scheduler relaunches it too
# (belt-and-suspenders on top of run_live.ps1's own loop).
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "ICTLiveBot" -Action $action -Trigger $trigger `
    -Settings $settings -RunLevel Highest -Force | Out-Null

Write-Host "Registered scheduled task 'ICTLiveBot' (runs at logon)." -ForegroundColor Green
Write-Host "Start it now without waiting for a re-logon:"
Write-Host "    Start-ScheduledTask -TaskName ICTLiveBot"
Write-Host "Stop it:    Stop-ScheduledTask -TaskName ICTLiveBot"
Write-Host "Remove it:  Unregister-ScheduledTask -TaskName ICTLiveBot -Confirm:`$false"
Write-Host ""
Write-Host "IMPORTANT: enable Windows auto-logon so a reboot re-triggers this task —"
Write-Host "see the 'Survive reboots' section in GCP_WINDOWS_SETUP.md."
