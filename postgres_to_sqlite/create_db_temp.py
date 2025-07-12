# postgres_to_sqlite/create_db_temp.py: SQLite数据库表结构创建模块
# 主要功能：创建SQLite数据库表结构，兼容PostgreSQL迁移数据

import sqlite3
import os
from config import DB_CONFIG, DB_TYPE, DATABASE_CONFIG
from db_factory import get_db_connection

def create_sqlite_tables():
    """创建SQLite数据库表结构
    
    功能：
    - 创建users表（如果不存在）
    - 创建bugs表（如果不存在）
    - 清空现有数据（可选）
    """
    # 确保目录存在
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'bugtracker.db')
    db_dir = os.path.dirname(db_path)
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, mode=0o777, exist_ok=True)
        os.chmod(db_dir, 0o777)
    
    # 创建数据库连接
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 创建users表
    c.execute('''
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
    c.execute('''
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
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    print("数据库表结构创建完成")

if __name__ == '__main__':
    create_sqlite_tables()
