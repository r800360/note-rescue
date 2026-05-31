@echo off
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
if not exist %PYTHON% set PYTHON=python

if /I "%~1"=="apply" (
    echo Applying checkmarks - items marked [x] will be removed permanently...
    echo.
    %PYTHON% main.py todos-apply
    goto :done
)

echo Refreshing TODO list and opening in Notepad++...
echo.
%PYTHON% main.py todos --open
echo.
echo HOW TO CLEAR ITEMS:
echo   1. Change - [ ] to - [x] for done or not relevant
echo   2. Save the file in Notepad++
echo   3. Double-click todos.cmd again and type: apply
echo      Or run: todos.cmd apply
echo.

:done
Read-Host "Press Enter to close"
