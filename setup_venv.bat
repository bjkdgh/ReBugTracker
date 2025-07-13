@echo off
REM ReBugTracker 虚拟环境设置脚本 (Windows)

echo ReBugTracker 虚拟环境设置
echo ============================

REM 检查Python是否安装
python --version >NUL 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

echo Python version:
python --version

REM 检查是否已存在虚拟环境
if exist ".venv" (
    echo Virtual environment already exists.
    set /p recreate="Do you want to recreate it? (y/N): "
    if /i "%recreate%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q .venv
    ) else (
        echo Using existing virtual environment.
        goto :activate
    )
)

REM 创建虚拟环境
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:activate
REM 激活虚拟环境
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM 升级pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM 安装依赖
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ================================
echo Virtual environment setup complete!
echo.
echo To activate the virtual environment:
echo   .venv\Scripts\activate.bat
echo.
echo To deactivate:
echo   deactivate
echo.
echo To start ReBugTracker:
echo   python rebugtracker.py
echo.
pause
