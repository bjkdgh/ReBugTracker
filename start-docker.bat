@echo off
REM ReBugTracker Windows 启动脚本
chcp 65001 >nul

echo 🚀 ReBugTracker 启动脚本
echo ==========================

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

REM 检查.env文件
if not exist .env (
    echo 📝 创建环境配置文件...
    copy .env.example .env >nul
    echo ✅ 已创建 .env 文件，请根据需要修改配置
)

REM 读取数据库类型
set DB_TYPE=postgres
for /f "tokens=2 delims==" %%a in ('findstr "^DB_TYPE=" .env 2^>nul') do set DB_TYPE=%%a

echo 📊 数据库类型: %DB_TYPE%

REM 根据数据库类型选择compose文件
if "%DB_TYPE%"=="sqlite" (
    set COMPOSE_FILE=docker-compose.sqlite.yml
    echo 🗄️ 使用 SQLite 模式
) else (
    set COMPOSE_FILE=docker-compose.yml
    echo 🐘 使用 PostgreSQL 模式
)

REM 构建并启动服务
echo 🔨 构建 Docker 镜像...
docker-compose -f %COMPOSE_FILE% build

echo 🚀 启动服务...
docker-compose -f %COMPOSE_FILE% up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose -f %COMPOSE_FILE% ps

REM 显示访问信息
echo.
echo ✅ ReBugTracker 启动完成！
echo 🌐 访问地址: http://localhost:5000
echo 👤 默认管理员账号: admin / admin
echo.
echo 📋 常用命令:
echo   查看日志: docker-compose -f %COMPOSE_FILE% logs -f
echo   停止服务: docker-compose -f %COMPOSE_FILE% down
echo   重启服务: docker-compose -f %COMPOSE_FILE% restart
echo.
pause
