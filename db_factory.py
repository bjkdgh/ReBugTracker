# db_factory.py: 数据库连接模块，提供统一的数据库连接接口
# 根据配置创建PostgreSQL或SQLite数据库连接，并处理特定于数据库的初始化设置

import psycopg2
import sqlite3
from config import DB_TYPE, DATABASE_CONFIG

def get_db_connection():
    """获取数据库连接实例
    
    Returns:
        connection: 配置好的数据库连接对象
        支持PostgreSQL和SQLite两种数据库类型
        
    Raises:
        ValueError: 当配置的数据库类型不被支持时抛出异常
    """
    if DB_TYPE == 'postgres':
        # 创建PostgreSQL连接
        conn = psycopg2.connect(**DATABASE_CONFIG['postgres'])
        conn.autocommit = False  # 禁用自动提交以保证事务完整性
        return conn
    elif DB_TYPE == 'sqlite':
        # 创建SQLite连接
        conn = sqlite3.connect(DATABASE_CONFIG['sqlite']['database'])
        conn.row_factory = sqlite3.Row  # 启用行工厂以获得字典风格的访问
        # 启用WAL模式提升并发性能
        conn.execute('PRAGMA journal_mode=WAL;')
        # 设置5秒锁等待超时
        conn.execute('PRAGMA busy_timeout = 5000;')  
        return conn
    else:
        # 不支持的数据库类型
        raise ValueError(f"不支持的数据库类型: {DB_TYPE}")
