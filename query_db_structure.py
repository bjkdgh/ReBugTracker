import sqlite3

def get_db_structure():
    conn = sqlite3.connect('bugtracker.db')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("数据库表:")
    for table in tables:
        print(f"- {table[0]}")
    
    # 获取所有表结构
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"\n{table[0]}表结构:")
        for col in columns:
            print(f"{col[1]} ({col[2]})")
    
    # 获取所有表数据
    for table in tables:
        cursor.execute(f"SELECT * FROM {table[0]}")
        data = cursor.fetchall()
        print(f"\n{table[0]}表数据:")
        for row in data:
            print(row)
    
    conn.close()

if __name__ == "__main__":
    get_db_structure()
