@echo off
chcp 65001
cls

echo ==========================================
echo  AI Learning System - 启动脚本
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
    echo 如需前端开发，请先安装Node.js 18+
    echo.
)

echo [1/4] 检查虚拟环境...
if not exist backend\venv (
    echo 创建虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

echo [2/4] 安装后端依赖...
cd backend
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
cd ..

echo [3/4] 检查环境变量...
if not exist backend\.env (
    echo 复制环境变量模板...
    copy backend\.env.example backend\.env
    echo [警告] 请编辑 backend\.env 文件，填写科大讯飞API密钥
)

echo [4/4] 启动服务...
echo.
echo ==========================================
echo  后端服务启动中...
echo  API文档: http://localhost:8000/docs
echo ==========================================
echo.

cd backend
start "Backend Server" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

REM 检查Node.js后启动前端
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

    cd frontend
    if not exist node_modules (
        echo 安装前端依赖...
        npm install
    )
    start "Frontend Server" cmd /k "npm run dev"
    cd ..
)

echo.
echo ==========================================
echo  服务启动完成！
echo ==========================================
echo.
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

pause
