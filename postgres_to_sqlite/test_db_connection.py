# postgres_to_sqlite/test_db_connection.py: SQLite数据库连接测试模块
# 主要功能：测试到SQLite数据库的连接是否正常

import os
import sqlite3
from config import DB_CONFIG, DB_TYPE, DATABASE_CONFIG
from db_factory import get_db_connection

def test_sqlite_connection():
    """测试SQLite数据库连接
    
    功能：
    - 创建SQLite数据库连接
    - 执行简单查询验证连接
    - 捕获并打印连接异常信息
    """
    try:
        # 获取SQLite数据库连接
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'bugtracker.db')
        conn = sqlite3.connect(db_path)
        
        # 测试查询
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        
        print(f"成功连接到SQLite数据库，当前users表中有{user_count}条记录")
        conn.close()
        
    except Exception as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    test_sqlite_connection()
