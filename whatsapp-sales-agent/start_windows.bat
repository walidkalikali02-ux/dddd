@echo off
cd /d "%~dp0"
title WhatsApp Sales Agent - keep this window open
echo Starting the agent. The dashboard will open at http://localhost:8000
echo Keep this window open while the agent is working.
python -m sales_agent serve
echo.
echo The agent stopped. If you see an error above, send a screenshot of it.
pause
