@echo off
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
if not exist %PYTHON% set PYTHON=python

%PYTHON% main.py workflows --open
if errorlevel 1 (
    echo.
    echo Showing quick reference in this window instead...
    echo.
    %PYTHON% main.py workflows
)

echo.
pause
