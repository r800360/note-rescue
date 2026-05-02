$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Users\bsach\Documents\note-rescue\run_sync.ps1"

$Trigger = New-ScheduledTaskTrigger -Daily -At 9:00PM

Register-ScheduledTask -TaskName "NoteRescueDailySync" -Action $Action -Trigger $Trigger -Description "Daily Notepad++ note rescue sync"