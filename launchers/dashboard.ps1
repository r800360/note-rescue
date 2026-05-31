# Visible dashboard window (backup launcher for Desktop shortcuts).
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot
$env:NOTE_RESCUE_LAUNCHER = "1"

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

& $Python main.py go
Write-Host ""
Read-Host "Press Enter to close"
