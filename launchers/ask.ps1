# Interactive ask loop for vault search.
$ErrorActionPreference = "Continue"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot
$env:NOTE_RESCUE_LAUNCHER = "1"

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $Python)) { $Python = "python" }

function Wait-ForUser {
    Write-Host ""
    Read-Host "Press Enter to close"
}

try {
    $Secrets = Join-Path $ProjectRoot "config\secrets.local.json"
    if (!(Test-Path $Secrets) -and -not $env:OPENAI_API_KEY) {
        Write-Host ""
        Write-Host "  OpenAI key not set up yet." -ForegroundColor Yellow
        Write-Host "  Copy config\secrets.example.json to config\secrets.local.json"
        Write-Host "  and paste your API key, then run ask.cmd again."
        Write-Host ""
        Wait-ForUser
        exit 1
    }

    Write-Host ""
    Write-Host "  note-rescue - ask your notes (AI vault search)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Type a question in plain English. Examples:"
    Write-Host "  What was I working on for student travel?"
    Write-Host "  What did I write about the AISC meeting last week?"
    Write-Host ""
    Write-Host "Special commands:"
    Write-Host "  correct: I meant ...     (fix shorthand the AI misread)"
    Write-Host "  corrections              (list saved clarifications)"
    Write-Host "  open                     (open top source note after last answer)"
    Write-Host "  Enter alone              (quit)"
    Write-Host ""

    $LastHadSources = $false

    do {
        $Line = Read-Host "Ask"
        if ([string]::IsNullOrWhiteSpace($Line)) { break }

        if ($Line -match '^(?i)corrections?\s*$') {
            & $Python main.py ask corrections
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Command failed (exit $LASTEXITCODE)" -ForegroundColor Red
            }
            Write-Host ""
            continue
        }

        if ($Line -match '^(?i)correct:\s*(.+)$') {
            $Text = $Matches[1].Trim()
            & $Python main.py ask correct "$Text"
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Command failed (exit $LASTEXITCODE)" -ForegroundColor Red
            }
            Write-Host ""
            continue
        }

        if ($Line -match '^(?i)open\s*$') {
            if (-not $LastHadSources) {
                Write-Host "Ask a question first, then type open." -ForegroundColor Yellow
                Write-Host ""
                continue
            }
            & $Python main.py ask "$script:LastQuestion" --open
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Command failed (exit $LASTEXITCODE)" -ForegroundColor Red
            }
            Write-Host ""
            continue
        }

        $script:LastQuestion = $Line
        & $Python main.py ask "$Line"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Ask failed (exit $LASTEXITCODE). Check your API key and internet connection." -ForegroundColor Red
        } else {
            $LastHadSources = $true
        }
        Write-Host ""
        $Again = Read-Host "Ask another? (Y/n)"
    } while ($Again -notin @("n", "N", "no", "No"))
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Wait-ForUser
    exit 1
}

Wait-ForUser
exit 0
