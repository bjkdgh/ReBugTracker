# sqlite_to_postgres/test_db_connection.py: PostgreSQL数据库连接测试模块
# 用于验证PostgreSQL数据库配置是否正确，能否成功建立数据库连接

from db_factory import get_db_connection

try:
    # 获取数据库连接
    conn = get_db_connection()
    
    # 如果能成功获取连接并执行简单操作，说明连接成功
    print("数据库连接成功!")
    
    # 关闭连接
    conn.close()
except Exception as e:
    # 捕获并打印连接异常信息
    print(f"数据库连接失败: {e}")
