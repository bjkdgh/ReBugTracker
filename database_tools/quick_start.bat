@echo off
echo ReBugTracker ���ݿ⹤�߼� - ��������
echo ============================================================

cd /d "%~dp0\.."

echo ����ѡ��:
echo 1. ����ʽ����ѡ���� (�Ƽ�)
echo 2. ���ݿ�״̬���
echo 3. ����ͬ�� (PostgreSQL �� SQLite)
echo 4. ��ṹ�Աȼ��
echo 0. �˳�

set /p choice="��ѡ����� (0-4): "

if "%choice%"=="1" (
    echo.
    echo ��������ʽ����ѡ����...
    .venv\Scripts\python.exe database_tools\tool_index.py
) else if "%choice%"=="2" (
    echo.
    echo ������ݿ�״̬...
    .venv\Scripts\python.exe database_tools\check_tools\sync_status_checker.py
) else if "%choice%"=="3" (
    echo.
    echo ִ������ͬ��...
    .venv\Scripts\python.exe database_tools\sync_tools\smart_sync_postgres_to_sqlite.py
) else if "%choice%"=="4" (
    echo.
    echo ����ṹ�Ա�...
    .venv\Scripts\python.exe database_tools\check_tools\table_structure_checker.py
) else if "%choice%"=="0" (
    echo.
    echo �ټ�!
    exit /b 0
) else (
    echo.
    echo ��Чѡ��
)

echo.
echo ============================================================
pause