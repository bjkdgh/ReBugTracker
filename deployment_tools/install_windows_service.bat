@echo off
REM ReBugTracker Windows����װ�ű�
REM ʹ��NSSM��ReBugTracker��װΪWindows����

setlocal enabledelayedexpansion

REM �̶�����Ŀ¼���������ԱȨ����·������
cd /d "%~dp0.."

REM ��������
set "SERVICE_NAME=ReBugTracker"
set "SERVICE_DISPLAY_NAME=ReBugTracker Bug Tracking System"
set "SERVICE_DESCRIPTION=��ҵ��ȱ�ݸ���ϵͳ"
set "PROJECT_DIR=%cd%"
set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
set "APP_SCRIPT=%PROJECT_DIR%\deployment_tools\run_waitress.py"
set "NSSM_EXE=%PROJECT_DIR%\deployment_tools\nssm.exe"

echo ReBugTracker Windows����װ����
echo ==========================================
echo.
echo ��ĿĿ¼: %PROJECT_DIR%
echo NSSM·��: %NSSM_EXE%
echo.

REM ���NSSM����
if not exist "%NSSM_EXE%" (
    echo [����] δ�ҵ�NSSM����: %NSSM_EXE%
    echo �������ز�����NSSM���ߵ�deployment_toolsĿ¼
    pause
    exit /b 1
)

REM ���Python���⻷��
if not exist "%PYTHON_EXE%" (
    echo [����] δ�ҵ�Python���⻷��: %PYTHON_EXE%
    echo ���ȴ������⻷��
    pause
    exit /b 1
)

REM ���Ӧ�ýű�
if not exist "%APP_SCRIPT%" (
    echo [����] δ�ҵ�Ӧ�ýű�: %APP_SCRIPT%
    pause
    exit /b 1
)

REM �������Ƿ��Ѵ���
sc query "%SERVICE_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo [����] ���� %SERVICE_NAME% �Ѵ���
    set /p overwrite="�Ƿ�Ҫ���°�װ? (y/n): "
    if /i "!overwrite!" neq "y" (
        echo ��װ��ȡ��
        pause
        exit /b 0
    )
    
    echo [��Ϣ] ֹͣ��ɾ�����з���...
    net stop "%SERVICE_NAME%" >nul 2>&1
    "%NSSM_EXE%" remove "%SERVICE_NAME%" confirm >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo [��Ϣ] ��װReBugTracker Windows����...
echo.

REM ��װ����
"%NSSM_EXE%" install "%SERVICE_NAME%" "%PYTHON_EXE%" "%APP_SCRIPT%"
if errorlevel 1 (
    echo [����] ����װʧ��
    pause
    exit /b 1
)

REM ���÷���
echo [��Ϣ] ���÷������...

REM ���÷�����ʾ���ƺ�����
"%NSSM_EXE%" set "%SERVICE_NAME%" DisplayName "%SERVICE_DISPLAY_NAME%"
"%NSSM_EXE%" set "%SERVICE_NAME%" Description "%SERVICE_DESCRIPTION%"

REM ���ù���Ŀ¼
"%NSSM_EXE%" set "%SERVICE_NAME%" AppDirectory "%PROJECT_DIR%"

REM ������������Ϊ�Զ�
"%NSSM_EXE%" set "%SERVICE_NAME%" Start SERVICE_AUTO_START

REM ������־�ļ�
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"
"%NSSM_EXE%" set "%SERVICE_NAME%" AppStdout "%PROJECT_DIR%\logs\service_stdout.log"
"%NSSM_EXE%" set "%SERVICE_NAME%" AppStderr "%PROJECT_DIR%\logs\service_stderr.log"

REM ������־��ת
"%NSSM_EXE%" set "%SERVICE_NAME%" AppStdoutCreationDisposition 4
"%NSSM_EXE%" set "%SERVICE_NAME%" AppStderrCreationDisposition 4

REM ���÷������������ʹ��PostgreSQL��
if exist "%PROJECT_DIR%\.env" (
    findstr /i "DB_TYPE=postgres" "%PROJECT_DIR%\.env" >nul 2>&1
    if not errorlevel 1 (
        echo [��Ϣ] ��⵽PostgreSQL���ݿ⣬���÷�������...
        "%NSSM_EXE%" set "%SERVICE_NAME%" DependOnService postgresql-x64-17
    )
)

REM ���÷���ָ�ѡ��
"%NSSM_EXE%" set "%SERVICE_NAME%" AppThrottle 1500
"%NSSM_EXE%" set "%SERVICE_NAME%" AppExit Default Restart
"%NSSM_EXE%" set "%SERVICE_NAME%" AppRestartDelay 0

echo [�ɹ�] ����װ���
echo.

REM ��������
echo [��Ϣ] ��������...
net start "%SERVICE_NAME%"
if errorlevel 1 (
    echo [����] ��������ʧ��
    echo ������־�ļ�: %PROJECT_DIR%\logs\service_stderr.log
    pause
    exit /b 1
)

echo [�ɹ�] ���������ɹ�
echo.

REM ��ʾ������Ϣ
echo ������Ϣ:
echo ==========================================
echo ��������: %SERVICE_NAME%
echo ��ʾ����: %SERVICE_DISPLAY_NAME%
echo ����״̬: 
sc query "%SERVICE_NAME%" | findstr "STATE"
echo.
echo ���ʵ�ַ: http://localhost:8000
echo ����Ա�˺�: admin
echo ����Ա����: admin
echo.
echo ��־�ļ�:
echo   ��׼���: %PROJECT_DIR%\logs\service_stdout.log
echo   �������: %PROJECT_DIR%\logs\service_stderr.log
echo.

echo �����������:
echo   ��������: net start %SERVICE_NAME%
echo   ֹͣ����: net stop %SERVICE_NAME%
echo   ��������: net stop %SERVICE_NAME% ^&^& net start %SERVICE_NAME%
echo   �鿴״̬: sc query %SERVICE_NAME%
echo   ж�ط���: deployment_tools\uninstall_windows_service.bat
echo.

echo [�ɹ�] ReBugTracker Windows����װ��ɣ�
pause
