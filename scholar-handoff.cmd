@echo off
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
if not exist %PYTHON% set PYTHON=python

echo Exporting handoff summaries for all 8 scholars...
echo.

set OUT=data\reports\scholar_handoffs_2025-26.csv
%PYTHON% main.py scholar handoff --output "%OUT%"

echo.
echo Open the CSV in Excel or Google Sheets and paste into your spreadsheet.
echo File: %OUT%
echo.
pause
