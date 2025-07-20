#!/bin/bash
# ReBugTracker Docker 启动脚本

cd "$(dirname "$0")"

echo "🚀 启动 ReBugTracker (Docker模式)..."
echo "数据库类型: sqlite"
echo "访问地址: http://localhost:10001"
echo "管理员账号: admin"
echo "管理员密码: admin"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

docker-compose -f docker-compose.sqlite.yml up -d
echo "服务已在后台启动"
echo ""
echo "查看日志: sudo docker-compose -f docker-compose.sqlite.yml logs -f"
echo "停止服务: sudo docker-compose -f docker-compose.sqlite.yml down"
