# Quick Notepad++ health check  -  are you accumulating too many tabs?
$ErrorActionPreference = "Continue"

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

try {
    & $Python main.py doctor @args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Doctor failed (exit $LASTEXITCODE)" -ForegroundColor Red
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to close"
