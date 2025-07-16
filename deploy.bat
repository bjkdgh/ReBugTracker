@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

:welcome
cls
echo ========================================
echo  ReBugTracker Windows һ������ű�
echo ========================================
echo.
echo ���ű������������ ReBugTracker �� Windows ϵͳ����������
echo ֧�����²���ʽ��
echo - Docker ��������
echo - ���ؿ�����������
echo - Windows ���������������Ƽ���
echo.
echo �����Ĺ��ߣ�
echo - NSSM Windows ���������
echo - PostgreSQL ��Я�����ݿ�
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
    echo [����] δ�ҵ� Python�����Ȱ�װ Python 3.8+
    echo ���ص�ַ: https://www.python.org/downloads/
    pause
    exit /b 1
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
echo    - ֧�ֱ�Я�� PostgreSQL
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
    goto choose_database
)
echo [����] ��Чѡ�������� 1��2 �� 3
goto deployment_loop

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
    echo    - ��ѡ���Я�� PostgreSQL���ⰲװ��
    echo    - ��ʹ���Ѱ�װ�� PostgreSQL ����
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
    goto confirm_deployment
)
echo [����] ��Чѡ�������� 1 �� 2
goto database_loop

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
    echo 1. ��鲿�𹤾ߣ�NSSM��Waitress��
    echo 2. ���� Python ���⻷��
    echo 3. ��װ��Ŀ������ Waitress
    echo 4. �������ݿ�����
    echo 5. ��ѹ������ NSSM
    echo 6. ��װ������ Windows ����
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

echo [���� 1/6] ��鲿�𹤾�
if not exist "deployment_tools\nssm-2.24.zip" (
    echo [����] δ�ҵ� NSSM ���߰�
    echo ��ȷ�� deployment_tools\nssm-2.24.zip �ļ�����
    pause
    exit /b 1
)
echo [�ɹ�] NSSM ���߰�����

if not exist "deployment_tools\run_waitress.py" (
    echo [����] δ�ҵ� Waitress ���нű�
    pause
    exit /b 1
)
echo [�ɹ�] Waitress ���нű�����

echo.
echo [���� 2/6] �������⻷��
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
echo [���� 3/6] ��װ����
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
echo [���� 4/6] �������ݿ�
if "%DATABASE_TYPE%"=="sqlite" (
    echo ���� SQLite ���ݿ�...
    echo DATABASE_TYPE=sqlite > .env
    echo APP_PORT=8000 >> .env
    echo [�ɹ�] SQLite �������
) else (
    echo ���� PostgreSQL ���ݿ�...
    echo.
    echo ����Я�� PostgreSQL...
    if exist "deployment_tools\postgresql-17.5-3-windows-x64.exe" (
        echo [����] PostgreSQL ��Я�氲װ��
        set /p install_pg="�Ƿ�װ��Я�� PostgreSQL��(y/N): "
        if /i "!install_pg!"=="y" (
            echo ���ڰ�װ��Я�� PostgreSQL...
            echo �밴�հ�װ����� PostgreSQL ��װ
            start /wait deployment_tools\postgresql-17.5-3-windows-x64.exe
            echo [�ɹ�] PostgreSQL ��װ���
        )
    )
    echo DATABASE_TYPE=postgres > .env
    echo APP_PORT=8000 >> .env
    echo DATABASE_HOST=localhost >> .env
    echo DATABASE_PORT=5432 >> .env
    echo [�ɹ�] PostgreSQL �������
)

echo.
echo [���� 5/6] ��ѹ������ NSSM
if not exist "deployment_tools\nssm.exe" (
    echo ���ڽ�ѹ NSSM...
    powershell -Command "Expand-Archive -Path 'deployment_tools\nssm-2.24.zip' -DestinationPath 'deployment_tools\temp' -Force"
    copy "deployment_tools\temp\nssm-2.24\win64\nssm.exe" "deployment_tools\nssm.exe"
    rmdir /s /q "deployment_tools\temp"
    echo [�ɹ�] NSSM ��ѹ���
) else (
    echo [����] NSSM �Ѵ���
)

echo.
echo [���� 6/6] ��װ Windows ����
echo ���ڰ�װ ReBugTracker Windows ����...
call deployment_tools\install_windows_service.bat
if errorlevel 1 (
    echo [����] Windows ����װʧ��
    pause
    exit /b 1
)
echo [�ɹ�] Windows ����װ���

echo.
echo �������� ReBugTracker ����...
call deployment_tools\start_service.bat
if errorlevel 1 (
    echo [����] ������������ʧ�ܣ�������־
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
    echo ��ȷ�� PostgreSQL ����������
    echo DATABASE_TYPE=postgres > .env
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
) else if "%DEPLOYMENT_MODE%"=="service" (
    echo Windows �������
    echo - �������deployment_tools\manage_windows_service.bat
    echo - ��������deployment_tools\start_service.bat
    echo - ֹͣ����net stop ReBugTracker
    echo - ��������net stop ReBugTracker ^&^& net start ReBugTracker
    echo - ж�ط���deployment_tools\uninstall_windows_service.bat
    echo - �鿴��־��logs\ Ŀ¼
    echo - ����˿ڣ�8000 ������ .env �ļ����޸� APP_PORT��
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
