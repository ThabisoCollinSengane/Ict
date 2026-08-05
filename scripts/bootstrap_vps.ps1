# ICT live-trading — one-shot Windows VM bootstrap (Azure / any Windows Server 2022).
#
# Installs Chocolatey, Python, and Git; downloads the MetaTrader 5 installer;
# clones this repo; and builds the Python venv with the live dependencies — the
# whole environment in one run. Run ONCE, in an *Administrator* PowerShell:
#
#     Set-ExecutionPolicy Bypass -Scope Process -Force
#     .\bootstrap_vps.ps1
#
# Safe to re-run: every step is skipped/updated if it's already done.

$ErrorActionPreference = "Stop"
$RepoUrl    = "https://github.com/ThabisoCollinSengane/Ict.git"
$RepoBranch = "claude/algorithm-ict-2022-alignment-9kkLi"
$RepoDir    = "C:\ICT"
$Mt5Url     = "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"

function Info($m) { Write-Host "=== $m ===" -ForegroundColor Cyan }

# 0. Must be Administrator (Chocolatey + machine PATH need it).
$admin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) {
    Write-Host "Please run this in an ADMINISTRATOR PowerShell window." -ForegroundColor Red
    Write-Host "(Start menu -> right-click PowerShell -> Run as administrator)"
    exit 1
}

# TLS 1.2 for every download on a fresh Server image.
[Net.ServicePointManager]::SecurityProtocol = `
    [Net.ServicePointManager]::SecurityProtocol -bor 3072

# 1. Chocolatey package manager.
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Info "Installing Chocolatey"
    Invoke-Expression ((New-Object Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    $env:Path += ";$env:ProgramData\chocolatey\bin"
} else {
    Info "Chocolatey already installed"
}

# 2. Python + Git.
Info "Installing Python 3 + Git"
choco install -y python git | Out-Null

# Make python/git usable in THIS session without reopening PowerShell.
Import-Module "$env:ProgramData\chocolatey\helpers\chocolateyProfile.psm1" -ErrorAction SilentlyContinue
if (Get-Command Update-SessionEnvironment -ErrorAction SilentlyContinue) { Update-SessionEnvironment }
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + `
            [Environment]::GetEnvironmentVariable("Path", "User")

# 3. MetaTrader 5 installer -> Desktop (you run it + log into Exness yourself:
#    the login is interactive and broker-specific, so we don't silent-install).
$desktop = [Environment]::GetFolderPath("Desktop")
$mt5exe  = Join-Path $desktop "mt5setup.exe"
if (-not (Test-Path $mt5exe)) {
    Info "Downloading MetaTrader 5 installer to the Desktop"
    try {
        Invoke-WebRequest $Mt5Url -OutFile $mt5exe -UseBasicParsing
    } catch {
        Write-Host "  MT5 download failed — download it from your Exness dashboard instead." -ForegroundColor Yellow
    }
} else {
    Info "MT5 installer already on the Desktop"
}

# 4. Clone (or update) the repo on the live branch.
if (-not (Test-Path $RepoDir)) {
    Info "Cloning repo to $RepoDir"
    git clone $RepoUrl $RepoDir
} else {
    Info "Repo already at $RepoDir - fetching latest"
    git -C $RepoDir fetch origin
}
git -C $RepoDir checkout $RepoBranch
git -C $RepoDir pull --ff-only origin $RepoBranch

# 5. venv + live dependencies (reuses the existing setup script).
Set-Location $RepoDir
Info "Building Python venv + installing live dependencies"
powershell -ExecutionPolicy Bypass -File scripts\setup_vps.ps1

# 6. live.env from the template (git-ignored; you fill in DEMO creds).
if (-not (Test-Path (Join-Path $RepoDir "live.env"))) {
    Copy-Item live.env.example live.env
    Info "Created live.env from template"
}

Write-Host ""
Write-Host "=== BOOTSTRAP COMPLETE ===" -ForegroundColor Green
Write-Host "Repo:  $RepoDir   (branch $RepoBranch)"
Write-Host ""
Write-Host "Next steps (see AZURE_WINDOWS_SETUP.md for detail):"
Write-Host "  1. Run the MT5 installer on your Desktop (mt5setup.exe); log into your Exness DEMO account."
Write-Host "  2. notepad $RepoDir\live.env      # MT5_LOGIN / MT5_PASSWORD / MT5_SERVER / MT5_TERMINAL_PATH"
Write-Host "  3. Smoke test (places NO trades): .\.venv\Scripts\python.exe -m live.smoke_test"
Write-Host "  4. Run the bot:      powershell -ExecutionPolicy Bypass -File scripts\run_live.ps1"
Write-Host "  5. Auto-start:       powershell -ExecutionPolicy Bypass -File scripts\install_startup_task.ps1"
