@echo off
REM ReBugTracker Windows服务安装脚本
REM 使用NSSM将ReBugTracker安装为Windows服务

setlocal enabledelayedexpansion

REM 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM 服务配置
set "SERVICE_NAME=ReBugTracker"
set "SERVICE_DISPLAY_NAME=ReBugTracker Bug Tracking System"
set "SERVICE_DESCRIPTION=企业级缺陷跟踪系统"
set "PROJECT_DIR=%~dp0.."
set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
set "APP_SCRIPT=%PROJECT_DIR%\deployment_tools\run_waitress.py"
set "NSSM_DIR=%PROJECT_DIR%\deployment_tools\nssm"

echo %BLUE%🔧 ReBugTracker Windows服务安装工具%NC%
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ 需要管理员权限才能安装Windows服务%NC%
    echo 请以管理员身份运行此脚本
    pause
    exit /b 1
)

REM 解压NSSM工具
if not exist "%NSSM_DIR%" (
    echo %BLUE%📦 解压NSSM工具...%NC%
    if exist "%PROJECT_DIR%\deployment_tools\nssm-2.24.zip" (
        powershell -Command "Expand-Archive -Path '%PROJECT_DIR%\deployment_tools\nssm-2.24.zip' -DestinationPath '%PROJECT_DIR%\deployment_tools\' -Force"
        if exist "%PROJECT_DIR%\deployment_tools\nssm-2.24" (
            move "%PROJECT_DIR%\deployment_tools\nssm-2.24" "%NSSM_DIR%"
        )
        echo %GREEN%✅ NSSM工具解压完成%NC%
    ) else (
        echo %RED%❌ 未找到NSSM安装包: nssm-2.24.zip%NC%
        pause
        exit /b 1
    )
)

REM 检查Python虚拟环境
if not exist "%PYTHON_EXE%" (
    echo %RED%❌ 未找到Python虚拟环境: %PYTHON_EXE%%NC%
    echo 请先运行部署脚本创建虚拟环境
    pause
    exit /b 1
)

REM 检查应用脚本
if not exist "%APP_SCRIPT%" (
    echo %RED%❌ 未找到应用脚本: %APP_SCRIPT%%NC%
    pause
    exit /b 1
)

REM 检查服务是否已存在
sc query "%SERVICE_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo %YELLOW%⚠️ 服务 %SERVICE_NAME% 已存在%NC%
    set /p overwrite="是否要重新安装? (y/n): "
    if /i "!overwrite!" neq "y" (
        echo 安装已取消
        pause
        exit /b 0
    )
    
    echo %BLUE%🛑 停止并删除现有服务...%NC%
    net stop "%SERVICE_NAME%" >nul 2>&1
    "%NSSM_DIR%\win64\nssm.exe" remove "%SERVICE_NAME%" confirm >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo %BLUE%🚀 安装ReBugTracker Windows服务...%NC%
echo.

REM 安装服务
"%NSSM_DIR%\win64\nssm.exe" install "%SERVICE_NAME%" "%PYTHON_EXE%" "%APP_SCRIPT%"
if errorlevel 1 (
    echo %RED%❌ 服务安装失败%NC%
    pause
    exit /b 1
)

REM 配置服务
echo %BLUE%⚙️ 配置服务参数...%NC%

REM 设置服务显示名称和描述
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" DisplayName "%SERVICE_DISPLAY_NAME%"
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" Description "%SERVICE_DESCRIPTION%"

REM 设置工作目录
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppDirectory "%PROJECT_DIR%"

REM 设置启动类型为自动
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" Start SERVICE_AUTO_START

REM 设置日志文件
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppStdout "%PROJECT_DIR%\logs\service_stdout.log"
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppStderr "%PROJECT_DIR%\logs\service_stderr.log"

REM 设置日志轮转
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppStdoutCreationDisposition 4
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppStderrCreationDisposition 4

REM 设置服务依赖（如果使用PostgreSQL）
if exist "%PROJECT_DIR%\.env" (
    findstr /i "DB_TYPE=postgres" "%PROJECT_DIR%\.env" >nul 2>&1
    if not errorlevel 1 (
        echo %BLUE%🗄️ 检测到PostgreSQL数据库，设置服务依赖...%NC%
        "%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" DependOnService postgresql-x64-17
    )
)

REM 设置服务恢复选项
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppThrottle 1500
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppExit Default Restart
"%NSSM_DIR%\win64\nssm.exe" set "%SERVICE_NAME%" AppRestartDelay 0

echo %GREEN%✅ 服务安装完成%NC%
echo.

REM 启动服务
echo %BLUE%🚀 启动服务...%NC%
net start "%SERVICE_NAME%"
if errorlevel 1 (
    echo %RED%❌ 服务启动失败%NC%
    echo 请检查日志文件: %PROJECT_DIR%\logs\service_stderr.log
    pause
    exit /b 1
)

echo %GREEN%✅ 服务启动成功%NC%
echo.

REM 显示服务信息
echo %BLUE%📋 服务信息:%NC%
echo ==========================================
echo 服务名称: %SERVICE_NAME%
echo 显示名称: %SERVICE_DISPLAY_NAME%
echo 服务状态: 
sc query "%SERVICE_NAME%" | findstr "STATE"
echo.
echo 访问地址: http://localhost:8000
echo 管理员账号: admin
echo 管理员密码: admin
echo.
echo 日志文件:
echo   标准输出: %PROJECT_DIR%\logs\service_stdout.log
echo   错误输出: %PROJECT_DIR%\logs\service_stderr.log
echo.

echo %BLUE%🔧 服务管理命令:%NC%
echo   启动服务: net start %SERVICE_NAME%
echo   停止服务: net stop %SERVICE_NAME%
echo   重启服务: net stop %SERVICE_NAME% ^&^& net start %SERVICE_NAME%
echo   查看状态: sc query %SERVICE_NAME%
echo   卸载服务: deployment_tools\uninstall_windows_service.bat
echo.

echo %GREEN%🎉 ReBugTracker Windows服务安装完成！%NC%
pause
