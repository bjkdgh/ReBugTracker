@echo off
REM ReBugTracker Windows服务卸载脚本
REM 使用NSSM卸载ReBugTracker Windows服务

setlocal enabledelayedexpansion

REM 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM 服务配置
set "SERVICE_NAME=ReBugTracker"
set "PROJECT_DIR=%~dp0.."
set "NSSM_DIR=%PROJECT_DIR%\deployment_tools\nssm"

echo %BLUE%🗑️ ReBugTracker Windows服务卸载工具%NC%
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ 需要管理员权限才能卸载Windows服务%NC%
    echo 请以管理员身份运行此脚本
    pause
    exit /b 1
)

REM 检查NSSM工具
if not exist "%NSSM_DIR%\win64\nssm.exe" (
    echo %RED%❌ 未找到NSSM工具: %NSSM_DIR%\win64\nssm.exe%NC%
    echo 请先运行安装脚本或手动解压NSSM工具
    pause
    exit /b 1
)

REM 检查服务是否存在
sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠️ 服务 %SERVICE_NAME% 不存在或已被卸载%NC%
    pause
    exit /b 0
)

REM 显示当前服务状态
echo %BLUE%📋 当前服务状态:%NC%
sc query "%SERVICE_NAME%" | findstr "STATE"
echo.

REM 确认卸载
set /p confirm="确定要卸载 ReBugTracker Windows服务吗? (y/n): "
if /i "%confirm%" neq "y" (
    echo 卸载已取消
    pause
    exit /b 0
)

echo.
echo %BLUE%🛑 正在卸载服务...%NC%

REM 停止服务
echo %BLUE%⏹️ 停止服务...%NC%
net stop "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠️ 服务可能已经停止或停止失败%NC%
) else (
    echo %GREEN%✅ 服务已停止%NC%
)

REM 等待服务完全停止
timeout /t 3 /nobreak >nul

REM 卸载服务
echo %BLUE%🗑️ 卸载服务...%NC%
"%NSSM_DIR%\win64\nssm.exe" remove "%SERVICE_NAME%" confirm
if errorlevel 1 (
    echo %RED%❌ 服务卸载失败%NC%
    echo.
    echo 可能的原因：
    echo 1. 服务正在运行，请先手动停止
    echo 2. 权限不足
    echo 3. 服务被其他程序占用
    echo.
    echo 手动卸载方法：
    echo 1. 打开服务管理器 (services.msc)
    echo 2. 找到 %SERVICE_NAME% 服务
    echo 3. 右键选择停止，然后删除
    echo.
    pause
    exit /b 1
)

echo %GREEN%✅ 服务卸载成功%NC%
echo.

REM 验证卸载
sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %GREEN%✅ 验证：服务已完全卸载%NC%
) else (
    echo %YELLOW%⚠️ 警告：服务可能仍然存在，请手动检查%NC%
)

echo.
echo %BLUE%📋 卸载完成信息:%NC%
echo ==========================================
echo 服务名称: %SERVICE_NAME%
echo 卸载状态: 已完成
echo.
echo %BLUE%📝 注意事项:%NC%
echo 1. 服务日志文件仍保留在 logs\ 目录中
echo 2. 应用程序文件和配置未被删除
echo 3. 如需完全清理，请手动删除相关文件
echo.
echo %BLUE%🔄 重新安装服务:%NC%
echo 如需重新安装服务，请运行:
echo   deployment_tools\install_windows_service.bat
echo.

echo %GREEN%🎉 ReBugTracker Windows服务卸载完成！%NC%
pause
