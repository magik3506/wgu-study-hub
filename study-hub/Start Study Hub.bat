@echo off
setlocal
title WGU Study Hub
cd /d "%~dp0"

rem --- find a Python 3 -------------------------------------------------
py -3 --version >nul 2>nul
if %errorlevel%==0 (
  py -3 wgu_study_hub.py %*
  goto :done
)
python --version >nul 2>nul
if %errorlevel%==0 (
  python wgu_study_hub.py %*
  goto :done
)
python3 --version >nul 2>nul
if %errorlevel%==0 (
  python3 wgu_study_hub.py %*
  goto :done
)

echo.
echo  ============================================================
echo   Python 3 was not found on this computer.
echo.
echo   The Study Hub needs Python (free, ~30 MB) to run:
echo     1. Go to   https://www.python.org/downloads/
echo     2. Download and run the installer
echo     3. IMPORTANT: tick the box "Add python.exe to PATH"
echo     4. Double-click "Start Study Hub.bat" again
echo.
echo   Nothing else to install - no npm, no Node, no pip.
echo  ============================================================
echo.
pause
goto :eof

:done
if %errorlevel% neq 0 (
  echo.
  echo  The hub stopped with an error - the message above has details.
  pause
)
