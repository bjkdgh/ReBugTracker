@echo off
echo ReBugTracker Startup
echo ===================

python --version 2>NUL
if errorlevel 1 (
    echo Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

if not exist logs mkdir logs
if not exist uploads mkdir uploads

echo Starting ReBugTracker...
echo Access: http://localhost:5000
echo Admin: admin / admin
echo.

python rebugtracker.py

pause
