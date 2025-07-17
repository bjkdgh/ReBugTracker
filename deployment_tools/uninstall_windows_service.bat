@echo off
REM ReBugTracker Windows服务卸载脚本
REM 使用NSSM卸载ReBugTracker Windows服务

setlocal enabledelayedexpansion

REM 固定工作目录，解决管理员权限下路径问题
cd /d "%~dp0.."

REM 服务配置
set "SERVICE_NAME=ReBugTracker"
set "PROJECT_DIR=%cd%"
set "NSSM_EXE=%PROJECT_DIR%\deployment_tools\nssm.exe"

echo ReBugTracker Windows服务卸载工具
echo ==========================================
echo.
echo 项目目录: %PROJECT_DIR%
echo NSSM路径: %NSSM_EXE%
echo.

REM 检查NSSM工具
if not exist "%NSSM_EXE%" (
    echo [错误] 未找到NSSM工具: %NSSM_EXE%
    echo 请先运行安装脚本或手动放置NSSM工具
    pause
    exit /b 1
)

REM 检查服务是否存在
sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [警告] 服务 %SERVICE_NAME% 不存在或已被卸载
    pause
    exit /b 0
)

echo [警告] 即将卸载 ReBugTracker Windows服务
echo.
echo 服务信息:
sc query "%SERVICE_NAME%" | findstr "SERVICE_NAME DISPLAY_NAME STATE"
echo.

set /p confirm="确定要卸载服务吗? (y/n): "
if /i "%confirm%" neq "y" (
    echo 卸载已取消
    pause
    exit /b 0
)

echo.
echo [信息] 停止服务...
net stop "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [警告] 服务可能已经停止
) else (
    echo [成功] 服务已停止
)

echo.
echo [信息] 卸载服务...
"%NSSM_EXE%" remove "%SERVICE_NAME%" confirm
if errorlevel 1 (
    echo [错误] 服务卸载失败
    pause
    exit /b 1
)

echo [成功] 服务卸载成功
echo.

echo 清理信息:
echo ==========================================
echo 服务已从系统中移除
echo 项目文件和数据保持不变
echo 如需完全清理，请手动删除以下内容:
echo   - 项目目录: %PROJECT_DIR%
echo   - 日志文件: %PROJECT_DIR%\logs\
echo   - 配置文件: %PROJECT_DIR%\.env
echo.

echo [成功] ReBugTracker Windows服务卸载完成！
pause
