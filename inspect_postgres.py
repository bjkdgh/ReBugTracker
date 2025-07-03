import psycopg2
from psycopg2.extras import DictCursor

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb',
    'host': '192.168.1.5'
}

def inspect_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=DictCursor)
        
        # 查询所有表名
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row['table_name'] for row in cur.fetchall()]
        
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
        print(f"数据库查询错误: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    inspect_database()
