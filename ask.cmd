@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launchers\ask.ps1"
if errorlevel 1 (
    echo.
    echo ask.cmd exited with an error.
    pause
)
