# Register the daily sync task. Run once after setup.
$ProjectRoot = $PSScriptRoot
$SyncScript = Join-Path $ProjectRoot "run_sync.ps1"

$Hour = 21
$SettingsPath = Join-Path $ProjectRoot "config\settings.json"
if (Test-Path $SettingsPath) {
    try {
        $Settings = Get-Content $SettingsPath -Raw | ConvertFrom-Json
        if ($null -ne $Settings.sync_schedule_hour) {
            $Hour = [int]$Settings.sync_schedule_hour
        }
    } catch {
        Write-Host "Could not read sync_schedule_hour from settings.json — using 9 PM" -ForegroundColor Yellow
    }
}

if ($Hour -eq 0) {
    $AtLabel = "12:00AM"
} elseif ($Hour -eq 12) {
    $AtLabel = "12:00PM"
} elseif ($Hour -gt 12) {
    $AtLabel = "$($Hour - 12):00PM"
} else {
    $AtLabel = "${Hour}:00AM"
}

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$SyncScript`""

$Trigger = New-ScheduledTaskTrigger -Daily -At $AtLabel

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "NoteRescueDailySync" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily Notepad++ note rescue sync (hour from config/settings.json)" `
    -Force

Write-Host "Scheduled task registered: NoteRescueDailySync (daily at $AtLabel, hour=$Hour in settings.json)"
Write-Host "Runs: $SyncScript"
