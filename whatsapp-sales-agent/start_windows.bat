@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -m sales_agent serve
pause
