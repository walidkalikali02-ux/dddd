@echo off
cd /d "%~dp0"
echo Starting the installer...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_windows.ps1"
if errorlevel 1 pause
