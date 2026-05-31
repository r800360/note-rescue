# Daily sync wrapper — invoked by Windows Scheduled Task at 9 PM.
$ProjectRoot = $PSScriptRoot
$LogDir = Join-Path $ProjectRoot "data\logs"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogDir "sync_$Timestamp.log"

Set-Location $ProjectRoot

function Write-Log($Message) {
    $Line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    $Line | Tee-Object -FilePath $LogFile -Append
}

Write-Log "Starting note-rescue sync"

if (Test-Path $VenvPython) {
    $Python = $VenvPython
} else {
    $Python = "python"
    Write-Log "WARNING: .venv not found, using system python"
}

try {
    & $Python main.py sync 2>&1 | Tee-Object -FilePath $LogFile -Append
    $ExitCode = $LASTEXITCODE
} catch {
    Write-Log "ERROR: sync failed — $_"
    $ExitCode = 1

    # Toast on failure (sync success toast is handled by Python)
    $FailScript = @"
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
`$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
`$xml.LoadXml('<toast><visual><binding template="ToastGeneric"><text>note-rescue sync FAILED</text><text>Check data/logs/ for details.</text></binding></visual></toast>')
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("note-rescue").Show([Windows.UI.Notifications.ToastNotification]::new(`$xml))
"@
    powershell -NoProfile -ExecutionPolicy Bypass -Command $FailScript
}

if ($ExitCode -ne 0) {
    Write-Log "Finished with errors (exit $ExitCode)"
    exit $ExitCode
}

Write-Log "Finished note-rescue sync"
exit 0
