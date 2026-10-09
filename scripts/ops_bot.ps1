# Ops bot - control the VM from Telegram via the SECOND bot. Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File scripts\ops_bot.ps1
# Needs OPS_BOT_TOKEN in live.env (chat id reused from TELEGRAM_CHAT_ID).
# Owner-only, whitelist-only. Leave it running (or wrap in a task) to keep control.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
.\.venv\Scripts\python.exe -m scripts.ops_bot
