import psycopg2
from config import DB_CONFIG

def check_constraints():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查询users表的约束
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'users'::regclass
        """)
        constraints = cur.fetchall()
        
        print("Users表约束:")
        for name, definition in constraints:
            print(f"{name}: {definition}")
            
        # 查询users表的索引
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'users'
        """)
        indexes = cur.fetchall()
        
        print("\nUsers表索引:")
        for name, definition in indexes:
            print(f"{name}: {definition}")
            
        # 检查重复用户名
        cur.execute("""
            SELECT LOWER(username) as lower_name, COUNT(*) as count
            FROM users
            GROUP BY LOWER(username)
            HAVING COUNT(*) > 1
        """)
        duplicates = cur.fetchall()
        
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
            
        conn.close()
    except Exception as e:
        print(f"查询失败: {e}")

if __name__ == "__main__":
    check_constraints()
