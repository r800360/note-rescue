# Refresh and open global TODO list in Notepad++.
param(
    [switch]$Apply
)

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

if ($Apply) {
    & $Python main.py todos-apply
} else {
    & $Python main.py todos --open
    Write-Host ""
    Write-Host "To remove items: mark - [x], save, then run: todos.cmd apply" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to close"
