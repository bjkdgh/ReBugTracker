@echo off
REM ReBugTracker Windows Simple Startup Script

echo ReBugTracker Windows Startup Script
echo ====================================

REM Check Python
python --version 2>NUL
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check dependencies
echo Checking dependencies...
python -c "import flask" 2>NUL
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Create directories
if not exist logs mkdir logs
if not exist uploads mkdir uploads

REM Test database connection
echo Testing database connection...
python database_tools/test_db_connection.py
if errorlevel 1 (
    echo ERROR: Database connection failed
    echo Please check your database configuration in config.py
    pause
    exit /b 1
)

echo Database connection successful!
echo.

REM Start application
echo Starting ReBugTracker...
echo Access URL: http://localhost:5000
echo Default admin: admin / admin
echo.
echo Press Ctrl+C to stop
echo.

REM Choose startup mode
echo Select startup mode:
echo 1 = Development mode
echo 2 = Production mode (Waitress)
echo 3 = Production mode (Optimized)
echo.
set /p mode="Enter choice (1-3): "

if "%mode%"=="1" (
    python rebugtracker.py
) else if "%mode%"=="2" (
    python run_waitress.py
) else if "%mode%"=="3" (
    python deployment_tools/run_waitress.py
) else (
    echo Invalid choice, starting development mode...
    python rebugtracker.py
)

echo.
echo Application stopped.
pause
