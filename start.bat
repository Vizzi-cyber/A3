@echo off
chcp 65001 >nul
cls
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
set "BACKEND_PORT=8010"
set "FRONTEND_PORT=5180"

echo ==========================================
echo  LearnLab - 启动脚本
echo ==========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.9+
    pause
    exit /b 1
)

REM 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到Node.js，前端将无法启动
    echo.
)

echo [1/4] 检查虚拟环境...
if not exist "%ROOT%\backend\venv" (
    echo 创建虚拟环境...
    cd "%ROOT%\backend"
    python -m venv venv
    cd "%ROOT%"
)

echo [2/4] 检查后端依赖...
cd "%ROOT%\backend"
if exist "%ROOT%\backend\venv\Scripts\activate.bat" (
    call "%ROOT%\backend\venv\Scripts\activate.bat"
    python -c "import fastapi,uvicorn,pydantic,sqlalchemy,httpx,langchain,langgraph,openai,aiosqlite,pptx,jose,passlib,pyBKT,fsrs,mabwiser,scipy" >nul 2>&1
    if errorlevel 1 (
        echo 安装缺失的后端依赖...
        pip install -q -r requirements.txt
        if errorlevel 1 (
            echo [错误] 后端依赖安装失败
            pause
            exit /b 1
        )
    ) else (
        echo [OK] 后端依赖已就绪
    )
) else (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
)
cd "%ROOT%"

echo [3/4] 检查环境变量...
if not exist "%ROOT%\backend\.env" (
    if exist "%ROOT%\backend\.env.example" (
        copy "%ROOT%\backend\.env.example" "%ROOT%\backend\.env"
        echo [警告] 已从 .env.example 创建 .env 文件
        echo [警告] 请编辑 backend\.env 填写 API 密钥后重新启动
        pause
        exit /b 1
    ) else (
        echo [错误] 找不到 .env.example 文件
        pause
        exit /b 1
    )
)

echo [4/4] 启动服务...

echo.
echo ==========================================
echo  后端服务启动中...
echo  API文档: http://localhost:%BACKEND_PORT%/docs
echo ==========================================
echo.

set "BACKEND_READY="
call :check_backend
if not errorlevel 1 set "BACKEND_READY=1"
if defined BACKEND_READY (
    echo [OK] 检测到 LearnLab 后端已运行，继续复用
) else (
    call :port_in_use %BACKEND_PORT%
    if not errorlevel 1 (
        echo [错误] 端口 %BACKEND_PORT% 已被其他程序占用，未终止该程序
        pause
        exit /b 1
    )
    start "LearnLab-Backend" /D "%ROOT%\backend" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT%"
)

REM 等待后端启动
echo 等待后端服务就绪...
for /l %%i in (1,1,15) do (
    if not defined BACKEND_READY (
        call :check_backend
        if not errorlevel 1 set "BACKEND_READY=1"
        if not defined BACKEND_READY timeout /t 2 /nobreak >nul
    )
)
if defined BACKEND_READY (
    echo [OK] 后端服务已就绪
) else (
    echo [错误] 后端未能启动，请检查后端窗口中的错误信息
    pause
    exit /b 1
)

REM 启动前端
node --version >nul 2>&1
if errorlevel 1 (
    echo [跳过] 前端服务未启动（Node.js未安装）
) else (
    echo.
    echo ==========================================
    echo  前端服务启动中...
    echo  访问: http://localhost:%FRONTEND_PORT%
    echo ==========================================
    echo.

    cd "%ROOT%\frontend"
    if not exist node_modules (
        echo 安装前端依赖...
        call npm install
    )
    set "FRONTEND_READY="
    call :check_frontend
    if not errorlevel 1 set "FRONTEND_READY=1"
    if defined FRONTEND_READY (
        echo [OK] 检测到 LearnLab 前端已运行，继续复用
    ) else (
        call :port_in_use %FRONTEND_PORT%
        if not errorlevel 1 (
            echo [错误] 端口 %FRONTEND_PORT% 已被其他程序占用，未终止该程序
            pause
            exit /b 1
        )
        start "LearnLab-Frontend" /D "%ROOT%\frontend" cmd /k "set VITE_PROXY_TARGET=http://127.0.0.1:%BACKEND_PORT%&& npm run dev -- --host 127.0.0.1 --port %FRONTEND_PORT% --strictPort"
    )
    cd "%ROOT%"

    for /l %%i in (1,1,15) do (
        if not defined FRONTEND_READY (
            call :check_frontend
            if not errorlevel 1 set "FRONTEND_READY=1"
            if not defined FRONTEND_READY timeout /t 1 /nobreak >nul
        )
    )
    if defined FRONTEND_READY (
        echo [OK] 前端服务已就绪
    ) else (
        echo [错误] 前端未能启动，请检查前端窗口中的错误信息
        pause
        exit /b 1
    )
)

echo.
echo ==========================================
echo  LearnLab 启动完成！
echo ==========================================
echo.
echo  后端API: http://localhost:%BACKEND_PORT%
echo  API文档: http://localhost:%BACKEND_PORT%/docs
echo  前端页面: http://localhost:%FRONTEND_PORT%
echo.
echo  测试账号:
echo  学生: student_001 / 123456
echo  教师: T001 / Teacher123
echo.

pause
exit /b 0

:check_backend
set "CHECK_FILE=%ROOT%\.learnlab-backend-check.tmp"
curl -sf http://127.0.0.1:%BACKEND_PORT%/openapi.json -o "%CHECK_FILE%" >nul 2>&1
if errorlevel 1 exit /b 1
findstr /C:"LearnLab" "%CHECK_FILE%" >nul
set "CHECK_STATUS=!errorlevel!"
del /q "%CHECK_FILE%" >nul 2>&1
exit /b !CHECK_STATUS!

:check_frontend
set "CHECK_FILE=%ROOT%\.learnlab-frontend-check.tmp"
curl -sf http://127.0.0.1:%FRONTEND_PORT%/ -o "%CHECK_FILE%" >nul 2>&1
if errorlevel 1 exit /b 1
findstr /C:"<title>LearnLab" "%CHECK_FILE%" >nul
set "CHECK_STATUS=!errorlevel!"
del /q "%CHECK_FILE%" >nul 2>&1
exit /b !CHECK_STATUS!

:port_in_use
set "CHECK_FILE=%ROOT%\.learnlab-port-check.tmp"
netstat -ano > "%CHECK_FILE%" 2>nul
findstr /R /C:":%~1 .*LISTENING" "%CHECK_FILE%" >nul
set "CHECK_STATUS=!errorlevel!"
del /q "%CHECK_FILE%" >nul 2>&1
exit /b !CHECK_STATUS!
