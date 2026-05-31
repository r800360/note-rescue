# Reset Notepad++ to a fresh session after notes are safely in vault/.
param(
    [switch]$Preview,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Wait-ForUser {
    Write-Host ""
    Read-Host "Press Enter to close"
}

try {
    $ProjectRoot = $PSScriptRoot
    Set-Location $ProjectRoot

    $Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (!(Test-Path $Python)) {
        $Python = "python"
    }

    if ($Preview) {
        & $Python main.py reset
        if ($LASTEXITCODE -ne 0) { throw "Preview failed (exit $LASTEXITCODE)" }
        Wait-ForUser
        exit 0
    }

    Write-Host "This will sync first, then reset Notepad++ to a clean session." -ForegroundColor Yellow
    Write-Host "Your notes stay safe in vault/ - nothing is deleted." -ForegroundColor Yellow
    Write-Host ""

    Write-Host "Step 1/2: Syncing notes to vault..." -ForegroundColor Cyan
    & $Python main.py sync
    if ($LASTEXITCODE -ne 0) {
        throw "Sync failed (exit $LASTEXITCODE). Reset was NOT run. Notes in Notepad++ are unchanged."
    }

    Write-Host ""
    Write-Host "Step 2/2: Resetting Notepad++ session..." -ForegroundColor Cyan
    $ResetArgs = @("main.py", "reset", "--apply", "--kill-notepadpp")
    if ($Force) { $ResetArgs += "--force" }

    & $Python @ResetArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Reset failed (exit $LASTEXITCODE). Your notes are in vault/ but Notepad++ was not reset."
    }

    Write-Host ""
    Write-Host "Done. Notepad++ should open clean. Search still works via Find Notes." -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ScriptStackTrace) {
        Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
    }
    Wait-ForUser
    exit 1
}

Wait-ForUser
exit 0
