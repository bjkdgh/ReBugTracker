@echo off
echo Starting ReBugTracker...
echo ================================================

REM ���ù���Ŀ¼
cd /d %~dp0

REM ���.env�ļ�
if not exist .env (
    echo δ�ҵ�.env�ļ������ڴ�ģ�崴��...
    copy .env.template .env
    if errorlevel 1 (
        echo ����.env�ļ�ʧ�ܣ�
        pause
        exit /b 1
    )
    echo .env�ļ��Ѵ������������Ҫ�޸�����
)

REM ��������
echo ��������ReBugTracker...
start ReBugTracker.exe

echo ������ɣ�
exit /b 0
