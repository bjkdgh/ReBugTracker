@echo off
REM ReBugTracker Windows服务快速启动脚本

setlocal enabledelayedexpansion

REM 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

set "SERVICE_NAME=ReBugTracker"

echo %BLUE%🚀 ReBugTracker Windows服务快速启动%NC%
echo ========================================
echo.

REM 检查服务是否存在
sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ 服务 %SERVICE_NAME% 未安装%NC%
    echo.
    echo 请先安装Windows服务:
    echo   deployment_tools\install_windows_service.bat
    echo.
    pause
    exit /b 1
)

REM 检查服务状态
for /f "tokens=4" %%i in ('sc query "%SERVICE_NAME%" ^| findstr "STATE"') do set SERVICE_STATE=%%i

if "%SERVICE_STATE%"=="RUNNING" (
    echo %GREEN%✅ 服务已在运行中%NC%
    echo 访问地址: http://localhost:8000
) else (
    echo %BLUE%🚀 启动服务...%NC%
    net start "%SERVICE_NAME%"
    if errorlevel 1 (
        echo %RED%❌ 服务启动失败%NC%
        echo 请检查日志或使用管理工具: deployment_tools\manage_windows_service.bat
    ) else (
        echo %GREEN%✅ 服务启动成功%NC%
        echo 访问地址: http://localhost:8000
    )
)

echo.
echo %BLUE%🔧 服务管理:%NC%
echo   管理工具: deployment_tools\manage_windows_service.bat
echo   停止服务: net stop %SERVICE_NAME%
echo   查看状态: sc query %SERVICE_NAME%
echo.

set /p open_web="是否打开Web界面? (y/n): "
if /i "%open_web%"=="y" (
    start http://localhost:8000
)

pause
