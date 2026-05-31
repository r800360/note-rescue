# Lazy personal-site builder menu
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

Write-Host ""
Write-Host "  note-rescue — personal website (public, reviewed)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1  First-time setup (site init)"
Write-Host "  2  Draft from my notes (AI)"
Write-Host "  3  Publish draft + build site"
Write-Host "  4  Privacy review (before uploading)"
Write-Host "  5  Open site in browser"
Write-Host "  Enter  Quit"
Write-Host ""

$Choice = Read-Host "Choice"

switch ($Choice) {
    "1" { & $Python main.py site init }
    "2" {
        Write-Host "Focus: all | about | projects | values | reading | quotes | interests"
        $Focus = Read-Host "Focus (Enter=all)"
        if ([string]::IsNullOrWhiteSpace($Focus)) { $Focus = "all" }
        & $Python main.py site draft $Focus
    }
    "3" {
        & $Python main.py site publish
        & $Python main.py site build --open
    }
    "4" { & $Python main.py site review }
    "5" { & $Python main.py site open }
    default { break }
}

Write-Host ""
Read-Host "Press Enter to close"
