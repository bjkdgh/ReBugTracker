@echo off
echo ReBugTracker 数据库工具集 - 快速启动
echo ============================================================

cd /d "%~dp0\.."

echo 功能选择:
echo 1. 交互式工具选择器 (推荐)
echo 2. 数据库状态检查
echo 3. 智能同步 (PostgreSQL 到 SQLite)
echo 4. 表结构对比检查
echo 0. 退出

set /p choice="请选择操作 (0-4): "

if "%choice%"=="1" (
    echo.
    echo 启动交互式工具选择器...
    .venv\Scripts\python.exe database_tools\tool_index.py
) else if "%choice%"=="2" (
    echo.
    echo 检查数据库状态...
    .venv\Scripts\python.exe database_tools\check_tools\sync_status_checker.py
) else if "%choice%"=="3" (
    echo.
    echo 执行智能同步...
    .venv\Scripts\python.exe database_tools\sync_tools\smart_sync_postgres_to_sqlite.py
) else if "%choice%"=="4" (
    echo.
    echo 检查表结构对比...
    .venv\Scripts\python.exe database_tools\check_tools\table_structure_checker.py
) else if "%choice%"=="0" (
    echo.
    echo 再见!
    exit /b 0
) else (
    echo.
    echo 无效选择
)

echo.
echo ============================================================
pause