@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launchers\site.ps1"
if errorlevel 1 (
    echo.
    echo site.cmd exited with an error.
    pause
)
