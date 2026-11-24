@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === تسطيب ايجنت المبيعات ===
where python >nul 2>nul || (echo Python مش متسطب. نزله من python.org وعلّم على "Add to PATH" & pause & exit /b 1)
where node >nul 2>nul || (echo Node.js مش متسطب. نزله من nodejs.org & pause & exit /b 1)
python -m pip install -r requirements.txt || (pause & exit /b 1)
cd bridge && call npm install && cd ..
if not exist .env copy .env.example .env
echo.
echo تمام! افتح ملف .env وحط ANTHROPIC_API_KEY، وبعدين شغّل start_windows.bat
pause
