@echo off
chcp 65001 > nul
cd /d "C:\Users\user\Desktop\bot"
call venv\Scripts\activate.bat
python bot.py
pause