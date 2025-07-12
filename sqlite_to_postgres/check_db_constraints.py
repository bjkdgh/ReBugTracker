# sqlite_to_postgres/check_db_constraints.py: 数据库约束检查与清理模块
# 主要功能：检查PostgreSQL数据库users表的约束、索引，并清理重复的用户名

import psycopg2
from config import DB_CONFIG

def check_constraints():
    """检查并处理数据库约束
    
    功能：
    - 查询并打印users表的所有约束
    - 查询并打印users表的所有索引
    - 检查并清理重复的用户名
    """
    try:
        # 获取数据库连接
        from db_factory import get_db_connection
        conn = get_db_connection()
        # 创建游标对象
        cur = conn.cursor()
        
        # 查询users表的约束
        # 获取约束名称和定义
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'users'::regclass
        """)
        constraints = cur.fetchall()
        
        # 输出约束信息
        print("Users表约束:")
        for name, definition in constraints:
            print(f"{name}: {definition}")
            
        # 查询users表的索引
        # 获取索引名称和定义
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'users'
        """)
        indexes = cur.fetchall()
        
        # 输出索引信息
        print("\nUsers表索引:")
        for name, definition in indexes:
            print(f"{name}: {definition}")
            
        # 检查重复用户名
        # 使用LOWER函数忽略大小写进行检查
        cur.execute("""
            SELECT LOWER(username) as lower_name, COUNT(*) as count
            FROM users
            GROUP BY LOWER(username)
            HAVING COUNT(*) > 1
        """)
        duplicates = cur.fetchall()
        
        # 如果发现重复用户名
        if duplicates:
            print("\n发现重复用户名:")
            for name, count in duplicates:
                print(f"{name}: {count}个重复")
            
            # 清理重复用户名(保留ID最小的记录)
            print("\n正在清理重复用户名...")
            cur.execute("""
                DELETE FROM users
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM users
                    GROUP BY LOWER(username)
                )
            """)
            conn.commit()
            print("重复用户名清理完成")
            
        # 关闭数据库连接
        conn.close()
    except Exception as e:
        # 捕获并打印异常信息
        print(f"查询失败: {e}")

if __name__ == "__main__":
    # 当作为脚本运行时执行约束检查
    check_constraints()
