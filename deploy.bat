@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

REM �̶�����Ŀ¼Ϊ�ű�����Ŀ¼���������ԱȨ����·������
cd /d "%~dp0"
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
echo - Windows ���������������Ƽ���
echo.
echo �����Ĺ��ߣ�
echo - NSSM Windows �������������Ҫ���أ�
echo - Waitress ������ WSGI ������
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
echo 3) Windows ���������������Ƽ���
echo    - ʹ�� NSSM ���� Windows ����
echo    - ʹ�� Waitress ������������
echo    - �����Զ��������ȶ��ɿ�
echo    - ��Ҫ�ֶ����� NSSM ����
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
    set DEPLOYMENT_MODE=service
    echo [�ɹ�] ��ѡ��Windows ������
    goto check_service_requirements
)
echo [����] ��Чѡ�������� 1��2 �� 3
goto deployment_loop

:check_service_requirements
cls
echo ========================================
echo  Windows ������Ҫ����
echo ========================================
echo.
echo ���ڼ�� Windows ���������蹤��...

REM ��� NSSM - ʹ�þ���·��
set "NSSM_PATH=%cd%\deployment_tools\nssm.exe"
if not exist "%NSSM_PATH%" (
    echo [ȱʧ] NSSM ����δ�ҵ�
    echo ����·��: %NSSM_PATH%
    echo.
    echo ������ NSSM ^(Non-Sucking Service Manager^):
    echo ������ַ: https://nssm.cc/download
    echo.
    echo ������ɺ� nssm.exe ���õ� deployment_tools\ Ŀ¼
    echo.
    goto nssm_download_wait
)
echo [�ɹ�] NSSM �����Ѿ���: %NSSM_PATH%
goto check_waitress_script

:nssm_download_wait
set /p nssm_continue="������ɺ� y �������� n ����ѡ����������ʽ (y/n): "
if /i "%nssm_continue%"=="n" goto choose_deployment
if /i "%nssm_continue%"=="y" (
    if not exist "%NSSM_PATH%" (
        echo [����] ��δ�ҵ� nssm.exe����ȷ���ļ�����ȷ����
        echo ����·��: %NSSM_PATH%
        pause
        goto nssm_download_wait
    )
    echo [�ɹ�] NSSM �����Ѿ���
    goto check_waitress_script
)
echo [����] ������ y �� n
goto nssm_download_wait

:check_waitress_script
if not exist "deployment_tools\run_waitress.py" (
    echo [����] δ�ҵ� Waitress ���нű�
    echo ��ȷ�� deployment_tools\run_waitress.py �ļ�����
    pause
    exit /b 1
)
echo [�ɹ�] Waitress ���нű�����

echo.
echo Windows ������Ҫ������ɣ�
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
) else if "%DEPLOYMENT_MODE%"=="service" (
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
) else if "%DEPLOYMENT_MODE%"=="service" (
    echo 1. ���� Python ���⻷��
    echo 2. ��װ��Ŀ������ Waitress
    echo 3. �������ݿ�����
    echo 4. ��װ������ Windows ����
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
) else if "%DEPLOYMENT_MODE%"=="service" (
    goto service_deployment
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

:service_deployment
echo [����] Windows ������ģʽ
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
pip install waitress
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
    echo DATABASE_TYPE=sqlite > .env
    echo APP_PORT=5000 >> .env
    echo [�ɹ�] SQLite �������
) else (
    echo ���� PostgreSQL ���ݿ�...
    echo DATABASE_TYPE=postgres > .env
    echo APP_PORT=5000 >> .env
    echo DATABASE_HOST=localhost >> .env
    echo DATABASE_PORT=5432 >> .env
    echo DATABASE_NAME=rebugtracker >> .env
    echo DATABASE_USER=postgres >> .env
    set /p db_password="������ PostgreSQL ����: "
    echo DATABASE_PASSWORD=%db_password% >> .env
    echo [�ɹ�] PostgreSQL �������
)

echo.
echo [���� 4/4] ��װ Windows ����
echo ���ڰ�װ ReBugTracker Windows ����...
set "INSTALL_SCRIPT=%PROJECT_ROOT%\deployment_tools\install_windows_service.bat"
echo ���ð�װ�ű�: %INSTALL_SCRIPT%
call "%INSTALL_SCRIPT%"
if errorlevel 1 (
    echo [����] Windows ����װʧ��
    echo ��װ�ű�·��: %INSTALL_SCRIPT%
    pause
    exit /b 1
)
echo [�ɹ�] Windows ����װ���

echo.
echo �������� ReBugTracker ����...
set "START_SCRIPT=%PROJECT_ROOT%\deployment_tools\start_service.bat"
echo ���������ű�: %START_SCRIPT%
call "%START_SCRIPT%"
if errorlevel 1 (
    echo [����] ������������ʧ�ܣ�������־
    echo �����ű�·��: %START_SCRIPT%
) else (
    echo [�ɹ�] ReBugTracker ���������ɹ�
)

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
if "%DEPLOYMENT_MODE%"=="service" (
    echo - ���ʵ�ַ��http://localhost:5000
) else (
    echo - ���ʵ�ַ��http://localhost:5000
)
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
) else if "%DEPLOYMENT_MODE%"=="service" (
    echo Windows �������
    echo - �������deployment_tools\manage_windows_service.bat
    echo - ��������deployment_tools\start_service.bat
    echo - ֹͣ����net stop ReBugTracker
    echo - ��������net stop ReBugTracker ^&^& net start ReBugTracker
    echo - ж�ط���deployment_tools\uninstall_windows_service.bat
    echo - �鿴��־��logs\ Ŀ¼
    echo - ����˿ڣ�5000 ������ .env �ļ����޸� APP_PORT��
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
echo 1. ��װ����������ع�ѡ "Add Python to PATH" ѡ��
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
    echo 1. ��װʱδ��ѡ "Add Python to PATH"
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
