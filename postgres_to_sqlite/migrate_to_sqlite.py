# postgres_to_sqlite/migrate_to_sqlite.py: PostgreSQL到SQLite数据迁移脚本
# 主要功能：将PostgreSQL数据库中的users表和bugs表迁移到SQLite数据库

import sys
import os

# 将当前工作目录和父目录添加到Python的模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import psycopg2
# PostgreSQL连接配置
PG_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb', 
    'host': '192.168.1.5'
}

def migrate_data():
    """迁移数据从PostgreSQL到SQLite
    
    功能：
    - 创建SQLite数据库文件
    - 迁移users表数据
    - 迁移bugs表数据
    - 保留所有关联数据和时间戳信息
    """
    # 创建SQLite数据库连接（项目根目录下的rebugtracker.db）
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
    sqlite_conn = sqlite3.connect(db_path)
    
    # 创建users表
    sqlite_conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            chinese_name TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            role_en TEXT,
            team TEXT,
            team_en TEXT
        )
    ''')
    
    # 创建bugs表
    sqlite_conn.execute('''
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    ''')
    
    # 清空目标表数据
    sqlite_conn.execute("DELETE FROM users")
    sqlite_conn.execute("DELETE FROM bugs")
    sqlite_conn.commit()
    
    # 直接创建PostgreSQL连接
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor()
    
    # 迁移users表数据
    pg_cursor.execute("SELECT * FROM users")
    for row in pg_cursor.fetchall():
        # 插入用户数据
        sqlite_conn.execute(
            '''INSERT INTO users 
            (username, password, chinese_name, role, role_en, team, team_en) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (row[1], row[2], row[3], row[4], row[5], row[6], row[7])  # 使用数字索引
        )
    
    # 迁移bugs表数据
    pg_cursor.execute("SELECT * FROM bugs")
    for row in pg_cursor.fetchall():
        # 插入问题数据
        sqlite_conn.execute(
            '''INSERT INTO bugs 
            (title, description, status, assigned_to, created_by, project, 
             created_at, resolved_at, resolution, image_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])  # 使用数字索引
        )
    
    # 提交事务并关闭连接
    sqlite_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    
    print("数据迁移完成")

if __name__ == '__main__':
    import os
    # 确保db_path目录存在
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
    db_dir = os.path.dirname(db_path)
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, mode=0o777, exist_ok=True)
        # 设置合适的权限
        os.chmod(db_dir, 0o777)
    
    migrate_data()
