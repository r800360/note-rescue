@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0reset-npp.ps1" %*
if errorlevel 1 (
    echo.
    echo reset-npp.cmd exited with an error.
    pause
)
