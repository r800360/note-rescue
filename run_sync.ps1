$ProjectRoot = "C:\Users\bsach\Documents\note-rescue"
$LogDir = Join-Path $ProjectRoot "data\logs"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogDir "sync_$Timestamp.log"

Set-Location $ProjectRoot

& ".\.venv\Scripts\Activate.ps1"

"[$(Get-Date)] Starting note-rescue sync" | Tee-Object -FilePath $LogFile -Append
python main.py sync *>&1 | Tee-Object -FilePath $LogFile -Append
"[$(Get-Date)] Finished note-rescue sync" | Tee-Object -FilePath $LogFile -Append