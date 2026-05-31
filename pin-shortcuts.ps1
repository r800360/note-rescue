# Pin note-rescue to Start menu and taskbar (Windows 11 compatible).
$ProjectRoot = $PSScriptRoot
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\note-rescue"
$DesktopDir = [Environment]::GetFolderPath("Desktop")
$PythonW = Join-Path $ProjectRoot ".venv\Scripts\pythonw.exe"

if (!(Test-Path $PythonW)) {
    Write-Host "ERROR: Run setup.ps1 first (.venv missing)." -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Path $StartMenuDir -Force | Out-Null

function New-NoteRescueShortcut {
    param(
        [string]$Path,
        [string]$PywScript,
        [string]$PsScript,
        [string]$Description,
        [string]$IconLocation = "$env:SystemRoot\System32\imageres.dll,109",
        [ValidateSet("Taskbar", "Desktop")]
        [string]$Kind = "Taskbar"
    )

    $Wsh = New-Object -ComObject WScript.Shell
    $Sc = $Wsh.CreateShortcut($Path)

    if ($Kind -eq "Desktop") {
        $Sc.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
        $Sc.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PsScript`""
    } else {
        $Sc.TargetPath = $PythonW
        $Sc.Arguments = "`"$PywScript`""
    }

    $Sc.WorkingDirectory = $ProjectRoot
    $Sc.Description = $Description
    $Sc.IconLocation = $IconLocation
    $Sc.Save()
}

$GoPyw = Join-Path $ProjectRoot "launchers\go.pyw"
$FindPyw = Join-Path $ProjectRoot "launchers\find.pyw"
$GoPs = Join-Path $ProjectRoot "launchers\dashboard.ps1"
$FindPs = Join-Path $ProjectRoot "launchers\find-notes.ps1"

$Shortcuts = @(
    @{
        Name = "note-rescue Dashboard"
        Pyw = $GoPyw
        Ps = $GoPs
        Desc = "note-rescue status dashboard"
        Icon = "$env:SystemRoot\System32\imageres.dll,109"
    },
    @{
        Name = "note-rescue Find Notes"
        Pyw = $FindPyw
        Ps = $FindPs
        Desc = "Search rescued notes and open in Notepad++"
        Icon = "$env:SystemRoot\System32\imageres.dll,176"
    }
)

foreach ($Item in $Shortcuts) {
    $StartLnk = Join-Path $StartMenuDir "$($Item.Name).lnk"
    $DesktopLnk = Join-Path $DesktopDir "$($Item.Name).lnk"
    New-NoteRescueShortcut -Path $StartLnk -PywScript $Item.Pyw -PsScript $Item.Ps -Description $Item.Desc -IconLocation $Item.Icon -Kind "Taskbar"
    New-NoteRescueShortcut -Path $DesktopLnk -PywScript $Item.Pyw -PsScript $Item.Ps -Description $Item.Desc -IconLocation $Item.Icon -Kind "Desktop"
}

function New-LayoutModificationXml {
    param(
        [string[]]$LnkPaths,
        [string]$OutputPath,
        [ValidateSet("Append", "Replace")]
        [string]$PinListPlacement = "Replace"
    )

    $xml = New-Object System.Xml.XmlDocument
    $root = $xml.CreateElement("LayoutModificationTemplate", "http://schemas.microsoft.com/Start/2014/LayoutModification")
    $xml.AppendChild($root) | Out-Null
    $root.SetAttribute("xmlns:defaultlayout", "http://schemas.microsoft.com/Start/2014/FullDefaultLayout")
    $root.SetAttribute("xmlns:taskbar", "http://schemas.microsoft.com/Start/2014/TaskbarLayout")
    $root.SetAttribute("Version", "1")

    $collection = $xml.CreateElement("CustomTaskbarLayoutCollection", $root.NamespaceURI)
    $collection.SetAttribute("PinListPlacement", $PinListPlacement)
    $root.AppendChild($collection) | Out-Null

    $layout = $xml.CreateElement("defaultlayout:TaskbarLayout", $root.GetAttribute("xmlns:defaultlayout"))
    $collection.AppendChild($layout) | Out-Null

    $pinList = $xml.CreateElement("taskbar:TaskbarPinList", $root.GetAttribute("xmlns:taskbar"))
    $layout.AppendChild($pinList) | Out-Null

    foreach ($lnk in $LnkPaths) {
        $desktopApp = $xml.CreateElement("taskbar:DesktopApp", $root.GetAttribute("xmlns:taskbar"))
        $desktopApp.SetAttribute("DesktopApplicationLinkPath", $lnk)
        $pinList.AppendChild($desktopApp) | Out-Null
    }

    $shellDir = Split-Path $OutputPath -Parent
    if (!(Test-Path $shellDir)) {
        New-Item -ItemType Directory -Path $shellDir -Force | Out-Null
    }
    $xml.Save($OutputPath)
}

# Keep your existing pins, add note-rescue at the end.
$LnkPaths = @(
    "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Microsoft Edge.lnk",
    "%APPDATA%\Microsoft\Windows\Start Menu\Programs\File Explorer.lnk",
    "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Norton 360.lnk",
    "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Notepad++.lnk",
    "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk",
    "%APPDATA%\Microsoft\Windows\Start Menu\Programs\note-rescue\note-rescue Dashboard.lnk",
    "%APPDATA%\Microsoft\Windows\Start Menu\Programs\note-rescue\note-rescue Find Notes.lnk"
)

$XmlPath = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Shell\LayoutModification.xml"
New-LayoutModificationXml -LnkPaths $LnkPaths -OutputPath $XmlPath -PinListPlacement "Replace"

Write-Host "Applying taskbar layout (Explorer will restart briefly)..." -ForegroundColor Yellow

# Remove old PowerShell-based pins that Windows 11 ignores on the taskbar.
$TaskbarDir = Join-Path $env:APPDATA "Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"
Get-ChildItem $TaskbarDir -Filter "note-rescue*.lnk" -ErrorAction SilentlyContinue | Remove-Item -Force

Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Shell\DefaultLayouts" -Recurse -Force -ErrorAction SilentlyContinue

Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 4
Remove-Item $XmlPath -Force -ErrorAction SilentlyContinue
Start-Process explorer

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host "  Start menu: $StartMenuDir"
Write-Host "  Desktop:    note-rescue Dashboard, note-rescue Find Notes"
Write-Host "  Taskbar:    both icons should appear after Explorer restarts"
Write-Host ""
Write-Host "If taskbar icons are still missing, right-click the Desktop shortcuts"
Write-Host "and choose Pin to taskbar (Windows 11 blocks fully automatic pinning sometimes)."
