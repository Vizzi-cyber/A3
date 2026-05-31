@echo off
chcp 65001 >nul
echo Starting Backend Server...
cd /d C:\Users\15722\Desktop\开发\软件杯A3\A3_项目框架\backend
start "Backend Server" cmd /k "venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo Starting Frontend Server...
cd /d C:\Users\15722\Desktop\开发\软件杯A3\A3_项目框架\frontend
start "Frontend Server" cmd /k "npm run dev"
echo Done! Backend: http://localhost:8000, Frontend: http://localhost:5173