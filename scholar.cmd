@echo off
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
if not exist %PYTHON% set PYTHON=python

echo.
echo  Scholar meeting prep
echo  ===================
echo.

%PYTHON% main.py scholar list
echo.

set /p SCHOLAR="Scholar name (from list above): "

if "%SCHOLAR%"=="" (
  echo No scholar entered.
  goto :done
)

set /p TOPIC="What do they need help with? (Enter to skip): "

echo.
if "%TOPIC%"=="" (
  %PYTHON% main.py scholar show "%SCHOLAR%"
) else (
  %PYTHON% main.py scholar show "%SCHOLAR%" --topic "%TOPIC%"
)

:done
echo.
Read-Host "Press Enter to close"
