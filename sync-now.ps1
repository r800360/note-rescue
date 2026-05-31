# Run sync immediately (backup + import + todos)  -  don't wait for 9 PM.
$ErrorActionPreference = "Continue"

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

try {
    & $Python main.py sync @args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Sync failed (exit $LASTEXITCODE)" -ForegroundColor Red
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to close"
