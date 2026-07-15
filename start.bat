@echo off
chcp 65001 >nul
cls

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

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

echo [2/4] 安装后端依赖...
cd "%ROOT%\backend"
if exist "%ROOT%\backend\venv\Scripts\activate.bat" (
    call "%ROOT%\backend\venv\Scripts\activate.bat"
    pip install -q -r requirements.txt
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

REM 清理旧的后端进程
echo 清理旧进程...
for /f "tokens=5" %%p in ('netstat -ano ^| find ":8000 " ^| find "LISTENING"') do (
    echo 关闭端口 8000 上的旧进程 PID: %%p
    taskkill /F /PID %%p >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo  后端服务启动中...
echo  API文档: http://localhost:8000/docs
echo ==========================================
echo.

cd "%ROOT%\backend"
start "LearnLab-Backend" cmd /k "call "%ROOT%\backend\venv\Scripts\activate.bat" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
cd "%ROOT%"

REM 等待后端启动
echo 等待后端服务就绪...
set "BACKEND_READY="
for /l %%i in (1,1,15) do (
    >nul 2>&1 curl -s http://localhost:8000/docs && set "BACKEND_READY=1" && goto :backend_ok
    >nul 2>&1 timeout /t 2 /nobreak
)
:backend_ok
if defined BACKEND_READY (
    echo [OK] 后端服务已就绪
) else (
    echo [警告] 后端服务启动可能较慢，请稍后手动检查 http://localhost:8000/docs
)

REM 启动前端
node --version >nul 2>&1
if errorlevel 1 (
    echo [跳过] 前端服务未启动（Node.js未安装）
) else (
    echo.
    echo ==========================================
    echo  前端服务启动中...
    echo  访问: http://localhost:5173
    echo ==========================================
    echo.

    cd "%ROOT%\frontend"
    if not exist node_modules (
        echo 安装前端依赖...
        call npm install
    )
    start "LearnLab-Frontend" cmd /k "npm run dev"
    cd "%ROOT%"
)

echo.
echo ==========================================
echo  LearnLab 启动完成！
echo ==========================================
echo.
echo  后端API: http://localhost:8000
echo  API文档: http://localhost:8000/docs
echo  前端页面: http://localhost:5173
echo.
echo  测试账号:
echo  学生: student_001 / 123456
echo  教师: T001 / Teacher123
echo.

pause
