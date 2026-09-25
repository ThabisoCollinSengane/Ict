# Opens port 8080 in Windows Firewall so the phone can reach the chart server.
# Run as Administrator in PowerShell.

New-NetFirewallRule `
    -DisplayName "ICT Chart Server 8080" `
    -Direction   Inbound `
    -Protocol    TCP `
    -LocalPort   8080 `
    -Action      Allow | Out-Null

Write-Host "Windows Firewall rule added for port 8080."
Write-Host "Now start the server:  python scripts/serve.py"
