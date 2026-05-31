# One-time setup: venv, deps, scheduled task, smoke test.
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=== note-rescue setup ===" -ForegroundColor Cyan

# Python
$Py = $null
foreach ($Candidate in @("py -3.12", "py -3.11", "python")) {
    try {
        $Version = Invoke-Expression "$Candidate --version 2>&1"
        if ($LASTEXITCODE -eq 0) {
            $Py = $Candidate
            Write-Host "Using: $Version"
            break
        }
    } catch {}
}

if (-not $Py) {
    Write-Host "ERROR: Python not found. Install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Virtual environment
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    Invoke-Expression "$Py -m venv .venv"
}

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvPip = Join-Path $ProjectRoot ".venv\Scripts\pip.exe"

Write-Host "Installing dependencies..."
& $VenvPip install -r requirements.txt -q

# Vault folders
$Categories = @(
    "Inbox", "School", "Projects", "TESC", "AISC", "Research",
    "Personal", "Tech_Debugging", "ChatGPT", "TODO", "Archive"
)
foreach ($Cat in $Categories) {
    $Dir = Join-Path $ProjectRoot "vault\$Cat"
    if (!(Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir | Out-Null
    }
}

# Smoke test
Write-Host "Running smoke test..."
& $VenvPython main.py smoke-test

# Scheduled task
Write-Host ""
$Answer = Read-Host "Register daily 9 PM sync task? (Y/n)"
if ($Answer -ne "n" -and $Answer -ne "N") {
    & (Join-Path $ProjectRoot "schedule_task_daily.ps1")
}

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Daily use (double-click these - window stays open):"
Write-Host "  go.cmd              # dashboard"
Write-Host "  sync-now.cmd        # rescue notes now (don't wait for 9 PM)"
Write-Host "  find-notes.cmd      # search + pick a result"
Write-Host "  todos.cmd           # refresh + open TODO list"
Write-Host "  reset-npp.cmd       # sync + fresh Notepad++ session"
Write-Host "  doctor.cmd          # health check"
Write-Host "  inbox.cmd           # open Inbox folder"
Write-Host "  ask.cmd             # ask AI about your notes (needs config\secrets.local.json)"
Write-Host ""
if (!(Test-Path (Join-Path $ProjectRoot "config\secrets.local.json"))) {
    Write-Host "Optional: copy config\secrets.example.json to config\secrets.local.json"
    Write-Host "          and add your OpenAI API key for ask.cmd"
    Write-Host ""
}
Write-Host "Or: python main.py go"
Write-Host ""
Read-Host "Press Enter to close"
