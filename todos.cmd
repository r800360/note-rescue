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
echo TODO CLEANUP — 3 STEPS (complete all three):
echo   Step 1: Done — list is open in Notepad++
echo   Step 2: Change - [ ] to - [x] for done or not relevant, then SAVE
echo   Step 3: Run todos.cmd apply  (or double-click todos.cmd and type: apply)
echo.
echo Until step 3, checked items stay in the list and show on go.cmd.
echo.

:done
Read-Host "Press Enter to close"
