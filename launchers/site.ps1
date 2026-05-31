# Personal-site builder menu.
$ErrorActionPreference = "Continue"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

function Wait-ForUser {
    Write-Host ""
    Read-Host "Press Enter to close"
}

try {
    Write-Host ""
    Write-Host "  note-rescue - personal website (public, reviewed)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Follow the steps in order. Only upload site/dist/ after step 5 passes."
    Write-Host ""
    Write-Host "  1  First-time setup (site init)"
    Write-Host "  2  Draft from my notes (AI)"
    Write-Host "  3  Review latest draft (open JSON - delete anything too personal)"
    Write-Host "  4  Publish draft + build site"
    Write-Host "  5  Privacy review (before uploading)"
    Write-Host "  6  Open site in browser"
    Write-Host "  Enter  Quit"
    Write-Host ""

    $Choice = Read-Host "Choice"

    switch ($Choice) {
        "1" {
            & $Python main.py site init
        }
        "2" {
            Write-Host "Focus: all | about | projects | values | reading | quotes | interests"
            $Focus = Read-Host "Focus (Enter=all)"
            if ([string]::IsNullOrWhiteSpace($Focus)) { $Focus = "all" }
            & $Python main.py site draft $Focus
            Write-Host ""
            Write-Host "Next: choose option 3 to review the draft before publishing." -ForegroundColor Yellow
        }
        "3" {
            $DraftsDir = Join-Path $ProjectRoot "site\drafts"
            if (!(Test-Path $DraftsDir)) {
                Write-Host "No drafts yet. Run option 2 first." -ForegroundColor Yellow
                break
            }
            $Latest = Get-ChildItem $DraftsDir -Filter "draft-*.json" | Sort-Object Name -Descending | Select-Object -First 1
            if (-not $Latest) {
                Write-Host "No draft-*.json files found. Run option 2 first." -ForegroundColor Yellow
                break
            }
            Write-Host "Opening: $($Latest.Name)" -ForegroundColor Green
            Write-Host "Delete anything too personal, then choose option 4 to publish."
            Start-Process $Latest.FullName
        }
        "4" {
            & $Python main.py site publish
            if ($LASTEXITCODE -ne 0) { throw "site publish failed (exit $LASTEXITCODE)" }
            & $Python main.py site build --open
            if ($LASTEXITCODE -ne 0) { throw "site build failed (exit $LASTEXITCODE)" }
            Write-Host ""
            Write-Host "Next: choose option 5 (privacy review) before uploading site/dist/." -ForegroundColor Yellow
        }
        "5" {
            & $Python main.py site review
        }
        "6" {
            & $Python main.py site open
        }
        default { break }
    }

    if ($Choice -match '^[1-6]$' -and $LASTEXITCODE -ne 0) {
        Write-Host "Command failed (exit $LASTEXITCODE)" -ForegroundColor Red
    }
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Wait-ForUser
    exit 1
}

Wait-ForUser
exit 0
