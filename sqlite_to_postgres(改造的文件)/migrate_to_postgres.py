import sqlite3
import psycopg2
from psycopg2 import sql
from config import Config

# SQLite连接
sqlite_conn = sqlite3.connect('bugtracker.db')

# PostgreSQL连接
pg_conn = psycopg2.connect(
    host="192.168.1.5",
    port=5432,
    dbname="postgres",  # 默认数据库，用户需确认实际数据库名
    user="postgres",
    password="$RFV5tgb"
)
pg_conn.autocommit = True
pg_cursor = pg_conn.cursor()

# 创建users表
pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
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

# 迁移users数据
sqlite_cursor = sqlite_conn.execute("SELECT * FROM users")
for row in sqlite_cursor:
    pg_cursor.execute(
        "INSERT INTO users (username, password, role, team) VALUES (%s, %s, %s, %s)",
        row[1:]  # 跳过ID字段
    )

# 迁移bugs数据
sqlite_cursor = sqlite_conn.execute("SELECT * FROM bugs")
for row in sqlite_cursor:
    pg_cursor.execute(
        """INSERT INTO bugs 
        (title, description, status, assigned_to, created_by, project, 
         created_at, resolved_at, resolution, image_path) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        row[1:]  # 跳过ID字段
    )

# 更新序列
pg_cursor.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
pg_cursor.execute("SELECT setval('bugs_id_seq', (SELECT MAX(id) FROM bugs))")

pg_conn.commit()
pg_cursor.close()
pg_conn.close()
sqlite_conn.close()

print("数据迁移完成")
