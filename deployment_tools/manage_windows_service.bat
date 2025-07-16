@echo off
REM ReBugTracker Windows服务管理脚本
REM 提供启动、停止、重启、状态查看等功能

setlocal enabledelayedexpansion

REM 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "CYAN=[96m"
set "NC=[0m"

REM 服务配置
set "SERVICE_NAME=ReBugTracker"
set "PROJECT_DIR=%~dp0.."

:main_menu
cls
echo %BLUE%🔧 ReBugTracker Windows服务管理工具%NC%
echo ==========================================
echo.

REM 检查服务是否存在
sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ 服务 %SERVICE_NAME% 未安装%NC%
    echo.
    echo 请先运行安装脚本: deployment_tools\install_windows_service.bat
    pause
    exit /b 1
)

REM 获取服务状态
for /f "tokens=4" %%i in ('sc query "%SERVICE_NAME%" ^| findstr "STATE"') do set SERVICE_STATE=%%i

echo %BLUE%📋 当前服务状态:%NC%
if "%SERVICE_STATE%"=="RUNNING" (
    echo %GREEN%🟢 运行中%NC%
) else if "%SERVICE_STATE%"=="STOPPED" (
    echo %RED%🔴 已停止%NC%
) else if "%SERVICE_STATE%"=="PENDING" (
    echo %YELLOW%🟡 状态变更中%NC%
) else (
    echo %YELLOW%🟡 %SERVICE_STATE%%NC%
)

echo.
echo %CYAN%请选择操作:%NC%
echo.
echo 1. 启动服务
echo 2. 停止服务  
echo 3. 重启服务
echo 4. 查看详细状态
echo 5. 查看服务日志
echo 6. 打开Web界面
echo 7. 服务配置管理
echo 8. 卸载服务
echo 9. 退出
echo.

set /p choice="请输入选择 (1-9): "

if "%choice%"=="1" goto start_service
if "%choice%"=="2" goto stop_service
if "%choice%"=="3" goto restart_service
if "%choice%"=="4" goto show_status
if "%choice%"=="5" goto show_logs
if "%choice%"=="6" goto open_web
if "%choice%"=="7" goto service_config
if "%choice%"=="8" goto uninstall_service
if "%choice%"=="9" goto exit_script

echo %RED%❌ 无效选择，请重新输入%NC%
timeout /t 2 /nobreak >nul
goto main_menu

:start_service
echo.
echo %BLUE%🚀 启动服务...%NC%
net start "%SERVICE_NAME%"
if errorlevel 1 (
    echo %RED%❌ 服务启动失败%NC%
    echo 请检查日志文件获取详细信息
) else (
    echo %GREEN%✅ 服务启动成功%NC%
    echo 访问地址: http://localhost:8000
)
pause
goto main_menu

:stop_service
echo.
echo %BLUE%⏹️ 停止服务...%NC%
net stop "%SERVICE_NAME%"
if errorlevel 1 (
    echo %RED%❌ 服务停止失败%NC%
) else (
    echo %GREEN%✅ 服务已停止%NC%
)
pause
goto main_menu

:restart_service
echo.
echo %BLUE%🔄 重启服务...%NC%
echo 正在停止服务...
net stop "%SERVICE_NAME%" >nul 2>&1
timeout /t 3 /nobreak >nul
echo 正在启动服务...
net start "%SERVICE_NAME%"
if errorlevel 1 (
    echo %RED%❌ 服务重启失败%NC%
) else (
    echo %GREEN%✅ 服务重启成功%NC%
    echo 访问地址: http://localhost:8000
)
pause
goto main_menu

:show_status
echo.
echo %BLUE%📊 详细服务状态:%NC%
echo ==========================================
sc query "%SERVICE_NAME%"
echo.
sc qc "%SERVICE_NAME%"
pause
goto main_menu

:show_logs
echo.
echo %BLUE%📝 服务日志:%NC%
echo ==========================================
echo.
echo 1. 查看标准输出日志
echo 2. 查看错误日志
echo 3. 查看应用日志
echo 4. 返回主菜单
echo.
set /p log_choice="请选择 (1-4): "

if "%log_choice%"=="1" (
    if exist "%PROJECT_DIR%\logs\service_stdout.log" (
        echo.
        echo %BLUE%📄 标准输出日志 (最后20行):%NC%
        powershell -Command "Get-Content '%PROJECT_DIR%\logs\service_stdout.log' -Tail 20"
    ) else (
        echo %YELLOW%⚠️ 标准输出日志文件不存在%NC%
    )
) else if "%log_choice%"=="2" (
    if exist "%PROJECT_DIR%\logs\service_stderr.log" (
        echo.
        echo %BLUE%📄 错误日志 (最后20行):%NC%
        powershell -Command "Get-Content '%PROJECT_DIR%\logs\service_stderr.log' -Tail 20"
    ) else (
        echo %YELLOW%⚠️ 错误日志文件不存在%NC%
    )
) else if "%log_choice%"=="3" (
    if exist "%PROJECT_DIR%\logs\rebugtracker.log" (
        echo.
        echo %BLUE%📄 应用日志 (最后20行):%NC%
        powershell -Command "Get-Content '%PROJECT_DIR%\logs\rebugtracker.log' -Tail 20"
    ) else (
        echo %YELLOW%⚠️ 应用日志文件不存在%NC%
    )
) else if "%log_choice%"=="4" (
    goto main_menu
) else (
    echo %RED%❌ 无效选择%NC%
)
pause
goto main_menu

:open_web
echo.
echo %BLUE%🌐 打开Web界面...%NC%
start http://localhost:8000
echo %GREEN%✅ 已在默认浏览器中打开 ReBugTracker%NC%
pause
goto main_menu

:service_config
echo.
echo %BLUE%⚙️ 服务配置管理:%NC%
echo ==========================================
echo.
echo 1. 查看服务配置
echo 2. 设置自动启动
echo 3. 设置手动启动
echo 4. 返回主菜单
echo.
set /p config_choice="请选择 (1-4): "

if "%config_choice%"=="1" (
    echo.
    sc qc "%SERVICE_NAME%"
) else if "%config_choice%"=="2" (
    echo.
    echo %BLUE%设置服务为自动启动...%NC%
    sc config "%SERVICE_NAME%" start= auto
    echo %GREEN%✅ 服务已设置为自动启动%NC%
) else if "%config_choice%"=="3" (
    echo.
    echo %BLUE%设置服务为手动启动...%NC%
    sc config "%SERVICE_NAME%" start= demand
    echo %GREEN%✅ 服务已设置为手动启动%NC%
) else if "%config_choice%"=="4" (
    goto main_menu
) else (
    echo %RED%❌ 无效选择%NC%
)
pause
goto main_menu

:uninstall_service
echo.
echo %YELLOW%⚠️ 确定要卸载 ReBugTracker Windows服务吗?%NC%
set /p confirm="输入 'yes' 确认卸载: "
if /i "%confirm%"=="yes" (
    echo.
    echo %BLUE%🗑️ 正在卸载服务...%NC%
    call "%PROJECT_DIR%\deployment_tools\uninstall_windows_service.bat"
    exit /b 0
) else (
    echo 卸载已取消
    pause
    goto main_menu
)

:exit_script
echo.
echo %GREEN%👋 感谢使用 ReBugTracker 服务管理工具！%NC%
exit /b 0
