# inspect_postgres.py: PostgreSQL数据库检查模块
# 用于查看PostgreSQL数据库的表结构和示例数据

import psycopg2
from psycopg2.extras import DictCursor

# 默认数据库连接配置（适用于本地开发环境）
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb',
    'host': '192.168.1.5'
}

def inspect_database():
    """检查数据库结构和内容
    
    功能：
    - 列出数据库中所有表
    - 显示每个表的结构（列名、数据类型、是否可为空）
    - 显示每个表的示例数据（最多5条）
    """
    try:
        # 直接创建PostgreSQL连接
        conn = psycopg2.connect(**DB_CONFIG)
        # 使用DictCursor获取字典形式的结果
        cur = conn.cursor(cursor_factory=DictCursor)
        
        # 查询所有表名
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row['table_name'] for row in cur.fetchall()]
        
        # 输出表信息
        print("数据库中的表:")
        print("-" * 40)
        
        for table in tables:
            print(f"\n表名: {table}")
            
            # 查询表结构
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
            """)
            print("\n表结构:")
            for col in cur.fetchall():
                print(f"  {col['column_name']}: {col['data_type']} {'(可为空)' if col['is_nullable'] == 'YES' else '(非空)'}")
            
            # 查询表内容
            cur.execute(f"SELECT * FROM {table} LIMIT 5")
            print("\n示例数据(最多5条):")
            for row in cur.fetchall():
                print("  ", dict(row))
                
        print("\n" + "=" * 40)
        
    except Exception as e:
        # 捕获并打印异常信息
        print(f"数据库查询错误: {e}")
    finally:
        # 确保关闭数据库连接
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    # 当作为脚本运行时执行数据库检查
    inspect_database()
