import sqlite3
import psycopg2
from psycopg2 import sql
import os

# SQLite连接
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'bugtracker.db')
sqlite_conn = sqlite3.connect(db_path)

# PostgreSQL连接配置
PG_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb',
    'host': '192.168.1.5'
}

# 直接创建PostgreSQL连接
pg_conn = psycopg2.connect(**PG_CONFIG)
pg_conn.autocommit = True
pg_cursor = pg_conn.cursor()

# 创建users表
pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    chinese_name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    team TEXT
)
""")

# 创建bugs表
pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS bugs (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT '待处理',
    assigned_to INTEGER,
    created_by INTEGER,
    project TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution TEXT,
    image_path TEXT
)
""")

# 清空表数据
pg_cursor.execute("TRUNCATE TABLE users CASCADE")
pg_cursor.execute("TRUNCATE TABLE bugs CASCADE")

# 迁移users表数据
sqlite_cursor = sqlite_conn.execute("SELECT * FROM users")
for row in sqlite_cursor:
    # 插入数据，跳过ID字段
    pg_cursor.execute(
        "INSERT INTO users (username, chinese_name, password, role, team) VALUES (%s, %s, %s, %s, %s)",
        row[1:]  # 跳过ID字段
    )

# 迁移bugs表数据
sqlite_cursor = sqlite_conn.execute("SELECT * FROM bugs")
for row in sqlite_cursor:
    # 插入数据，跳过ID字段
    pg_cursor.execute(
        """INSERT INTO bugs 
        (title, description, status, assigned_to, created_by, project, 
         created_at, resolved_at, resolution, image_path) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        row[1:]  # 跳过ID字段
    )

# 更新PostgreSQL的序列值，确保自增ID从现有最大值开始
pg_cursor.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
pg_cursor.execute("SELECT setval('bugs_id_seq', (SELECT MAX(id) FROM bugs))")

# 提交事务并关闭连接
pg_conn.commit()
pg_cursor.close()
pg_conn.close()
sqlite_conn.close()

# 输出迁移完成信息
print("数据迁移完成")
