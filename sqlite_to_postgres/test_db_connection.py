import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="$RFV5tgb",
        host="192.168.1.5"
    )
    print("数据库连接成功!")
    conn.close()
except Exception as e:
    print(f"数据库连接失败: {e}")
