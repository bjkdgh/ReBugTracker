#!/bin/bash
# ReBugTracker 启动脚本

set -e

echo "🚀 ReBugTracker 启动脚本"
echo "=========================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 读取数据库类型
DB_TYPE=$(grep "^DB_TYPE=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")

echo "📊 数据库类型: ${DB_TYPE:-postgres}"

# 根据数据库类型选择compose文件
if [ "$DB_TYPE" = "sqlite" ]; then
    COMPOSE_FILE="docker-compose.sqlite.yml"
    echo "🗄️ 使用 SQLite 模式"
else
    COMPOSE_FILE="docker-compose.yml"
    echo "🐘 使用 PostgreSQL 模式"
fi

# 构建并启动服务
echo "🔨 构建 Docker 镜像..."
docker-compose -f $COMPOSE_FILE build

echo "🚀 启动服务..."
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f $COMPOSE_FILE ps

# 显示访问信息
echo ""
echo "✅ ReBugTracker 启动完成！"
echo "🌐 访问地址: http://localhost:5000"
echo "👤 默认管理员账号: admin / admin"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
echo "  停止服务: docker-compose -f $COMPOSE_FILE down"
echo "  重启服务: docker-compose -f $COMPOSE_FILE restart"
echo ""
