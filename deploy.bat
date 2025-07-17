@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

REM 固定工作目录为脚本所在目录，解决管理员权限下路径问题
cd /d "%~dp0"
set "PROJECT_ROOT=%cd%"

:welcome
cls
echo ========================================
echo  ReBugTracker Windows 一键部署脚本
echo ========================================
echo.
echo 项目根目录: %PROJECT_ROOT%
echo.
echo 本脚本将引导您完成 ReBugTracker 在 Windows 系统的完整部署
echo 支持以下部署方式：
echo - Docker 容器部署
echo - 本地开发环境部署
echo - Windows 服务部署（生产环境推荐）
echo.
echo 包含的工具：
echo - NSSM Windows 服务管理器（需要下载）
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
    echo [错误] 未找到 Python，需要先安装 Python 3.8+
    echo.
    echo 官网下载地址: https://www.python.org/downloads/
    echo.
    echo 是否使用 Windows 默认工具自动下载 Python？
    echo.
    goto python_download_choice
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
echo    - 需要手动下载 NSSM 工具
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
    goto check_service_requirements
)
echo [错误] 无效选择，请输入 1、2 或 3
goto deployment_loop

:check_service_requirements
cls
echo ========================================
echo  Windows 服务部署要求检查
echo ========================================
echo.
echo 正在检查 Windows 服务部署所需工具...

REM 检查 NSSM - 使用绝对路径
set "NSSM_PATH=%cd%\deployment_tools\nssm.exe"
if not exist "%NSSM_PATH%" (
    echo [缺失] NSSM 工具未找到
    echo 查找路径: %NSSM_PATH%
    echo.
    echo 请下载 NSSM ^(Non-Sucking Service Manager^):
    echo 官网地址: https://nssm.cc/download
    echo.
    echo 下载完成后将 nssm.exe 放置到 deployment_tools\ 目录
    echo.
    goto nssm_download_wait
)
echo [成功] NSSM 工具已就绪: %NSSM_PATH%
goto check_waitress_script

:nssm_download_wait
set /p nssm_continue="下载完成后按 y 继续，或按 n 返回选择其他部署方式 (y/n): "
if /i "%nssm_continue%"=="n" goto choose_deployment
if /i "%nssm_continue%"=="y" (
    if not exist "%NSSM_PATH%" (
        echo [错误] 仍未找到 nssm.exe，请确保文件已正确放置
        echo 请检查路径: %NSSM_PATH%
        pause
        goto nssm_download_wait
    )
    echo [成功] NSSM 工具已就绪
    goto check_waitress_script
)
echo [错误] 请输入 y 或 n
goto nssm_download_wait

:check_waitress_script
if not exist "deployment_tools\run_waitress.py" (
    echo [错误] 未找到 Waitress 运行脚本
    echo 请确保 deployment_tools\run_waitress.py 文件存在
    pause
    exit /b 1
)
echo [成功] Waitress 运行脚本存在

echo.
echo Windows 服务部署要求检查完成！
pause
goto choose_database

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
    echo    - 需要手动安装 PostgreSQL 服务
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
    if "%DEPLOYMENT_MODE%" neq "docker" (
        goto check_postgres_installation
    )
    goto confirm_deployment
)
echo [错误] 无效选择，请输入 1 或 2
goto database_loop

:check_postgres_installation
cls
echo ========================================
echo  PostgreSQL 安装检查
echo ========================================
echo.
echo 正在检查 PostgreSQL 安装...

REM 检查 PostgreSQL 服务
sc query postgresql-x64-17 >nul 2>&1
if errorlevel 1 (
    sc query postgresql >nul 2>&1
    if errorlevel 1 (
        echo [缺失] PostgreSQL 服务未安装
        echo.
        echo 请安装 PostgreSQL 数据库:
        echo 1. 访问官网: https://www.postgresql.org/download/windows/
        echo 2. 下载 PostgreSQL 17.x Windows 安装包
        echo 3. 运行安装程序，记住设置的密码
        echo 4. 确保 PostgreSQL 服务已启动
        echo.
        echo 安装提示:
        echo - 端口: 5432 (默认)
        echo - 用户名: postgres (默认)
        echo - 密码: 请记住您设置的密码
        echo.
        goto postgres_install_wait
    ) else (
        echo [成功] PostgreSQL 服务已安装
    )
) else (
    echo [成功] PostgreSQL 17 服务已安装
)

echo.
echo PostgreSQL 检查完成！
pause
goto confirm_deployment

:postgres_install_wait
set /p pg_continue="安装完成后按 y 继续，或按 n 返回选择 SQLite (y/n): "
if /i "%pg_continue%"=="n" (
    set DATABASE_TYPE=sqlite
    echo [已切换] 已切换到 SQLite 数据库
    goto confirm_deployment
)
if /i "%pg_continue%"=="y" (
    goto check_postgres_installation
)
echo [错误] 请输入 y 或 n
goto postgres_install_wait

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
    echo 1. 创建 Python 虚拟环境
    echo 2. 安装项目依赖和 Waitress
    echo 3. 配置数据库连接
    echo 4. 安装并启动 Windows 服务
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

echo [步骤 1/4] 创建虚拟环境
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
echo [步骤 2/4] 安装依赖
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
echo [步骤 3/4] 配置数据库
if "%DATABASE_TYPE%"=="sqlite" (
    echo 配置 SQLite 数据库...
    echo DATABASE_TYPE=sqlite > .env
    echo APP_PORT=5000 >> .env
    echo [成功] SQLite 配置完成
) else (
    echo 配置 PostgreSQL 数据库...
    echo DATABASE_TYPE=postgres > .env
    echo APP_PORT=5000 >> .env
    echo DATABASE_HOST=localhost >> .env
    echo DATABASE_PORT=5432 >> .env
    echo DATABASE_NAME=rebugtracker >> .env
    echo DATABASE_USER=postgres >> .env
    set /p db_password="请输入 PostgreSQL 密码: "
    echo DATABASE_PASSWORD=%db_password% >> .env
    echo [成功] PostgreSQL 配置完成
)

echo.
echo [步骤 4/4] 安装 Windows 服务
echo 正在安装 ReBugTracker Windows 服务...
set "INSTALL_SCRIPT=%PROJECT_ROOT%\deployment_tools\install_windows_service.bat"
echo 调用安装脚本: %INSTALL_SCRIPT%
call "%INSTALL_SCRIPT%"
if errorlevel 1 (
    echo [错误] Windows 服务安装失败
    echo 安装脚本路径: %INSTALL_SCRIPT%
    pause
    exit /b 1
)
echo [成功] Windows 服务安装完成

echo.
echo 正在启动 ReBugTracker 服务...
set "START_SCRIPT=%PROJECT_ROOT%\deployment_tools\start_service.bat"
echo 调用启动脚本: %START_SCRIPT%
call "%START_SCRIPT%"
if errorlevel 1 (
    echo [警告] 服务启动可能失败，请检查日志
    echo 启动脚本路径: %START_SCRIPT%
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
    echo DATABASE_TYPE=postgres > .env
    echo DATABASE_HOST=localhost >> .env
    echo DATABASE_PORT=5432 >> .env
    echo DATABASE_NAME=rebugtracker >> .env
    echo DATABASE_USER=postgres >> .env
    set /p db_password="请输入 PostgreSQL 密码: "
    echo DATABASE_PASSWORD=%db_password% >> .env
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
if "%DEPLOYMENT_MODE%"=="service" (
    echo - 访问地址：http://localhost:5000
) else (
    echo - 访问地址：http://localhost:5000
)
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
    echo - 服务端口：5000 （可在 .env 文件中修改 APP_PORT）
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

:python_download_choice
cls
echo ========================================
echo  Python 安装向导
echo ========================================
echo.
echo 选择下载方式：
echo 1) PowerShell 下载（推荐）
echo 2) curl 下载（Windows 10 1803+）
echo 3) bitsadmin 下载（兼容所有Windows版本）
echo 4) 手动下载（显示下载命令）
echo n) 跳过安装
echo.

set /p download_choice="请选择 (1-4/n): "

if "%download_choice%"=="1" goto download_powershell
if "%download_choice%"=="2" goto download_curl
if "%download_choice%"=="3" goto download_bitsadmin
if "%download_choice%"=="4" goto download_manual
if /i "%download_choice%"=="n" goto skip_python

echo [错误] 无效选择，请输入 1、2、3、4 或 n
pause
goto python_download_choice

:download_powershell
echo.
echo [PowerShell] 正在使用 PowerShell 下载 Python 3.12.7...
echo 下载地址: https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo 保存位置: %cd%\python-installer.exe
echo.
echo 正在下载，请稍候...
powershell -Command "& {try {$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile 'python-installer.exe' -UseBasicParsing; Write-Host '[成功] Python 安装包下载完成'} catch {Write-Host '[错误] 下载失败:' $_.Exception.Message; exit 1}}"
if errorlevel 1 (
    echo [错误] PowerShell 下载失败，请尝试其他方式
    pause
    goto python_download_choice
)
goto install_python

:download_curl
echo.
echo [curl] 正在使用 curl 下载 Python 3.12.7...
curl --version >nul 2>&1
if errorlevel 1 (
    echo [错误] curl 不可用，请选择其他下载方式
    pause
    goto python_download_choice
)
echo 下载地址: https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo 保存位置: %cd%\python-installer.exe
echo.
echo 正在下载，请稍候...
curl -L -o python-installer.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
if errorlevel 1 (
    echo [错误] curl 下载失败，请尝试其他方式
    pause
    goto python_download_choice
)
echo [成功] Python 安装包下载完成
goto install_python

:download_bitsadmin
echo.
echo [bitsadmin] 正在使用 bitsadmin 下载 Python 3.12.7...
echo 下载地址: https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo 保存位置: %cd%\python-installer.exe
echo.
echo 正在下载，请稍候...
bitsadmin /transfer "PythonDownload" https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe "%cd%\python-installer.exe"
if errorlevel 1 (
    echo [错误] bitsadmin 下载失败，请尝试其他方式
    pause
    goto python_download_choice
)
echo [成功] Python 安装包下载完成
goto install_python

:download_manual
echo.
echo [手动下载] 请手动下载 Python 安装包：
echo.
echo 方法1 - 访问官网下载：
echo 1. 访问: https://www.python.org/downloads/
echo 2. 下载 Python 3.12.7 Windows x86-64 executable installer
echo 3. 将下载的文件重命名为 python-installer.exe 并放在当前目录
echo.
echo 方法2 - 使用命令行下载（复制以下命令到新的命令提示符窗口）：
echo.
echo PowerShell:
echo powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile 'python-installer.exe'"
echo.
echo curl:
echo curl -o python-installer.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo.
echo bitsadmin:
echo bitsadmin /transfer "PythonDownload" https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe "%cd%\python-installer.exe"
echo.

:manual_wait
set /p manual_continue="下载完成后按 y 继续安装，按 n 重新选择 (y/n): "
if /i "%manual_continue%"=="y" (
    if exist "python-installer.exe" (
        goto install_python
    ) else (
        echo [错误] 未找到 python-installer.exe 文件，请确保文件在当前目录
        goto manual_wait
    )
)
if /i "%manual_continue%"=="n" goto python_download_choice
echo [错误] 请输入 y 或 n
goto manual_wait

:skip_python
echo [跳过] 已跳过 Python 安装
echo 请手动安装 Python 后重新运行此脚本
pause
exit /b 1

:install_python
echo.
echo ========================================
echo  安装 Python
echo ========================================
echo.
echo [检查] 验证下载文件...
if not exist "python-installer.exe" (
    echo [错误] 未找到 python-installer.exe 文件
    pause
    goto python_download_choice
)

echo [检查] 文件大小验证...
for %%A in (python-installer.exe) do set file_size=%%~zA
if %file_size% LSS 10000000 (
    echo [错误] 下载的文件可能不完整 ^(大小: %file_size% 字节^)
    echo 正常的Python安装包应该大于10MB
    echo 请重新下载
    del python-installer.exe >nul 2>&1
    pause
    goto python_download_choice
)
echo [成功] 文件大小正常 ^(%file_size% 字节^)

echo.
echo [安装] 准备安装 Python...
echo.
echo 重要提示：
echo 1. 安装过程中请务必勾选 "Add Python to PATH" 选项
echo 2. 建议选择 "Install for all users" 选项
echo 3. 安装完成后不要立即关闭安装程序
echo.

:install_confirm
set /p install_confirm="按 y 开始安装，按 n 取消 (y/n): "
if /i "%install_confirm%"=="y" goto start_install
if /i "%install_confirm%"=="n" (
    echo [取消] 已取消安装
    pause
    exit /b 1
)
echo [错误] 请输入 y 或 n
goto install_confirm

:start_install
echo [安装] 正在启动 Python 安装程序...
echo 请在安装程序中完成安装过程
start /wait python-installer.exe

echo.
echo [验证] 安装完成，正在验证...
timeout /t 3 /nobreak >nul

REM 尝试刷新环境变量
set PATH=%PATH%

python --version >nul 2>&1
if errorlevel 1 (
    echo [警告] Python 可能未正确安装或未添加到 PATH
    echo.
    echo 可能的原因：
    echo 1. 安装时未勾选 "Add Python to PATH"
    echo 2. 需要重启命令提示符
    echo 3. 可能是加载问题，可关闭此脚本，在cmd中输入python -v查看
    echo 4. 需要重新登录 Windows
  

    :retry_check
    set /p retry_check="按 y 重新检查，按 r 重新安装，按 n 退出 (y/r/n): "
    if /i "%retry_check%"=="y" (
        python --version >nul 2>&1
        if errorlevel 1 (
            echo [错误] Python 仍然不可用
            goto retry_check
        ) else (
            goto python_success
        )
    )
    if /i "%retry_check%"=="r" goto install_python
    if /i "%retry_check%"=="n" (
        pause
        exit /b 1
    )
    echo [错误] 请输入 y、r 或 n
    goto retry_check
)

:python_success
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] Python 安装成功！版本: %PYTHON_VERSION%

echo.
echo [清理] 安装文件处理...

:cleanup_choice
set /p cleanup="是否删除安装文件 python-installer.exe？(y/N): "
if /i "%cleanup%"=="y" (
    del python-installer.exe >nul 2>&1
    echo [清理] 安装文件已删除
) else if /i "%cleanup%"=="n" (
    echo [保留] 安装文件已保留
) else if "%cleanup%"=="" (
    echo [保留] 安装文件已保留
) else (
    echo [错误] 请输入 y 或 n
    goto cleanup_choice
)

echo.
echo [完成] Python 安装向导完成！
echo 正在返回环境检查...
pause
goto check_environment
