# postgres_to_sqlite/check_db_constraints.py: 数据库约束检查与清理模块
# 主要功能：检查SQLite数据库users表的约束问题，并清理重复的用户名

import os
import sqlite3
from config import DB_CONFIG, DB_TYPE, DATABASE_CONFIG
from db_factory import get_db_connection

def check_constraints():
    """主函数执行数据库约束检查和清理操作
    
    功能：
    - 创建SQLite数据库连接
    - 查询users表的约束信息
    - 检查并清理重复的用户名
    """
    # 创建SQLite数据库连接
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'bugtracker.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 查询users表的约束（SQLite不支持直接查询约束，通过PRAGMA table_info查看）
    print("Users表约束:")
    c.execute(f"PRAGMA table_info(users)")
    columns = c.fetchall()
    for col in columns:
        print(f"{col[1]}: {col[2]} {'NOT NULL' if col[3] else ''} {col[4] if col[4] else ''}")

    # SQLite不支持独立索引，无法直接查询索引信息
    print("\nUsers表索引:")
    print("SQLite不支持直接查询索引信息")

    # 检查重复用户名
    c.execute("""
        SELECT username, COUNT(*) as count
        FROM users
        GROUP BY username
        HAVING COUNT(*) > 1
    """)
    duplicates = c.fetchall()

    # 如果发现重复用户名
    if duplicates:
        print("\n发现重复用户名:")
        for name, count in duplicates:
            print(f"{name}: {count}个重复")
        
        # 清理重复用户名(保留ID最小的记录)
        print("\n正在清理重复用户名...")
        c.execute("""
            DELETE FROM users
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM users
                GROUP BY username
            )
        """)
        conn.commit()
        print("重复用户名清理完成")

    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    # 当作为脚本运行时执行约束检查
    check_constraints()
