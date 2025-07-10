import psycopg2
from config import DB_CONFIG

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("数据库连接成功")
    conn.close()
except Exception as e:
    print(f"数据库连接失败: {e}")
