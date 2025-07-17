@echo off
REM ReBugTracker Windows����ж�ؽű�
REM ʹ��NSSMж��ReBugTracker Windows����

setlocal enabledelayedexpansion

REM �̶�����Ŀ¼���������ԱȨ����·������
cd /d "%~dp0.."

REM ��������
set "SERVICE_NAME=ReBugTracker"
set "PROJECT_DIR=%cd%"
set "NSSM_EXE=%PROJECT_DIR%\deployment_tools\nssm.exe"

echo ReBugTracker Windows����ж�ع���
echo ==========================================
echo.
echo ��ĿĿ¼: %PROJECT_DIR%
echo NSSM·��: %NSSM_EXE%
echo.

REM ���NSSM����
if not exist "%NSSM_EXE%" (
    echo [����] δ�ҵ�NSSM����: %NSSM_EXE%
    echo �������а�װ�ű����ֶ�����NSSM����
    pause
    exit /b 1
)

REM �������Ƿ����
sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [����] ���� %SERVICE_NAME% �����ڻ��ѱ�ж��
    pause
    exit /b 0
)

echo [����] ����ж�� ReBugTracker Windows����
echo.
echo ������Ϣ:
sc query "%SERVICE_NAME%" | findstr "SERVICE_NAME DISPLAY_NAME STATE"
echo.

set /p confirm="ȷ��Ҫж�ط�����? (y/n): "
if /i "%confirm%" neq "y" (
    echo ж����ȡ��
    pause
    exit /b 0
)

echo.
echo [��Ϣ] ֹͣ����...
net stop "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [����] ��������Ѿ�ֹͣ
) else (
    echo [�ɹ�] ������ֹͣ
)

echo.
echo [��Ϣ] ж�ط���...
"%NSSM_EXE%" remove "%SERVICE_NAME%" confirm
if errorlevel 1 (
    echo [����] ����ж��ʧ��
    pause
    exit /b 1
)

echo [�ɹ�] ����ж�سɹ�
echo.

echo ������Ϣ:
echo ==========================================
echo �����Ѵ�ϵͳ���Ƴ�
echo ��Ŀ�ļ������ݱ��ֲ���
echo ������ȫ�������ֶ�ɾ����������:
echo   - ��ĿĿ¼: %PROJECT_DIR%
echo   - ��־�ļ�: %PROJECT_DIR%\logs\
echo   - �����ļ�: %PROJECT_DIR%\.env
echo.

echo [�ɹ�] ReBugTracker Windows����ж����ɣ�
pause
