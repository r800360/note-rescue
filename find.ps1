# Search your rescued notes and open the top result in Notepad++.
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$Query
)

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

if (-not $Query) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ProjectRoot "launchers\find-notes.ps1")
    exit $LASTEXITCODE
}

try {
    & $Python main.py find $Query
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Search failed (exit $LASTEXITCODE)" -ForegroundColor Red
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to close"
