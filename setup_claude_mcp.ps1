# Creates the Claude Desktop MCP config for filesystem access
$dir = "$env:APPDATA\Claude"
$file = "$dir\claude_desktop_config.json"

New-Item -ItemType Directory -Path $dir -Force | Out-Null

$config = @{
    mcpServers = @{
        filesystem = @{
            command = "npx"
            args    = @("-y", "@modelcontextprotocol/server-filesystem", "C:\Users\Administrator")
        }
    }
} | ConvertTo-Json -Depth 5

Set-Content -Path $file -Value $config -Encoding UTF8

Write-Host "Done. Config written to: $file"
Write-Host "Restart Claude Desktop now."
