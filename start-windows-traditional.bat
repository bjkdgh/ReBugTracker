@echo off
REM ReBugTracker Windows Traditional Deployment Startup Script
REM For deployment method described in DEPLOYMENT_GUIDE_WINDOWS_POSTGRES.md

echo ReBugTracker Windows Traditional Deployment Startup Script
echo ============================================================

REM Check if Python is installed
python --version 2>NUL
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check PostgreSQL connection
echo Checking PostgreSQL connection...
python -c "import psycopg2; print('PostgreSQL connection library installed')" 2>NUL
if errorlevel 1 (
    echo ERROR: psycopg2 not installed. Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking Python dependencies...
python -c "import flask, waitress; print('Dependencies check passed')" 2>NUL
if errorlevel 1 (
    echo WARNING: Missing required dependencies, installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check configuration file
if not exist config.py (
    echo ERROR: config.py file does not exist
    pause
    exit /b 1
)

REM Test database connection
echo Testing database connection...
python database_tools/test_db_connection.py 2>NUL
if errorlevel 1 (
    echo ERROR: Database connection failed. Please check database configuration in config.py
    echo Please ensure:
    echo   1. PostgreSQL service is running
    echo   2. Database user and password are correct
    echo   3. Database has been created
    pause
    exit /b 1
)

echo SUCCESS: Database connection established

REM Create necessary directories
if not exist logs mkdir logs
if not exist uploads mkdir uploads

REM Startup options
echo.
echo Choose startup mode:
echo   1. Development mode (Flask dev server)
echo   2. Production mode (Waitress)
echo   3. Production mode (Optimized script)
echo.
set /p choice="Please select (1-3): "

if "%choice%"=="1" (
    echo Starting development mode...
    echo Access URL: http://localhost:5000
    echo Default admin account: admin / admin
    echo.
    echo Press Ctrl+C to stop service
    python rebugtracker.py
) else if "%choice%"=="2" (
    echo Starting production mode (Waitress)...
    echo Access URL: http://localhost:5000
    echo Default admin account: admin / admin
    echo.
    echo Press Ctrl+C to stop service
    python run_waitress.py
) else if "%choice%"=="3" (
    echo Starting production mode (Optimized script)...
    echo Access URL: http://localhost:5000
    echo Default admin account: admin / admin
    echo.
    echo Press Ctrl+C to stop service
    python deployment_tools/run_waitress.py
) else (
    echo ERROR: Invalid selection
    pause
    exit /b 1
)

echo.
echo Service management commands:
echo   Start Nginx: cd C:\nginx && start nginx
echo   Stop Nginx: cd C:\nginx && nginx -s stop
echo   Reload Nginx: cd C:\nginx && nginx -s reload
echo.
echo Windows Service management (if configured):
echo   Start service: net start ReBugTracker
echo   Stop service: net stop ReBugTracker
echo   Check status: sc query ReBugTracker
echo.
pause
