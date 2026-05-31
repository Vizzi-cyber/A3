@echo off
cd /d "C:\Users\Vizzi\Desktop\A3_项目框架\backend"
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
