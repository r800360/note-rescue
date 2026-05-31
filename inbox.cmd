@echo off
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
if not exist %PYTHON% set PYTHON=python

%PYTHON% main.py open inbox
echo.
Read-Host "Press Enter to close"
