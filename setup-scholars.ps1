# One-time: create private scholar config from the public template.
$ProjectRoot = $PSScriptRoot
$Example = Join-Path $ProjectRoot "config\scholars.example.json"
$Local = Join-Path $ProjectRoot "config\scholars.local.json"
$ScholarData = Join-Path $ProjectRoot "data\scholars"

if (Test-Path $Local) {
    Write-Host "Already exists: config\scholars.local.json" -ForegroundColor Yellow
    exit 0
}

Copy-Item $Example $Local
New-Item -ItemType Directory -Path $ScholarData -Force | Out-Null

Write-Host "Created config\scholars.local.json (private, gitignored)" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit config\scholars.local.json with your scholar names and CSV paths"
Write-Host "  2. Optionally copy benchmark CSVs to data\scholars\ (also gitignored)"
Write-Host "  3. Run: python main.py privacy-check before pushing to GitHub"
