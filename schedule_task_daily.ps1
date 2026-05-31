# Register the daily 9 PM sync task. Run once after setup.
$ProjectRoot = $PSScriptRoot
$SyncScript = Join-Path $ProjectRoot "run_sync.ps1"

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$SyncScript`""

$Trigger = New-ScheduledTaskTrigger -Daily -At 9:00PM

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "NoteRescueDailySync" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily Notepad++ note rescue sync at 9 PM" `
    -Force

Write-Host "Scheduled task registered: NoteRescueDailySync (daily at 9:00 PM)"
Write-Host "Runs: $SyncScript"
