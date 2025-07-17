@echo off
REM ReBugTracker Windows������������ű�

setlocal enabledelayedexpansion

set "SERVICE_NAME=ReBugTracker"

echo ReBugTracker Windows�����������
echo ========================================
echo.

REM �������Ƿ����
sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [����] ���� %SERVICE_NAME% δ��װ
    echo.
    echo ���Ȱ�װWindows����:
    echo   deployment_tools\install_windows_service.bat
    echo.
    pause
    exit /b 1
)

REM ������״̬
for /f "tokens=4" %%i in ('sc query "%SERVICE_NAME%" ^| findstr "STATE"') do set SERVICE_STATE=%%i

if "%SERVICE_STATE%"=="RUNNING" (
    echo [�ɹ�] ��������������
    echo ���ʵ�ַ: http://localhost:8000
) else (
    echo [��Ϣ] ��������...
    net start "%SERVICE_NAME%"
    if errorlevel 1 (
        echo [����] ��������ʧ��
        echo ������־��ʹ�ù�����: deployment_tools\manage_windows_service.bat
    ) else (
        echo [�ɹ�] ���������ɹ�
        echo ���ʵ�ַ: http://localhost:8000
    )
)

echo.
echo �������:
echo   ������: deployment_tools\manage_windows_service.bat
echo   ֹͣ����: net stop %SERVICE_NAME%
echo   �鿴״̬: sc query %SERVICE_NAME%
echo.

set /p open_web="�Ƿ��Web����? (y/n): "
if /i "%open_web%"=="y" (
    start http://localhost:8000
)

pause