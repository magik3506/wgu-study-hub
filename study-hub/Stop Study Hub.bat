@echo off
setlocal
title Stop WGU Study Hub
cd /d "%~dp0"

py -3 --version >nul 2>nul
if %errorlevel%==0 (
  py -3 wgu_study_hub.py --stop
  goto :done
)
python --version >nul 2>nul
if %errorlevel%==0 (
  python wgu_study_hub.py --stop
  goto :done
)
python3 --version >nul 2>nul
if %errorlevel%==0 (
  python3 wgu_study_hub.py --stop
  goto :done
)
echo  Python was not found - but then the hub can't be running either.

:done
echo.
pause
