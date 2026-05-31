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
$Answer = Read-Host "Register daily sync task? (Y/n)"
if ($Answer -ne "n" -and $Answer -ne "N") {
    & (Join-Path $ProjectRoot "schedule_task_daily.ps1")
}

# Optional AI ask setup
Write-Host ""
$SecretsPath = Join-Path $ProjectRoot "config\secrets.local.json"
if (!(Test-Path $SecretsPath) -and -not $env:OPENAI_API_KEY) {
    $AskSetup = Read-Host "Set up ask.cmd (OpenAI API key) now? (y/N)"
    if ($AskSetup -eq "y" -or $AskSetup -eq "Y") {
        $Example = Join-Path $ProjectRoot "config\secrets.example.json"
        Copy-Item $Example $SecretsPath
        Write-Host "Created config\secrets.local.json — paste your OpenAI API key, then run ask.cmd"
        Start-Process notepad.exe $SecretsPath
    }
}

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "What's next (recommended order):"
Write-Host "  1. Double-click go.cmd          — your home base (status + next steps)"
Write-Host "  2. Pin launchers you use daily  — run pin-shortcuts.ps1 for Start menu + taskbar"
Write-Host "  3. Read WORKFLOWS.md            — one-page 'I want X -> run Y' guide"
Write-Host ""
Write-Host "Daily launchers (double-click):"
Write-Host "  go.cmd              dashboard + next steps"
Write-Host "  sync-now.cmd        rescue notes now"
Write-Host "  find-notes.cmd      search + open a note"
Write-Host "  ask.cmd             ask AI about your notes (needs secrets.local.json)"
Write-Host "  todos.cmd           refresh + open TODO list (todos.cmd apply after checkoffs)"
Write-Host "  reset-npp.cmd       sync + fresh Notepad++ session"
Write-Host "  workflows.cmd       open the quick-reference guide"
Write-Host ""
Write-Host "Or: python main.py go"
Write-Host ""
Read-Host "Press Enter to close"
