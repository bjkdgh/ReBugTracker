#!/bin/bash
# ReBugTracker 系统安装脚本
# 适用于 Linux 系统

echo "ReBugTracker 系统安装程序"
echo "=========================="

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    echo "例如: sudo ./install.sh"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="/opt/rebugtracker"
SERVICE_USER="rebugtracker"

echo "安装目录: $INSTALL_DIR"
echo "服务用户: $SERVICE_USER"
echo ""

# 询问确认
read -p "是否继续安装? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "安装已取消"
    exit 0
fi

echo "正在安装 ReBugTracker..."

# 创建服务用户
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "创建服务用户: $SERVICE_USER"
    useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
fi

# 创建安装目录
echo "创建安装目录: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# 复制文件
echo "复制应用文件..."
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

# 设置权限
echo "设置文件权限..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/ReBugTracker"
chmod +x "$INSTALL_DIR/start_rebugtracker.sh"

# 创建系统服务文件
echo "创建系统服务..."
SERVICE_FILE="/etc/systemd/system/rebugtracker.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=ReBugTracker Bug Tracking System
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/ReBugTracker
Restart=always
RestartSec=10

# 环境变量
Environment=FLASK_ENV=production
Environment=SERVER_HOST=0.0.0.0
Environment=SERVER_PORT=5000

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
echo "重新加载 systemd..."
systemctl daemon-reload

# 启用服务
echo "启用 ReBugTracker 服务..."
systemctl enable rebugtracker.service

# 创建桌面快捷方式
echo "创建桌面快捷方式..."
DESKTOP_FILE="/usr/share/applications/rebugtracker.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=ReBugTracker
Comment=Bug Tracking System
Exec=$INSTALL_DIR/start_rebugtracker.sh
Icon=$INSTALL_DIR/static/RBT.ico
Terminal=false
Type=Application
Categories=Development;
StartupNotify=true
EOF

# 创建命令行快捷方式
echo "创建命令行快捷方式..."
SYMLINK="/usr/local/bin/rebugtracker"
ln -sf "$INSTALL_DIR/start_rebugtracker.sh" "$SYMLINK"

# 创建管理脚本
echo "创建管理脚本..."
MANAGE_SCRIPT="/usr/local/bin/rebugtracker-manage"
cat > "$MANAGE_SCRIPT" << 'EOF'
#!/bin/bash
# ReBugTracker 管理脚本

case "$1" in
    start)
        echo "启动 ReBugTracker 服务..."
        systemctl start rebugtracker
        ;;
    stop)
        echo "停止 ReBugTracker 服务..."
        systemctl stop rebugtracker
        ;;
    restart)
        echo "重启 ReBugTracker 服务..."
        systemctl restart rebugtracker
        ;;
    status)
        systemctl status rebugtracker
        ;;
    logs)
        journalctl -u rebugtracker -f
        ;;
    enable)
        echo "启用开机自启动..."
        systemctl enable rebugtracker
        ;;
    disable)
        echo "禁用开机自启动..."
        systemctl disable rebugtracker
        ;;
    uninstall)
        echo "卸载 ReBugTracker..."
        systemctl stop rebugtracker
        systemctl disable rebugtracker
        rm -f /etc/systemd/system/rebugtracker.service
        rm -f /usr/share/applications/rebugtracker.desktop
        rm -f /usr/local/bin/rebugtracker
        rm -f /usr/local/bin/rebugtracker-manage
        systemctl daemon-reload
        echo "是否删除安装目录? (y/N)"
        read -r REMOVE_DIR
        if [[ "$REMOVE_DIR" =~ ^[Yy]$ ]]; then
            rm -rf /opt/rebugtracker
            userdel rebugtracker 2>/dev/null
            echo "已完全卸载 ReBugTracker"
        else
            echo "保留了安装目录: /opt/rebugtracker"
        fi
        ;;
    *)
        echo "ReBugTracker 管理工具"
        echo "用法: $0 {start|stop|restart|status|logs|enable|disable|uninstall}"
        echo ""
        echo "命令说明:"
        echo "  start     - 启动服务"
        echo "  stop      - 停止服务"
        echo "  restart   - 重启服务"
        echo "  status    - 查看状态"
        echo "  logs      - 查看日志"
        echo "  enable    - 启用开机自启动"
        echo "  disable   - 禁用开机自启动"
        echo "  uninstall - 卸载系统"
        exit 1
        ;;
esac
EOF

chmod +x "$MANAGE_SCRIPT"

echo ""
echo "安装完成！"
echo "============"
echo ""
echo "启动方法："
echo "1. 系统服务: systemctl start rebugtracker"
echo "2. 管理工具: rebugtracker-manage start"
echo "3. 命令行: rebugtracker"
echo "4. 桌面快捷方式: 在应用菜单中找到 ReBugTracker"
echo ""
echo "管理命令："
echo "- 查看状态: rebugtracker-manage status"
echo "- 查看日志: rebugtracker-manage logs"
echo "- 重启服务: rebugtracker-manage restart"
echo "- 卸载系统: rebugtracker-manage uninstall"
echo ""
echo "访问地址: http://localhost:5000"
echo "默认管理员: admin / admin"
echo ""

# 询问是否立即启动
read -p "是否立即启动 ReBugTracker 服务? (Y/n): " START_NOW
if [[ ! "$START_NOW" =~ ^[Nn]$ ]]; then
    echo "启动服务..."
    systemctl start rebugtracker
    
    # 等待启动
    sleep 3
    
    # 检查状态
    if systemctl is-active --quiet rebugtracker; then
        echo "✅ ReBugTracker 服务启动成功"
        echo "🌐 访问地址: http://localhost:5000"
    else
        echo "❌ 服务启动失败，请检查日志:"
        echo "   journalctl -u rebugtracker"
    fi
fi
