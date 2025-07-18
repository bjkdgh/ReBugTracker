#!/bin/bash
# ReBugTracker 启动脚本
# 适用于 macOS 和 Linux 系统

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 切换到应用目录
cd "$SCRIPT_DIR"

# 检查是否已经在运行
PID=$(pgrep -f "ReBugTracker")
if [ ! -z "$PID" ]; then
    echo "ReBugTracker 已经在运行 (PID: $PID)"
    
    # 询问是否打开浏览器
    read -p "是否打开浏览器? (y/n): " OPEN_BROWSER
    if [[ "$OPEN_BROWSER" =~ ^[Yy]$ ]]; then
        # 尝试打开浏览器
        if [ "$(uname)" == "Darwin" ]; then
            # macOS
            open http://localhost:5000
        else
            # Linux
            if command -v xdg-open > /dev/null; then
                xdg-open http://localhost:5000
            elif command -v gnome-open > /dev/null; then
                gnome-open http://localhost:5000
            elif command -v firefox > /dev/null; then
                firefox http://localhost:5000 &
            elif command -v chromium-browser > /dev/null; then
                chromium-browser http://localhost:5000 &
            else
                echo "无法自动打开浏览器，请手动访问: http://localhost:5000"
            fi
        fi
    fi
    
    exit 0
fi

# 检查可执行文件
if [ ! -f "$SCRIPT_DIR/ReBugTracker" ]; then
    echo "错误: 未找到 ReBugTracker 可执行文件"
    echo "请确保在正确的目录中运行此脚本"
    exit 1
fi

# 检查权限
if [ ! -x "$SCRIPT_DIR/ReBugTracker" ]; then
    echo "设置可执行权限..."
    chmod +x "$SCRIPT_DIR/ReBugTracker"
fi

# 创建必要的目录
mkdir -p "$SCRIPT_DIR/uploads"
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/data_exports"

# 启动应用
echo "正在启动 ReBugTracker..."
"$SCRIPT_DIR/ReBugTracker" &

# 等待应用启动
echo "等待服务启动..."
sleep 3

# 检查是否成功启动
PID=$(pgrep -f "ReBugTracker")
if [ -z "$PID" ]; then
    echo "启动失败，请检查日志文件"
    exit 1
fi

echo "ReBugTracker 已成功启动 (PID: $PID)"
echo "访问地址: http://localhost:5000"
echo "默认管理员: admin / admin"

# 尝试打开浏览器
if [ "$(uname)" == "Darwin" ]; then
    # macOS
    open http://localhost:5000
else
    # Linux
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:5000
    elif command -v gnome-open > /dev/null; then
        gnome-open http://localhost:5000
    elif command -v firefox > /dev/null; then
        firefox http://localhost:5000 &
    elif command -v chromium-browser > /dev/null; then
        chromium-browser http://localhost:5000 &
    else
        echo "无法自动打开浏览器，请手动访问: http://localhost:5000"
    fi
fi

# 显示停止命令
echo ""
echo "要停止服务，请运行:"
echo "kill $PID"
