@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

REM �̶�����Ŀ¼Ϊ�ű�����Ŀ¼���������ԱȨ����·������
cd /d "%~dp0"
cd /d "%~dp0\..\.."
set "PROJECT_ROOT=%cd%"

:welcome
cls
echo ========================================
echo  ReBugTracker Windows һ������ű�
echo ========================================
echo.
echo ��Ŀ��Ŀ¼: %PROJECT_ROOT%
echo.
echo ���ű������������ ReBugTracker �� Windows ϵͳ����������
echo ֧�����²���ʽ��
echo - Docker ��������
echo - ���ؿ�����������
echo - VBS ��̨���������������Ƽ���
echo.
echo ��ɫ���ܣ�
echo - VBS �ű��޴��ں�̨����
echo - �����ÿ����Զ�����
echo - ������⹤�ߣ�Windows ԭ��֧��
echo.
echo ���������ʼ����...
pause >nul

:check_environment
cls
echo ========================================
echo  �������
echo ========================================
echo.
echo ���ڼ��ϵͳ����...

python --version >nul 2>&1
if errorlevel 1 (
    echo [����] δ�ҵ� Python����Ҫ�Ȱ�װ Python 3.8+
    echo.
    echo �������ص�ַ: https://www.python.org/downloads/
    echo.
    echo �Ƿ�ʹ�� Windows Ĭ�Ϲ����Զ����� Python��
    echo.
    goto python_download_choice
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [�ɹ�] Python �汾: !PYTHON_VERSION!
)

pip --version >nul 2>&1
if errorlevel 1 (
    echo [����] δ�ҵ� pip
    pause
    exit /b 1
) else (
    echo [�ɹ�] pip ����
)

docker --version >nul 2>&1
if errorlevel 1 (
    echo [����] δ�ҵ� Docker��Docker������Ҫ��
    set DOCKER_AVAILABLE=no
) else (
    echo [�ɹ�] Docker ����
    set DOCKER_AVAILABLE=yes
)

echo.
echo ���������ɣ�
pause

:choose_deployment
cls
echo ========================================
echo  ѡ����ģʽ
echo ========================================
echo.
echo 1) Docker ����
echo    - �������룬�����ͻ
echo    - һ�����������ڹ���
echo    - ��Ҫ Docker Desktop
if "%DOCKER_AVAILABLE%"=="no" (
    echo    [������] Docker δ��װ
)
echo.
echo 2) ���ؿ�������
echo    - ֱ�����У����ڿ�������
echo    - ʹ�� Flask ����������
echo    - ʹ�����⻷������
echo.
echo 3) VBS ��̨���������������Ƽ���
echo    - ʹ�� VBS �ű���̨����
echo    - �޴������У��ȶ��ɿ�
echo    - �����ÿ����Զ�����
echo    - ������⹤�ߣ�Windows ԭ��֧��
echo.

:deployment_loop
set /p choice="��ѡ����ģʽ (1-3): "
if "%choice%"=="1" (
    if "%DOCKER_AVAILABLE%"=="no" (
        echo [����] Docker �����ã��޷�ѡ�� Docker ����
        echo �밲װ Docker Desktop ��ѡ����������ʽ
        goto deployment_loop
    )
    set DEPLOYMENT_MODE=docker
    echo [�ɹ�] ��ѡ��Docker ����
    goto choose_database
)
if "%choice%"=="2" (
    set DEPLOYMENT_MODE=local
    echo [�ɹ�] ��ѡ�񣺱��ؿ�������
    goto choose_database
)
if "%choice%"=="3" (
    set DEPLOYMENT_MODE=vbs
    echo [�ɹ�] ��ѡ��VBS ��̨����
    goto check_vbs_requirements
)
echo [����] ��Чѡ�������� 1��2 �� 3
goto deployment_loop

:check_vbs_requirements
cls
echo ========================================
echo  VBS ��̨����Ҫ����
echo ========================================
echo.
echo ���ڼ�� VBS �����ű�...

REM ��� VBS �����ű�
set "VBS_SCRIPT_PATH=%cd%\start_rebugtracker.vbs"
if not exist "%VBS_SCRIPT_PATH%" (
    echo [��Ϣ] VBS �����ű�δ�ҵ�
    echo ����·��: %VBS_SCRIPT_PATH%
    echo.
    echo  ��������н��Զ����� VBS �����ű�
    echo �����������ֶ�ָ�����е� VBS �ű�·��
    echo.
    goto vbs_path_config
)
echo [�ɹ�] VBS �����ű����ҵ�: %VBS_SCRIPT_PATH%
echo.
echo ���ڼ�� VBS �ű��е�·������...
goto check_vbs_path

:vbs_path_config
echo.
echo  VBS �ű�·������
echo ========================================
echo.
echo ��ǰ����·��: %VBS_SCRIPT_PATH%
echo.
echo ��ѡ�����:
echo 1) �Զ����� VBS �ű����Ƽ���
echo 2) �ֶ�ָ������ VBS �ű�·��
echo 3) ����ѡ����������ʽ
echo.

:vbs_path_loop
set /p vbs_choice="��ѡ�� (1-3): "
if "%vbs_choice%"=="1" goto auto_create_vbs
if "%vbs_choice%"=="2" goto manual_vbs_path
if "%vbs_choice%"=="3" goto choose_deployment
echo [����] ��Чѡ�������� 1��2 �� 3
goto vbs_path_loop

:check_vbs_path
echo ������� VBS �ű��е�·������...
findstr /i "CurrentDirectory" "%VBS_SCRIPT_PATH%" >nul 2>&1
if errorlevel 1 (
    echo [����] �޷���� VBS �ű��е�·������
    goto vbs_path_config
)

REM ��ȡ��ǰ·��
for /f "tokens=*" %%i in ('findstr /i "CurrentDirectory" "%VBS_SCRIPT_PATH%"') do set "VBS_CURRENT_PATH=%%i"
echo ��ǰ VBS �ű��е�·��: %VBS_CURRENT_PATH%
echo ��Ŀʵ��·��: %PROJECT_ROOT%
echo.

echo ��ѡ�����:
echo 1) ʹ������ VBS �ű������޸�·����
echo 2) ���� VBS �ű��е�·��Ϊ��ǰ��Ŀ·��
echo 3) ���´��� VBS �ű�
echo.

:vbs_update_loop
set /p vbs_update_choice="��ѡ�� (1-3): "
if "%vbs_update_choice%"=="1" goto vbs_requirements_complete
if "%vbs_update_choice%"=="2" goto update_vbs_path
if "%vbs_update_choice%"=="3" goto auto_create_vbs
echo [����] ��Чѡ�������� 1��2 �� 3
goto vbs_update_loop

:update_vbs_path
echo ���ڸ��� VBS �ű��е�·��...
REM ����ԭ�ļ�
copy "%VBS_SCRIPT_PATH%" "%VBS_SCRIPT_PATH%.backup" >nul 2>&1

REM ������ʱ�ļ�
set "TEMP_VBS=%VBS_SCRIPT_PATH%.tmp"
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo.
echo ' ��Ŀ·�� - �Զ�����
echo WshShell.CurrentDirectory = "%PROJECT_ROOT%"
echo.
echo ' ���� Waitress ������
echo WshShell.Run "python deployment_tools\run_waitress.py", 0, False
echo.
echo MsgBox "ReBugTracker started successfully! Visit: http://localhost:5000", vbInformation
) > "%TEMP_VBS%"

REM �滻ԭ�ļ�
move "%TEMP_VBS%" "%VBS_SCRIPT_PATH%" >nul 2>&1
if errorlevel 1 (
    echo [����] ���� VBS �ű�ʧ��
    if exist "%VBS_SCRIPT_PATH%.backup" (
        move "%VBS_SCRIPT_PATH%.backup" "%VBS_SCRIPT_PATH%" >nul 2>&1
        echo [�ָ�] �ѻָ�ԭʼ VBS �ű�
    )
    pause
    exit /b 1
)

echo [�ɹ�] VBS �ű�·���Ѹ���
if exist "%VBS_SCRIPT_PATH%.backup" (
    echo [����] ԭʼ�ļ��ѱ���Ϊ: %VBS_SCRIPT_PATH%.backup
)
goto vbs_requirements_complete

:auto_create_vbs
echo [ѡ��] ���ڲ���������Զ����� VBS �ű�
set "VBS_SCRIPT_PATH=%cd%\start_rebugtracker.vbs"
echo VBS �ű���������: %VBS_SCRIPT_PATH%
goto vbs_requirements_complete

:manual_vbs_path
echo.
echo ������ start_rebugtracker.vbs ������·��:
echo ʾ��: C:\path\to\your\start_rebugtracker.vbs
echo.
set /p custom_vbs_path="VBS �ű�·��: "

if "%custom_vbs_path%"=="" (
    echo [����] ·������Ϊ��
    goto manual_vbs_path
)

if not exist "%custom_vbs_path%" (
    echo [����] ָ�����ļ�������: %custom_vbs_path%
    echo.
    set /p retry_path="�Ƿ���������·��? (y/n): "
    if /i "%retry_path%"=="y" goto manual_vbs_path
    goto choose_deployment
)

set "VBS_SCRIPT_PATH=%custom_vbs_path%"
echo [�ɹ�] VBS �ű�·��������: %VBS_SCRIPT_PATH%

:vbs_requirements_complete
echo.
echo VBS ��̨����Ҫ������ɣ�
pause
goto choose_database

:choose_database
cls
echo ========================================
echo  ѡ�����ݿ�����
echo ========================================
echo.
echo 1) SQLite���Ƽ����֣�
echo    - �����ã����伴��
echo    - �ʺ�С�Ŷ�ʹ��
echo    - �����ļ����ڱ���
echo.
echo 2) PostgreSQL���Ƽ�������
echo    - �����ܣ�֧�ִ󲢷�
echo    - �ʺϴ��Ŷ�ʹ��
echo    - ��ҵ�����ݿ⹦��
if "%DEPLOYMENT_MODE%"=="docker" (
    echo    - Docker ���Զ����� PostgreSQL
) else if "%DEPLOYMENT_MODE%"=="vbs" (
    echo    - ��Ҫ�ֶ���װ PostgreSQL ����
) else (
    echo    - ��Ҫ�ֶ���װ������ PostgreSQL
)
echo.

:database_loop
set /p choice="��ѡ�����ݿ����� (1-2): "
if "%choice%"=="1" (
    set DATABASE_TYPE=sqlite
    echo [�ɹ�] ��ѡ��SQLite ���ݿ�
    goto confirm_deployment
)
if "%choice%"=="2" (
    set DATABASE_TYPE=postgres
    echo [�ɹ�] ��ѡ��PostgreSQL ���ݿ�
    if "%DEPLOYMENT_MODE%" neq "docker" (
        goto check_postgres_installation
    )
    goto confirm_deployment
)
echo [����] ��Чѡ�������� 1 �� 2
goto database_loop

:check_postgres_installation
cls
echo ========================================
echo  PostgreSQL ��װ���
echo ========================================
echo.
echo ���ڼ�� PostgreSQL ��װ...

REM ��� PostgreSQL ����
sc query postgresql-x64-17 >nul 2>&1
if errorlevel 1 (
    sc query postgresql >nul 2>&1
    if errorlevel 1 (
        echo [ȱʧ] PostgreSQL ����δ��װ
        echo.
        echo �밲װ PostgreSQL ���ݿ�:
        echo 1. ���ʹ���: https://www.postgresql.org/download/windows/
        echo 2. ���� PostgreSQL 17.x Windows ��װ��
        echo 3. ���а�װ���򣬼�ס���õ�����
        echo 4. ȷ�� PostgreSQL ����������
        echo.
        echo ��װ��ʾ:
        echo - �˿�: 5432 (Ĭ��)
        echo - �û���: postgres (Ĭ��)
        echo - ����: ���ס�����õ�����
        echo.
        goto postgres_install_wait
    ) else (
        echo [�ɹ�] PostgreSQL �����Ѱ�װ
    )
) else (
    echo [�ɹ�] PostgreSQL 17 �����Ѱ�װ
)

echo.
echo PostgreSQL �����ɣ�
pause
goto confirm_deployment

:postgres_install_wait
set /p pg_continue="��װ��ɺ� y �������� n ����ѡ�� SQLite (y/n): "
if /i "%pg_continue%"=="n" (
    set DATABASE_TYPE=sqlite
    echo [���л�] ���л��� SQLite ���ݿ�
    goto confirm_deployment
)
if /i "%pg_continue%"=="y" (
    goto check_postgres_installation
)
echo [����] ������ y �� n
goto postgres_install_wait

:confirm_deployment
cls
echo ========================================
echo  ȷ�ϲ�������
echo ========================================
echo.
echo ����ģʽ��%DEPLOYMENT_MODE%
echo ���ݿ����ͣ�%DATABASE_TYPE%
echo ��ĿĿ¼��%cd%
echo.
echo ����ִ�еĲ�����
if "%DEPLOYMENT_MODE%"=="docker" (
    echo 1. ��� Docker Compose �ļ�
    echo 2. ���� Docker ����
    echo 3. ������������
    echo 4. ��ʼ�����ݿ�
) else if "%DEPLOYMENT_MODE%"=="vbs" (
    echo 1. ���� Python ���⻷��
    echo 2. ��װ��Ŀ����
    echo 3. �������ݿ�����
    echo 4. ʹ�� VBS �ű���̨����
) else (
    echo 1. ���� Python ���⻷��
    echo 2. ��װ��Ŀ����
    echo 3. �������ݿ�����
    echo 4. ��ʼ�����ݿ�
    echo 5. ��������������
)
echo.

:confirm_loop
set /p confirm="ȷ�Ͽ�ʼ����(y/N): "
if /i "%confirm%"=="y" goto start_deployment
if /i "%confirm%"=="yes" goto start_deployment
if /i "%confirm%"=="n" goto welcome
if /i "%confirm%"=="no" goto welcome
if "%confirm%"=="" goto welcome
echo [����] ������ y �� n
goto confirm_loop

:start_deployment
cls
echo ========================================
echo  ��ʼ����
echo ========================================
echo.

if "%DEPLOYMENT_MODE%"=="docker" (
    goto docker_deployment
) else if "%DEPLOYMENT_MODE%"=="vbs" (
    goto vbs_deployment
) else (
    goto local_deployment
)

:docker_deployment
echo [Docker] Docker ����ģʽ
echo.

echo [���� 1/4] ��� Docker Compose �ļ�
if not exist "docker-compose.yml" (
    echo [����] δ�ҵ� docker-compose.yml �ļ�
    echo ��ȷ������Ŀ��Ŀ¼���д˽ű�
    pause
    exit /b 1
)
echo [�ɹ�] Docker Compose �ļ�����

echo.
echo [���� 2/4] ���� Docker ����
echo ���ڹ����������Ժ�...
docker-compose build
if errorlevel 1 (
    echo [����] Docker ���񹹽�ʧ��
    pause
    exit /b 1
)
echo [�ɹ�] Docker ���񹹽����

echo.
echo [���� 3/4] ������������
echo ������������...
docker-compose up -d
if errorlevel 1 (
    echo [����] ��������ʧ��
    pause
    exit /b 1
)
echo [�ɹ�] �������������ɹ�

echo.
echo [���� 4/4] �ȴ��������
echo �ȴ����ݿ��ʼ��...
timeout /t 10 /nobreak >nul
echo [�ɹ�] �������

goto deployment_complete

:vbs_deployment
echo [VBS] VBS ��̨����ģʽ
echo.

echo [���� 1/4] �������⻷��
if exist ".venv" (
    echo [����] ���⻷���Ѵ���
) else (
    echo ���ڴ������⻷��...
    python -m venv .venv
    if errorlevel 1 (
        echo [����] ���⻷������ʧ��
        pause
        exit /b 1
    )
    echo [�ɹ�] ���⻷���������
)

echo.
echo [���� 2/4] ��װ����
echo ���ڰ�װ������...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo [����] ������װʧ��
    pause
    exit /b 1
)
echo [�ɹ�] ������װ���

echo.
echo [���� 3/4] �������ݿ�
if "%DATABASE_TYPE%"=="sqlite" (
    echo ���� SQLite ���ݿ�...
    echo DB_TYPE=sqlite > .env
    echo SERVER_PORT=5000 >> .env
    echo [�ɹ�] SQLite �������
) else (
    echo ���� PostgreSQL ���ݿ�...
    echo DB_TYPE=postgres > .env
    echo SERVER_PORT=5000 >> .env
    echo DATABASE_HOST=localhost >> .env
    echo DATABASE_PORT=5432 >> .env
    echo DATABASE_NAME=rebugtracker >> .env
    echo DATABASE_USER=postgres >> .env
    set /p db_password="������ PostgreSQL ����: "
    echo DATABASE_PASSWORD=%db_password% >> .env
    echo [�ɹ�] PostgreSQL �������
)

echo.
echo [���� 4/4] ���������� VBS �ű�
echo ���ڴ��� VBS �����ű�...

REM ���� VBS �����ű�
set "VBS_SCRIPT_PATH=%PROJECT_ROOT%\start_rebugtracker.vbs"
echo ���� VBS �ű�: %VBS_SCRIPT_PATH%

(
echo ' ReBugTracker VBS �����ű�
echo ' �Զ������ڲ������
echo.
echo ' ������Ŀ��Ŀ¼·��
echo Dim projectPath
echo projectPath = "%PROJECT_ROOT%"
echo.
echo ' ���� Python ���⻷��·��
echo Dim pythonPath
echo pythonPath = projectPath ^& "\.venv\Scripts\python.exe"
echo.
echo ' ���� Waitress �����ű�·��
echo Dim waitressScript
echo waitressScript = projectPath ^& "\deployment_tools\run_waitress.py"
echo.
echo ' ���� Shell ����
echo Dim shell
echo Set shell = CreateObject^("WScript.Shell"^)
echo.
echo ' �л�����ĿĿ¼
echo shell.CurrentDirectory = projectPath
echo.
echo ' ������������^(ʹ�� Waitress ����������^)
echo Dim command
echo command = """" ^& pythonPath ^& """ """ ^& waitressScript ^& """"
echo.
echo ' �ں�̨����^(��������^)
echo shell.Run command, 0, False
echo.
echo ' ��ʾ������ʾ^(��ѡ^)
echo MsgBox "ReBugTracker started in background" ^& vbCrLf ^& "Access URL: http://localhost:5000", vbInformation, "ReBugTracker"
) > "%VBS_SCRIPT_PATH%"

if exist "%VBS_SCRIPT_PATH%" (
    echo [�ɹ�] VBS �ű��������
) else (
    echo [����] VBS �ű�����ʧ��
    pause
    exit /b 1
)

echo.
echo ����ʹ�� VBS �ű���̨���� ReBugTracker...
echo Start command: wscript.exe "%VBS_SCRIPT_PATH%"
wscript.exe "%VBS_SCRIPT_PATH%"
if errorlevel 1 (
    echo [����] VBS �ű���������ʧ��
    echo ���� VBS �ű��Ƿ���ȷ����
) else (
    echo [�ɹ�] VBS �ű�������
)

echo.
echo �ȴ���������...
timeout /t 5 /nobreak >nul

echo [��Ϣ] ReBugTracker ���ں�̨����
echo ����ֹͣ�����������ص� Python ����

goto deployment_complete

:local_deployment
echo [����] ���ز���ģʽ
echo.

echo [���� 1/5] �������⻷��
if exist ".venv" (
    echo [����] ���⻷���Ѵ���
) else (
    echo ���ڴ������⻷��...
    python -m venv .venv
    if errorlevel 1 (
        echo [����] ���⻷������ʧ��
        pause
        exit /b 1
    )
    echo [�ɹ�] ���⻷���������
)

echo.
echo [���� 2/5] �������⻷������װ����
echo ���ڰ�װ������...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo [����] ������װʧ��
    pause
    exit /b 1
)
echo [�ɹ�] ������װ���

echo.
echo [���� 3/5] �������ݿ�
if "%DATABASE_TYPE%"=="sqlite" (
    echo ���� SQLite ���ݿ�...
    echo DATABASE_TYPE=sqlite > .env
    echo [�ɹ�] SQLite �������
) else (
    echo ���� PostgreSQL ���ݿ�...
    echo DATABASE_TYPE=postgres > .env
    echo DATABASE_HOST=localhost >> .env
    echo DATABASE_PORT=5432 >> .env
    echo DATABASE_NAME=rebugtracker >> .env
    echo DATABASE_USER=postgres >> .env
    set /p db_password="������ PostgreSQL ����: "
    echo DATABASE_PASSWORD=%db_password% >> .env
    echo [�ɹ�] PostgreSQL �������
)

echo.
echo [���� 4/5] ��ʼ�����ݿ�
echo ���ڳ�ʼ�����ݿ�...
python database_tools\sync_tools\smart_sync_postgres_to_sqlite.py
if errorlevel 1 (
    echo [����] ���ݿ�ͬ������ʧ�ܣ�����������
)
echo [�ɹ�] ���ݿ��ʼ�����

echo.
echo [���� 5/5] ����Ӧ��
echo �������� ReBugTracker...
echo.
echo Ӧ�ý��� http://localhost:5000 ����
echo Ĭ�Ϲ���Ա�˺�: admin
echo Ĭ�Ϲ���Ա����: admin
echo.
echo �� Ctrl+C ֹͣ����
python rebugtracker.py

goto deployment_complete

:deployment_complete
cls
echo ========================================
echo  ������ɣ�
echo ========================================
echo.
echo [�ɹ�] ReBugTracker ����ɹ���
echo.
echo ������Ϣ��
echo - ���ʵ�ַ��http://localhost:5000
echo - ����Ա�˺ţ�admin
echo - ����Ա���룺admin
echo.
echo �������ã�
echo - ����ģʽ��%DEPLOYMENT_MODE%
echo - ���ݿ����ͣ�%DATABASE_TYPE%
echo.
if "%DEPLOYMENT_MODE%"=="docker" (
    echo Docker �������
    echo - �鿴״̬��docker-compose ps
    echo - �鿴��־��docker-compose logs
    echo - ֹͣ����docker-compose down
    echo - ��������docker-compose restart
) else if "%DEPLOYMENT_MODE%"=="vbs" (
    echo VBS ��̨��������
    echo - VBS �ű���%VBS_SCRIPT_PATH%
    echo - Restart: wscript.exe "%VBS_SCRIPT_PATH%"
    echo - ֹͣ���񣺽��� Python ���̣������������
    echo - �鿴��־��logs\ Ŀ¼
    echo - �����ļ���.env
    echo - ����˿ڣ�5000 ������ .env �ļ����޸� SERVER_PORT��
    echo.
    echo  �����Զ��������ã�
    echo - �� VBS �ű���ӵ������ļ���
    echo - �����ļ���·����%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Startup
) else (
    echo ���ؿ����������
    echo - ��������python rebugtracker.py
    echo - ���⻷����.venv\Scripts\activate.bat
    echo - �����ļ���.env
)
echo.
echo ��лʹ�� ReBugTracker��
echo ���輼��֧�֣���鿴��Ŀ�ĵ���
echo.
pause
exit /b 0

:python_download_choice
cls
echo ========================================
echo  Python ��װ��
echo ========================================
echo.
echo ѡ�����ط�ʽ��
echo 1) PowerShell ���أ��Ƽ���
echo 2) curl ���أ�Windows 10 1803+��
echo 3) bitsadmin ���أ���������Windows�汾��
echo 4) �ֶ����أ���ʾ�������
echo n) ������װ
echo.

set /p download_choice="��ѡ�� (1-4/n): "

if "%download_choice%"=="1" goto download_powershell
if "%download_choice%"=="2" goto download_curl
if "%download_choice%"=="3" goto download_bitsadmin
if "%download_choice%"=="4" goto download_manual
if /i "%download_choice%"=="n" goto skip_python

echo [����] ��Чѡ�������� 1��2��3��4 �� n
pause
goto python_download_choice

:download_powershell
echo.
echo [PowerShell] ����ʹ�� PowerShell ���� Python 3.12.7...
echo ���ص�ַ: https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo ����λ��: %cd%\python-installer.exe
echo.
echo �������أ����Ժ�...
powershell -Command "& {try {$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile 'python-installer.exe' -UseBasicParsing; Write-Host '[�ɹ�] Python ��װ���������'} catch {Write-Host '[����] ����ʧ��:' $_.Exception.Message; exit 1}}"
if errorlevel 1 (
    echo [����] PowerShell ����ʧ�ܣ��볢��������ʽ
    pause
    goto python_download_choice
)
goto install_python

:download_curl
echo.
echo [curl] ����ʹ�� curl ���� Python 3.12.7...
curl --version >nul 2>&1
if errorlevel 1 (
    echo [����] curl �����ã���ѡ���������ط�ʽ
    pause
    goto python_download_choice
)
echo ���ص�ַ: https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo ����λ��: %cd%\python-installer.exe
echo.
echo �������أ����Ժ�...
curl -L -o python-installer.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
if errorlevel 1 (
    echo [����] curl ����ʧ�ܣ��볢��������ʽ
    pause
    goto python_download_choice
)
echo [�ɹ�] Python ��װ���������
goto install_python

:download_bitsadmin
echo.
echo [bitsadmin] ����ʹ�� bitsadmin ���� Python 3.12.7...
echo ���ص�ַ: https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo ����λ��: %cd%\python-installer.exe
echo.
echo �������أ����Ժ�...
bitsadmin /transfer "PythonDownload" https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe "%cd%\python-installer.exe"
if errorlevel 1 (
    echo [����] bitsadmin ����ʧ�ܣ��볢��������ʽ
    pause
    goto python_download_choice
)
echo [�ɹ�] Python ��װ���������
goto install_python

:download_manual
echo.
echo [�ֶ�����] ���ֶ����� Python ��װ����
echo.
echo ����1 - ���ʹ������أ�
echo 1. ����: https://www.python.org/downloads/
echo 2. ���� Python 3.12.7 Windows x86-64 executable installer
echo 3. �����ص��ļ�������Ϊ python-installer.exe �����ڵ�ǰĿ¼
echo.
echo ����2 - ʹ�����������أ�������������µ�������ʾ�����ڣ���
echo.
echo PowerShell:
echo powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile 'python-installer.exe'"
echo.
echo curl:
echo curl -o python-installer.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
echo.
echo bitsadmin:
echo bitsadmin /transfer "PythonDownload" https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe "%cd%\python-installer.exe"
echo.

:manual_wait
set /p manual_continue="������ɺ� y ������װ���� n ����ѡ�� (y/n): "
if /i "%manual_continue%"=="y" (
    if exist "python-installer.exe" (
        goto install_python
    ) else (
        echo [����] δ�ҵ� python-installer.exe �ļ�����ȷ���ļ��ڵ�ǰĿ¼
        goto manual_wait
    )
)
if /i "%manual_continue%"=="n" goto python_download_choice
echo [����] ������ y �� n
goto manual_wait

:skip_python
echo [����] ������ Python ��װ
echo ���ֶ���װ Python ���������д˽ű�
pause
exit /b 1

:install_python
echo.
echo ========================================
echo  ��װ Python
echo ========================================
echo.
echo [���] ��֤�����ļ�...
if not exist "python-installer.exe" (
    echo [����] δ�ҵ� python-installer.exe �ļ�
    pause
    goto python_download_choice
)

echo [���] �ļ���С��֤...
for %%A in (python-installer.exe) do set file_size=%%~zA
if %file_size% LSS 10000000 (
    echo [����] ���ص��ļ����ܲ����� ^(��С: %file_size% �ֽ�^)
    echo ������Python��װ��Ӧ�ô���10MB
    echo ����������
    del python-installer.exe >nul 2>&1
    pause
    goto python_download_choice
)
echo [�ɹ�] �ļ���С���� ^(%file_size% �ֽ�^)

echo.
echo [��װ] ׼����װ Python...
echo.
echo ��Ҫ��ʾ��
echo 1. Please check "Add Python to PATH" option during installation
echo 2. ����ѡ�� "Install for all users" ѡ��
echo 3. ��װ��ɺ�Ҫ�����رհ�װ����
echo.

:install_confirm
set /p install_confirm="�� y ��ʼ��װ���� n ȡ�� (y/n): "
if /i "%install_confirm%"=="y" goto start_install
if /i "%install_confirm%"=="n" (
    echo [ȡ��] ��ȡ����װ
    pause
    exit /b 1
)
echo [����] ������ y �� n
goto install_confirm

:start_install
echo [��װ] �������� Python ��װ����...
echo ���ڰ�װ��������ɰ�װ����
start /wait python-installer.exe

echo.
echo [��֤] ��װ��ɣ�������֤...
timeout /t 3 /nobreak >nul

REM ����ˢ�»�������
set PATH=%PATH%

python --version >nul 2>&1
if errorlevel 1 (
    echo [����] Python ����δ��ȷ��װ��δ��ӵ� PATH
    echo.
    echo ���ܵ�ԭ��
    echo 1. "Add Python to PATH" was not checked during installation
    echo 2. ��Ҫ����������ʾ��
    echo 3. �����Ǽ������⣬�ɹرմ˽ű�����cmd������python -v�鿴
    echo 4. ��Ҫ���µ�¼ Windows
  

    :retry_check
    set /p retry_check="�� y ���¼�飬�� r ���°�װ���� n �˳� (y/r/n): "
    if /i "%retry_check%"=="y" (
        python --version >nul 2>&1
        if errorlevel 1 (
            echo [����] Python ��Ȼ������
            goto retry_check
        ) else (
            goto python_success
        )
    )
    if /i "%retry_check%"=="r" goto install_python
    if /i "%retry_check%"=="n" (
        pause
        exit /b 1
    )
    echo [����] ������ y��r �� n
    goto retry_check
)

:python_success
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [�ɹ�] Python ��װ�ɹ����汾: %PYTHON_VERSION%

echo.
echo [����] ��װ�ļ�����...

:cleanup_choice
set /p cleanup="�Ƿ�ɾ����װ�ļ� python-installer.exe��(y/N): "
if /i "%cleanup%"=="y" (
    del python-installer.exe >nul 2>&1
    echo [����] ��װ�ļ���ɾ��
) else if /i "%cleanup%"=="n" (
    echo [����] ��װ�ļ��ѱ���
) else if "%cleanup%"=="" (
    echo [����] ��װ�ļ��ѱ���
) else (
    echo [����] ������ y �� n
    goto cleanup_choice
)

echo.
echo [���] Python ��װ����ɣ�
echo ���ڷ��ػ������...
pause
goto check_environment
