@echo off
echo Starting ReBugTracker...
echo ================================================

REM 设置工作目录
cd /d %~dp0

REM 检查.env文件
if not exist .env (
    echo 未找到.env文件，正在从模板创建...
    copy .env.template .env
    if errorlevel 1 (
        echo 创建.env文件失败！
        pause
        exit /b 1
    )
    echo .env文件已创建，请根据需要修改配置
)

REM 启动程序
echo 正在启动ReBugTracker...
start ReBugTracker.exe

echo 启动完成！
exit /b 0
