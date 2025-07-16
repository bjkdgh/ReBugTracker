@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

:welcome
cls
echo ========================================
echo  ReBugTracker Windows 一键部署脚本
echo ========================================
echo.
echo 本脚本将引导您完成 ReBugTracker 在 Windows 系统的完整部署
echo 支持以下部署方式：
echo - Docker 容器部署
echo - 本地开发环境部署
echo - Windows 服务部署（生产环境推荐）
echo.
echo 包含的工具：
echo - NSSM Windows 服务管理器
echo - PostgreSQL 便携版数据库
echo - Waitress 生产级 WSGI 服务器
echo.
echo 按任意键开始部署...
pause >nul

:check_environment
cls
echo ========================================
echo  环境检查
echo ========================================
echo.
echo 正在检查系统环境...

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [成功] Python 版本: !PYTHON_VERSION!
)

pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 pip
    pause
    exit /b 1
) else (
    echo [成功] pip 可用
)

docker --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未找到 Docker（Docker部署需要）
    set DOCKER_AVAILABLE=no
) else (
    echo [成功] Docker 可用
    set DOCKER_AVAILABLE=yes
)

echo.
echo 环境检查完成！
pause

:choose_deployment
cls
echo ========================================
echo  选择部署模式
echo ========================================
echo.
echo 1) Docker 部署
echo    - 环境隔离，避免冲突
echo    - 一键启动，易于管理
echo    - 需要 Docker Desktop
if "%DOCKER_AVAILABLE%"=="no" (
    echo    [不可用] Docker 未安装
)
echo.
echo 2) 本地开发部署
echo    - 直接运行，便于开发调试
echo    - 使用 Flask 开发服务器
echo    - 使用虚拟环境隔离
echo.
echo 3) Windows 服务部署（生产环境推荐）
echo    - 使用 NSSM 管理 Windows 服务
echo    - 使用 Waitress 生产级服务器
echo    - 开机自动启动，稳定可靠
echo    - 支持便携版 PostgreSQL
echo.

:deployment_loop
set /p choice="请选择部署模式 (1-3): "
if "%choice%"=="1" (
    if "%DOCKER_AVAILABLE%"=="no" (
        echo [错误] Docker 不可用，无法选择 Docker 部署
        echo 请安装 Docker Desktop 或选择其他部署方式
        goto deployment_loop
    )
    set DEPLOYMENT_MODE=docker
    echo [成功] 已选择：Docker 部署
    goto choose_database
)
if "%choice%"=="2" (
    set DEPLOYMENT_MODE=local
    echo [成功] 已选择：本地开发部署
    goto choose_database
)
if "%choice%"=="3" (
    set DEPLOYMENT_MODE=service
    echo [成功] 已选择：Windows 服务部署
    goto choose_database
)
echo [错误] 无效选择，请输入 1、2 或 3
goto deployment_loop

:choose_database
cls
echo ========================================
echo  选择数据库类型
echo ========================================
echo.
echo 1) SQLite（推荐新手）
echo    - 零配置，开箱即用
echo    - 适合小团队使用
echo    - 数据文件便于备份
echo.
echo 2) PostgreSQL（推荐生产）
echo    - 高性能，支持大并发
echo    - 适合大团队使用
echo    - 企业级数据库功能
if "%DEPLOYMENT_MODE%"=="docker" (
    echo    - Docker 会自动配置 PostgreSQL
) else if "%DEPLOYMENT_MODE%"=="service" (
    echo    - 可选择便携版 PostgreSQL（免安装）
    echo    - 或使用已安装的 PostgreSQL 服务
) else (
    echo    - 需要手动安装和配置 PostgreSQL
)
echo.

:database_loop
set /p choice="请选择数据库类型 (1-2): "
if "%choice%"=="1" (
    set DATABASE_TYPE=sqlite
    echo [成功] 已选择：SQLite 数据库
    goto confirm_deployment
)
if "%choice%"=="2" (
    set DATABASE_TYPE=postgres
    echo [成功] 已选择：PostgreSQL 数据库
    goto confirm_deployment
)
echo [错误] 无效选择，请输入 1 或 2
goto database_loop

:confirm_deployment
cls
echo ========================================
echo  确认部署配置
echo ========================================
echo.
echo 部署模式：%DEPLOYMENT_MODE%
echo 数据库类型：%DATABASE_TYPE%
echo 项目目录：%cd%
echo.
echo 即将执行的操作：
if "%DEPLOYMENT_MODE%"=="docker" (
    echo 1. 检查 Docker Compose 文件
    echo 2. 构建 Docker 镜像
    echo 3. 启动容器服务
    echo 4. 初始化数据库
) else if "%DEPLOYMENT_MODE%"=="service" (
    echo 1. 检查部署工具（NSSM、Waitress）
    echo 2. 创建 Python 虚拟环境
    echo 3. 安装项目依赖和 Waitress
    echo 4. 配置数据库连接
    echo 5. 解压并配置 NSSM
    echo 6. 安装并启动 Windows 服务
) else (
    echo 1. 创建 Python 虚拟环境
    echo 2. 安装项目依赖
    echo 3. 配置数据库连接
    echo 4. 初始化数据库
    echo 5. 启动开发服务器
)
echo.

:confirm_loop
set /p confirm="确认开始部署？(y/N): "
if /i "%confirm%"=="y" goto start_deployment
if /i "%confirm%"=="yes" goto start_deployment
if /i "%confirm%"=="n" goto welcome
if /i "%confirm%"=="no" goto welcome
if "%confirm%"=="" goto welcome
echo [错误] 请输入 y 或 n
goto confirm_loop

:start_deployment
cls
echo ========================================
echo  开始部署
echo ========================================
echo.

if "%DEPLOYMENT_MODE%"=="docker" (
    goto docker_deployment
) else if "%DEPLOYMENT_MODE%"=="service" (
    goto service_deployment
) else (
    goto local_deployment
)

:docker_deployment
echo [Docker] Docker 部署模式
echo.

echo [步骤 1/4] 检查 Docker Compose 文件
if not exist "docker-compose.yml" (
    echo [错误] 未找到 docker-compose.yml 文件
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)
echo [成功] Docker Compose 文件存在

echo.
echo [步骤 2/4] 构建 Docker 镜像
echo 正在构建镜像，请稍候...
docker-compose build
if errorlevel 1 (
    echo [错误] Docker 镜像构建失败
    pause
    exit /b 1
)
echo [成功] Docker 镜像构建完成

echo.
echo [步骤 3/4] 启动容器服务
echo 正在启动服务...
docker-compose up -d
if errorlevel 1 (
    echo [错误] 容器启动失败
    pause
    exit /b 1
)
echo [成功] 容器服务启动成功

echo.
echo [步骤 4/4] 等待服务就绪
echo 等待数据库初始化...
timeout /t 10 /nobreak >nul
echo [成功] 服务就绪

goto deployment_complete

:service_deployment
echo [服务] Windows 服务部署模式
echo.

echo [步骤 1/6] 检查部署工具
if not exist "deployment_tools\nssm-2.24.zip" (
    echo [错误] 未找到 NSSM 工具包
    echo 请确保 deployment_tools\nssm-2.24.zip 文件存在
    pause
    exit /b 1
)
echo [成功] NSSM 工具包存在

if not exist "deployment_tools\run_waitress.py" (
    echo [错误] 未找到 Waitress 运行脚本
    pause
    exit /b 1
)
echo [成功] Waitress 运行脚本存在

echo.
echo [步骤 2/6] 创建虚拟环境
if exist ".venv" (
    echo [跳过] 虚拟环境已存在
) else (
    echo 正在创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
)

echo.
echo [步骤 3/6] 安装依赖
echo 正在安装依赖包...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
pip install waitress
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [成功] 依赖安装完成

echo.
echo [步骤 4/6] 配置数据库
if "%DATABASE_TYPE%"=="sqlite" (
    echo 配置 SQLite 数据库...
    echo DATABASE_TYPE=sqlite > .env
    echo APP_PORT=8000 >> .env
    echo [成功] SQLite 配置完成
) else (
    echo 配置 PostgreSQL 数据库...
    echo.
    echo 检查便携版 PostgreSQL...
    if exist "deployment_tools\postgresql-17.5-3-windows-x64.exe" (
        echo [发现] PostgreSQL 便携版安装包
        set /p install_pg="是否安装便携版 PostgreSQL？(y/N): "
        if /i "!install_pg!"=="y" (
            echo 正在安装便携版 PostgreSQL...
            echo 请按照安装向导完成 PostgreSQL 安装
            start /wait deployment_tools\postgresql-17.5-3-windows-x64.exe
            echo [成功] PostgreSQL 安装完成
        )
    )
    echo DATABASE_TYPE=postgres > .env
    echo APP_PORT=8000 >> .env
    echo DATABASE_HOST=localhost >> .env
    echo DATABASE_PORT=5432 >> .env
    echo [成功] PostgreSQL 配置完成
)

echo.
echo [步骤 5/6] 解压并配置 NSSM
if not exist "deployment_tools\nssm.exe" (
    echo 正在解压 NSSM...
    powershell -Command "Expand-Archive -Path 'deployment_tools\nssm-2.24.zip' -DestinationPath 'deployment_tools\temp' -Force"
    copy "deployment_tools\temp\nssm-2.24\win64\nssm.exe" "deployment_tools\nssm.exe"
    rmdir /s /q "deployment_tools\temp"
    echo [成功] NSSM 解压完成
) else (
    echo [跳过] NSSM 已存在
)

echo.
echo [步骤 6/6] 安装 Windows 服务
echo 正在安装 ReBugTracker Windows 服务...
call deployment_tools\install_windows_service.bat
if errorlevel 1 (
    echo [错误] Windows 服务安装失败
    pause
    exit /b 1
)
echo [成功] Windows 服务安装完成

echo.
echo 正在启动 ReBugTracker 服务...
call deployment_tools\start_service.bat
if errorlevel 1 (
    echo [警告] 服务启动可能失败，请检查日志
) else (
    echo [成功] ReBugTracker 服务启动成功
)

goto deployment_complete

:local_deployment
echo [本地] 本地部署模式
echo.

echo [步骤 1/5] 创建虚拟环境
if exist ".venv" (
    echo [跳过] 虚拟环境已存在
) else (
    echo 正在创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
)

echo.
echo [步骤 2/5] 激活虚拟环境并安装依赖
echo 正在安装依赖包...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [成功] 依赖安装完成

echo.
echo [步骤 3/5] 配置数据库
if "%DATABASE_TYPE%"=="sqlite" (
    echo 配置 SQLite 数据库...
    echo DATABASE_TYPE=sqlite > .env
    echo [成功] SQLite 配置完成
) else (
    echo 配置 PostgreSQL 数据库...
    echo 请确保 PostgreSQL 服务已启动
    echo DATABASE_TYPE=postgres > .env
    echo [成功] PostgreSQL 配置完成
)

echo.
echo [步骤 4/5] 初始化数据库
echo 正在初始化数据库...
python database_tools\sync_tools\smart_sync_postgres_to_sqlite.py
if errorlevel 1 (
    echo [警告] 数据库同步可能失败，但继续部署
)
echo [成功] 数据库初始化完成

echo.
echo [步骤 5/5] 启动应用
echo 正在启动 ReBugTracker...
echo.
echo 应用将在 http://localhost:5000 启动
echo 默认管理员账号: admin
echo 默认管理员密码: admin
echo.
echo 按 Ctrl+C 停止服务
python rebugtracker.py

goto deployment_complete

:deployment_complete
cls
echo ========================================
echo  部署完成！
echo ========================================
echo.
echo [成功] ReBugTracker 部署成功！
echo.
echo 访问信息：
echo - 访问地址：http://localhost:5000
echo - 管理员账号：admin
echo - 管理员密码：admin
echo.
echo 部署配置：
echo - 部署模式：%DEPLOYMENT_MODE%
echo - 数据库类型：%DATABASE_TYPE%
echo.
if "%DEPLOYMENT_MODE%"=="docker" (
    echo Docker 管理命令：
    echo - 查看状态：docker-compose ps
    echo - 查看日志：docker-compose logs
    echo - 停止服务：docker-compose down
    echo - 重启服务：docker-compose restart
) else if "%DEPLOYMENT_MODE%"=="service" (
    echo Windows 服务管理：
    echo - 服务管理：deployment_tools\manage_windows_service.bat
    echo - 启动服务：deployment_tools\start_service.bat
    echo - 停止服务：net stop ReBugTracker
    echo - 重启服务：net stop ReBugTracker ^&^& net start ReBugTracker
    echo - 卸载服务：deployment_tools\uninstall_windows_service.bat
    echo - 查看日志：logs\ 目录
    echo - 服务端口：8000 （可在 .env 文件中修改 APP_PORT）
) else (
    echo 本地开发部署管理：
    echo - 启动服务：python rebugtracker.py
    echo - 虚拟环境：.venv\Scripts\activate.bat
    echo - 配置文件：.env
)
echo.
echo 感谢使用 ReBugTracker！
echo 如需技术支持，请查看项目文档。
echo.
pause
exit /b 0
