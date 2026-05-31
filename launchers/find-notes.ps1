# Visible search window (backup launcher for Desktop shortcuts).
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot
$env:NOTE_RESCUE_LAUNCHER = "1"

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

Write-Host ""
Write-Host "  note-rescue - search your rescued Notepad++ notes" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tips: use words from a meeting, project, or class name."
Write-Host "Example: student travel funds"
Write-Host ""

do {
    $Query = Read-Host "Search (Enter to quit)"
    if ([string]::IsNullOrWhiteSpace($Query)) { break }

    Write-Host ""
    & $Python main.py find $Query
    Write-Host ""
    $Again = Read-Host "Search again? (Y/n)"
} while ($Again -notin @("n", "N", "no", "No"))

Read-Host "Press Enter to close"
