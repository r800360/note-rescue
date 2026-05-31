# Prompts for a search query, then opens the best match in Notepad++.
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$Query = Read-Host "Search your rescued notes"
if (-not $Query.Trim()) {
    Write-Host "No query entered." -ForegroundColor Yellow
    Read-Host "Press Enter to close"
    exit 0
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

& $Python main.py find $Query

Write-Host ""
Read-Host "Press Enter to close"
