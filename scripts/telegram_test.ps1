# Two-way Telegram test (no MT5 needed). Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File scripts\telegram_test.ps1
# Loads live.env, sends a welcome message to your phone, then listens for your
# commands (/status, /lot, /bias, /levels, /help) and acks each one. Ctrl-C to stop.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
.\.venv\Scripts\python.exe -m live.telegram_test
