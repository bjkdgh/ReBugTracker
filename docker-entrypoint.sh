#!/bin/bash
# Docker 容器启动脚本
# 处理不同数据库模式和应用启动

set -e

echo "🚀 ReBugTracker Docker 容器启动中..."
echo "数据库类型: ${DB_TYPE:-postgres}"

# 等待数据库服务（仅在 PostgreSQL 模式下）
if [ "${DB_TYPE:-postgres}" = "postgres" ]; then
    echo "⏳ 等待 PostgreSQL 数据库启动..."
    
    # 等待数据库连接可用
    python3 -c "
import psycopg2
import os
import time
import sys

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'db'),
            port=os.getenv('DATABASE_PORT', '5432'),
            dbname=os.getenv('DATABASE_NAME', 'rebugtracker'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', 'ReBugTracker2024')
        )
        conn.close()
        print('✅ PostgreSQL 连接成功')
        sys.exit(0)
    except Exception as e:
        attempt += 1
        print(f'⏳ 等待数据库连接... ({attempt}/{max_attempts})')
        time.sleep(2)

print('❌ 数据库连接超时')
sys.exit(1)
"

    # 检查 Python 脚本的退出状态
    if [ $? -ne 0 ]; then
        echo "❌ PostgreSQL 数据库连接失败"
        exit 1
    fi
else
    echo "📄 使用 SQLite 数据库模式"
    
    # 确保 SQLite 数据库目录存在
    mkdir -p /app/data
    
    # 如果 SQLite 数据库不存在，创建它
    if [ ! -f "${SQLITE_DB_PATH:-/app/data/rebugtracker.db}" ]; then
        echo "🗄️ 初始化 SQLite 数据库..."
        python3 -c "
import sqlite3
import os

db_path = os.getenv('SQLITE_DB_PATH', '/app/data/rebugtracker.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# 创建空的数据库文件
conn = sqlite3.connect(db_path)
conn.close()
print(f'✅ SQLite 数据库文件已创建: {db_path}')
"
    fi
fi

# 初始化数据库表（如果需要）
echo "🗄️ 检查数据库表..."
python3 -c "
import sys
import os
sys.path.append('/app')

try:
    # 尝试导入应用并初始化数据库
    import rebugtracker
    if hasattr(rebugtracker, 'init_db'):
        rebugtracker.init_db()
        print('✅ 数据库表初始化完成')
    else:
        print('ℹ️ 跳过数据库初始化（未找到 init_db 函数）')
except Exception as e:
    print(f'⚠️ 数据库初始化警告: {e}')
    # 不退出，让应用自己处理数据库初始化
"

# 检查应用文件
if [ ! -f "/app/rebugtracker.py" ]; then
    echo "❌ 未找到应用文件 rebugtracker.py"
    exit 1
fi

# 确定应用对象名称
echo "🔍 检测应用对象..."
APP_MODULE="rebugtracker"
APP_OBJECT="app"

# 尝试检测正确的应用对象名称
python3 -c "
import sys
sys.path.append('/app')

try:
    import rebugtracker
    
    # 检查可能的应用对象名称
    possible_names = ['app', 'application', 'flask_app']
    
    for name in possible_names:
        if hasattr(rebugtracker, name):
            obj = getattr(rebugtracker, name)
            if hasattr(obj, 'run'):  # Flask 应用对象应该有 run 方法
                print(f'✅ 找到应用对象: {name}')
                with open('/tmp/app_object', 'w') as f:
                    f.write(name)
                sys.exit(0)
    
    print('⚠️ 未找到标准的 Flask 应用对象，使用默认名称: app')
    with open('/tmp/app_object', 'w') as f:
        f.write('app')
        
except Exception as e:
    print(f'⚠️ 应用检测失败: {e}，使用默认名称: app')
    with open('/tmp/app_object', 'w') as f:
        f.write('app')
"

# 读取检测到的应用对象名称
if [ -f "/tmp/app_object" ]; then
    APP_OBJECT=$(cat /tmp/app_object)
fi

echo "🚀 启动应用: ${APP_MODULE}:${APP_OBJECT}"

# 设置 Gunicorn 配置
WORKERS=${GUNICORN_WORKERS:-4}
TIMEOUT=${GUNICORN_TIMEOUT:-120}
BIND_ADDRESS="0.0.0.0:${SERVER_PORT:-5000}"

echo "⚙️ Gunicorn 配置:"
echo "   绑定地址: $BIND_ADDRESS"
echo "   工作进程: $WORKERS"
echo "   超时时间: $TIMEOUT 秒"

# 启动应用
exec gunicorn \
    --bind "$BIND_ADDRESS" \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "${APP_MODULE}:${APP_OBJECT}"
